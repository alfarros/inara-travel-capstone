// src/types/chat.ts
export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

export interface ChatRequest {
  user_id: string;
  message: string;
  user_email?: string;
}

export interface ChatResponse {
  user_id: string;
  response_text: string;
  source: string;
  escalated: boolean;
  escalation_reason?: string;
}
