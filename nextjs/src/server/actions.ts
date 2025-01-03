"use server";
import axios from "axios";

async function sendPostRequest(prompt: string, threadId: string) {
  const url = "http://127.0.0.1:8000/api/process-prompt";

  const requestBody = {
    prompt: prompt,
    thread_id: threadId,
  };

  try {
    const response = await axios.post(url, requestBody, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    return response.data; // Return the response data
  } catch (error) {
    console.error("Error sending POST request:", error);
    throw error;
  }
}
