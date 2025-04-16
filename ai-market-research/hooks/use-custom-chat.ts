"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { getToken } from "@/lib/auth-utils";

export type Message = {
  id: string
  role: "user" | "assistant"
  content: string
}

type UseCustomChatOptions = {
  initialMessages?: Message[]
  onResponse?: (response: any) => void
  onError?: (error: Error) => void
}

export function useCustomChat(options: UseCustomChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>(options.initialMessages || [])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // For handling streaming responses
  const messageIdRef = useRef("")

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLTextAreaElement>) => {
      setInput(e.target.value)
    },
    [],
  )

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault()
      if (!input.trim()) return

      const accessToken = getToken();
      console.log("Access Token:", accessToken);
      if (!accessToken) {
        setError(Error('No JWT Token available!'));
        return;
      }

      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: input,
      }

      // Add user message to the chat
      setMessages((messages) => [...messages, userMessage])
      setInput("")
      setIsLoading(true)
      setError(null)

      // Create a placeholder for the assistant's response
      const assistantMessageId = (Date.now() + 1).toString()
      messageIdRef.current = assistantMessageId

      setMessages((messages) => [...messages, { id: assistantMessageId, role: "assistant", content: "" }])

      try {
        const endpoint = `${process.env.NEXT_PUBLIC_API_BASE_URL}/chat`;
        // Make API request
        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            input: userMessage.content,
          }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()

        setMessages((messages) =>
          messages.map((message) =>
            message.id === assistantMessageId
              ? { ...message, content: data.response || data.message || JSON.stringify(data) }
              : message,
          ),
        )

        if (options.onResponse) {
          options.onResponse(data)
        }
      } catch (err) {
        console.error("Error in chat request:", err)
        setError(err instanceof Error ? err : new Error("An unknown error occurred"))

        // Update the assistant message to show the error
        setMessages((messages) =>
          messages.map((message) =>
            message.id === assistantMessageId
              ? {
                  ...message,
                  content:
                    "Sorry, I couldn't process your request. Please try again or contact support if the problem persists.",
                }
              : message,
          ),
        )

        if (options.onError) {
          options.onError(err instanceof Error ? err : new Error("An unknown error occurred"))
        }
      } finally {
        setIsLoading(false)
      }
    },
    [input, options],
  )

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error,
    setMessages,
  }
}
