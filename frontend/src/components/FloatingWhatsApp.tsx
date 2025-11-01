// D:\inara-travel-capstone\src\components\FloatingChatWidget.tsx
// (Menggantikan file FloatingWhatsApp.tsx Anda)

import { MessageCircle, X, Send } from "lucide-react";
import { Button } from "@/components/ui/button"; // Asumsi dari 'shadcn'
import { useState, useEffect, useRef, FormEvent } from "react";

// Definisikan tipe data di sini agar self-contained
type ChatMessage = {
  sender: "user" | "bot";
  text: string;
};

// Tipe data ini HARUS SESUAI dengan schemas.py Anda
type ChatResponse = {
  user_id: string;
  response_text: string;
  source: string;
  escalated: boolean;
  escalation_reason?: string;
};

// Tipe data request (sesuai schemas.py)
type ChatRequest = {
  user_id: string;
  message: string;
  user_email?: string;
};

const FloatingChatWidget = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const chatEndRef = useRef<null | HTMLDivElement>(null);

  // 1. Logika untuk memunculkan tombol saat scroll
  useEffect(() => {
    const toggleVisibility = () => {
      setIsVisible(window.pageYOffset > 300);
    };
    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  // 2. Logika untuk auto-scroll ke pesan terbaru
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // 3. Logika untuk membuka/menutup window chat
  const toggleChat = () => {
    setIsChatOpen(prev => !prev);
    // Tambahkan pesan sambutan jika chat baru dibuka
    if (!isChatOpen && chatHistory.length === 0) {
      setChatHistory([
        { sender: "bot", text: "Assalamualaikum! Ada yang bisa saya bantu terkait paket haji & umrah?" }
      ]);
    }
  };

  // 4. FUNGSI PENGHUBUNG UTAMA (API CALL)
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = { sender: 'user', text: message };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      // Panggil API backend Anda di port 8008
      const response = await fetch('http://localhost:8008/chat', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user_inara_web_123', // Ganti dengan ID user (jika sudah login)
          message: message,
          user_email: 'customer@example.com' // Ganti dengan email user (jika ada)
        } as ChatRequest)
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      
      const botMessage: ChatMessage = { 
        sender: 'bot', 
        text: data.response_text //
      };
      setChatHistory(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Gagal terhubung ke Chatbot API:", error);
      const errorMessage: ChatMessage = { 
        sender: 'bot', 
        text: 'Maaf, layanan chat sedang mengalami gangguan. Silakan coba lagi nanti.' 
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* CHAT WINDOW */}
      {isChatOpen && (
        <div 
          style={{ boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)' }}
          className={`fixed bottom-28 right-8 z-50 w-80 h-[28rem] bg-white rounded-lg shadow-large border border-gray-200 flex flex-col transition-all duration-300 ${
            isChatOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          {/* Header */}
          <div className="flex justify-between items-center p-4 bg-gray-800 text-white rounded-t-lg">
            <h3 className="font-semibold">Chat Bantuan</h3>
            <Button variant="ghost" size="icon" onClick={toggleChat} className="h-8 w-8 text-white hover:bg-gray-700">
              <X className="w-5 h-5" />
            </Button>
          </div>
          
          {/* Body Pesan */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {chatHistory.map((chat, index) => (
              <div 
                key={index} 
                className={`flex ${chat.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm shadow-md ${
                    chat.sender === 'user' 
                    ? 'bg-purple-700 text-white' // Warna Anda
                    : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {chat.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-500 rounded-lg px-3 py-2 text-sm">
                  Mengetik...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex p-3 border-t">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ketik pesan Anda..."
              className="flex-1 px-3 py-2 text-sm border rounded-l-md focus:outline-none focus:ring-1 focus:ring-purple-700"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              className="rounded-l-none bg-purple-700 hover:bg-purple-800" // Warna Anda
              disabled={isLoading}
              aria-label="Kirim Pesan"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      )}

      {/* TOMBOL FLOATING */}
      <Button
        onClick={toggleChat}
        size="lg"
        className={`fixed bottom-8 right-8 z-50 rounded-full w-16 h-16 shadow-large bg-purple-700 hover:bg-purple-800 text-white transition-all duration-300 ${ // Warna Anda
          isVisible ? "translate-y-0 opacity-100" : "translate-y-20 opacity-0"
        } hover:scale-110 ${isChatOpen ? 'scale-0 opacity-0' : 'animate-pulse'}`}
        aria-label="Buka Chat Bantuan"
      >
        <MessageCircle className="w-8 h-8" />
      </Button>
    </>
  );
};

export default FloatingChatWidget;