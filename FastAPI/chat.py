from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

class PromptRequest(BaseModel):
    prompt: str
    thread_id: str

class PromptResponse(BaseModel):
    response: str
    status: str = "success"

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
MODEL_NAME = "meta.llama3-8b-instruct-v1:0"

model = ChatBedrock(model=MODEL_NAME, beta_use_converse_api=True, streaming=True)

trimmer = trim_messages(
    max_tokens=1000,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sarcastic parrot. Your response should be under 70 words.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

async def call_model(state: MessagesState):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(
        {"messages": trimmed_messages}
    )
    response = await model.ainvoke(prompt)
    return {"messages": response}

workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# streaming endpoint
@api.post("/api/stream-prompt")
async def stream_prompt(request: PromptRequest):
    try:
        if not request.thread_id:
            raise HTTPException(status_code=400, detail="thread_id is required")
        
        # Configuration for the graph
        config = {"configurable": {"thread_id": request.thread_id}}
        input_messages = [HumanMessage(request.prompt)]
        
        # Async generator for streaming response
        async def message_stream() -> AsyncGenerator[str, None]:
            async for chunk, metadata in graph.astream(
                {"messages": input_messages},
                config,
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessage):  # Filter AIMessage chunks
                    yield f"data: {chunk.content}\n\n"

        return StreamingResponse(
            message_stream(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# non-streaming endpoint
@api.post("/api/process-prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    try:
        if not request.thread_id:
            raise HTTPException(status_code=400, detail="thread_id is required")
            
        config = {"configurable": {"thread_id": request.thread_id}}
        input_messages = [HumanMessage(request.prompt)]
        output = await graph.ainvoke({"messages": input_messages}, config)
        response = output["messages"][-1]
        
        return PromptResponse(
            response=response.content,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/")
async def health_check():
    return {"status": "healthy"}