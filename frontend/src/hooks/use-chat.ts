// src/hooks/use-chat.ts
import { useState, useCallback, useRef, useEffect } from "react";
import { ChatMessage, ChatRequest } from "@/types/chat";
import { chatEndpoint } from "@/lib/api";

export const useChat = (userId: string, userEmail?: string) => {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const chatEndRef = useRef<null | HTMLDivElement>(null);

  // Fungsi untuk mengirim pesan, dibungkus dengan useCallback
  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      const userMessage: ChatMessage = { sender: "user", text };
      setChatHistory((prev) => [...prev, userMessage]);
      setMessage("");
      setIsLoading(true);

      try {
        const response = await fetch(chatEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId,
            message: text,
            user_email: userEmail,
          } as ChatRequest),
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();
        const botMessage: ChatMessage = {
          sender: "bot",
          text: data.response_text,
        };
        setChatHistory((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error("Gagal terhubung ke Chatbot API:", error);
        const errorMessage: ChatMessage = {
          sender: "bot",
          text: "Maaf, layanan chat sedang mengalami gangguan. Silakan coba lagi nanti atau hubungi kami via WhatsApp.",
        };
        setChatHistory((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, userEmail, isLoading]
  );

  // Fungsi untuk menambah pesan sambutan
  const addWelcomeMessage = useCallback(() => {
    if (chatHistory.length === 0) {
      setChatHistory([
        {
          sender: "bot",
          text: "Assalamualaikum! Ada yang bisa saya bantu terkait paket haji & umrah?",
        },
      ]);
    }
  }, [chatHistory.length]);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  return {
    message,
    setMessage,
    isLoading,
    chatHistory,
    chatEndRef,
    sendMessage,
    addWelcomeMessage,
  };
};
