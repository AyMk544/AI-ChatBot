"use client";

import { useChat } from "ai/react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import axios from "axios";

export default function ChatForm() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  const [isLoading, setIsLoading] = useState(false);

  // DON'T USE USEEFFECT, CALL IT WHEN FORM IS SUBMITTED
  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const response = await fetch("http://127.0.0.1:8000/api/process-prompt");
  //       const result = await response.json();
  //       // setData(result.message);
  //     } catch (error) {
  //       console.error("Error fetching data:", error);
  //     }
  //   };

  //   fetchData();
  // }, []);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    await handleSubmit(e);
    setIsLoading(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>AI Chatbot</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[60vh] pr-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`mb-4 ${
                  m.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <span
                  className={`inline-block p-2 rounded-lg ${
                    m.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-black"
                  }`}
                >
                  {m.content}
                </span>
              </div>
            ))}
          </ScrollArea>
        </CardContent>
        <CardFooter>
          <form onSubmit={onSubmit} className="flex w-full space-x-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              className="flex-grow"
            />
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Sending..." : "Send"}
            </Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
