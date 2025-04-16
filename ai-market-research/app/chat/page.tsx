"use client";

import type React from "react";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SendIcon, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { useCustomChat } from "@/hooks/use-custom-chat";
import { logout } from "@/lib/auth-utils";

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } =
    useCustomChat();
  const [isTyping, setIsTyping] = useState(false);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    setIsTyping(true);
    handleSubmit(e).finally(() => setIsTyping(false));
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      <header className="sticky top-0 z-10 bg-white border-b shadow-sm">
        <div className="container flex items-center justify-between h-16 px-4 max-w-4xl mx-auto">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-semibold">
              AI Market Research Analyst
            </h1>
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </header>

      <main className="flex-1 overflow-hidden container max-w-4xl mx-auto px-4 py-6">
        <Card className="flex flex-col h-full border shadow-sm">
          <CardHeader className="px-6 py-4 border-b bg-white">
            <CardTitle className="text-lg font-medium">
              Chat with your AI Analyst
            </CardTitle>
          </CardHeader>

          <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-slate-500">
                <Bot className="h-12 w-12 text-slate-400" />
                <div className="max-w-md space-y-2">
                  <h3 className="text-xl font-medium">
                    Welcome to AI Market Research Analyst
                  </h3>
                  <p>
                    Describe your startup idea, and ask a question you want
                    answered about it. I&apos;ll answer your question to the
                    best of my ability!
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-3 max-w-[85%]",
                    message.role === "user" ? "ml-auto flex-row-reverse" : ""
                  )}
                >
                  <div
                    className={cn(
                      "flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0",
                      message.role === "user" ? "bg-primary" : "bg-slate-200"
                    )}
                  >
                    {message.role === "user" ? (
                      <User className="h-4 w-4 text-white" />
                    ) : (
                      <Bot className="h-4 w-4 text-slate-700" />
                    )}
                  </div>
                  <div
                    className={cn(
                      "rounded-lg px-4 py-3 text-sm shadow-sm",
                      message.role === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-none"
                        : "bg-white text-slate-800 rounded-tl-none border border-slate-200"
                    )}
                  >
                    {message.content || "..."}
                  </div>
                </div>
              ))
            )}
            {isTyping && !isLoading && (
              <div className="flex items-start gap-3 max-w-[85%]">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-200 flex-shrink-0">
                  <Bot className="h-4 w-4 text-slate-700" />
                </div>
                <div className="rounded-lg rounded-tl-none px-4 py-3 text-sm bg-white border border-slate-200 shadow-sm">
                  <div className="flex space-x-1">
                    <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce"></div>
                    <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce delay-75"></div>
                    <div className="h-2 w-2 rounded-full bg-slate-300 animate-bounce delay-150"></div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="p-4 border-t bg-white">
            <form onSubmit={onSubmit} className="flex w-full gap-2">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="Describe your startup idea..."
                className="flex-1 border-slate-300"
                disabled={isLoading}
              />
              <Button
                type="submit"
                size="icon"
                disabled={isLoading || !input.trim()}
                className="bg-primary hover:bg-primary/90"
              >
                <SendIcon className="h-4 w-4" />
                <span className="sr-only">Send</span>
              </Button>
            </form>
          </CardFooter>
        </Card>
      </main>
    </div>
  );
}
