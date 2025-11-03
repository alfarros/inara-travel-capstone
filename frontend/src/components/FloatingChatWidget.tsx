// src/components/FloatingChatWidget.tsx
import { MessageCircle, X, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect, FormEvent } from "react";
import { useChat } from "@/hooks/use-chat"; // Import custom hook

// Kita tidak perlu lagi mendefinisikan tipe data di sini

const FloatingChatWidget = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Gunakan custom hook. ID dan email bisa dinamis di masa depan.
  const {
    message,
    setMessage,
    isLoading,
    chatHistory,
    chatEndRef,
    sendMessage,
    addWelcomeMessage,
  } = useChat("user_inara_web_123", "customer@example.com");

  // Logika untuk memunculkan tombol saat scroll
  useEffect(() => {
    const toggleVisibility = () => {
      setIsVisible(window.pageYOffset > 300);
    };
    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  // Logika untuk membuka/menutup window chat
  const toggleChat = () => {
    const newChatState = !isChatOpen;
    setIsChatOpen(newChatState);
    if (newChatState) {
      addWelcomeMessage();
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage(message);
  };

  return (
    <>
      {/* CHAT WINDOW */}
      {isChatOpen && (
        <div
          className="fixed bottom-28 right-8 z-50 w-80 h-[28rem] bg-white rounded-lg shadow-large border border-gray-200 flex flex-col transition-all duration-300"
          role="dialog"
          aria-modal="true"
          aria-labelledby="chat-header"
        >
          {/* Header */}
          <div
            id="chat-header"
            className="flex justify-between items-center p-4 bg-gray-800 text-white rounded-t-lg"
          >
            <h3 className="font-semibold">Chat Bantuan</h3>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleChat}
              className="h-8 w-8 text-white hover:bg-gray-700"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Body Pesan */}
          <div
            className="flex-1 p-4 overflow-y-auto space-y-3"
            aria-live="polite"
            aria-label="Riwayat percakapan"
          >
            {chatHistory.map((chat, index) => (
              <div
                key={index}
                className={`flex ${
                  chat.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm shadow-md ${
                    chat.sender === "user"
                      ? "bg-purple-700 text-white"
                      : "bg-gray-100 text-gray-800"
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
              aria-label="Ketik pesan"
            />
            <Button
              type="submit"
              className="rounded-l-none bg-purple-700 hover:bg-purple-800"
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
        className={`fixed bottom-8 right-8 z-50 rounded-full w-16 h-16 shadow-large bg-purple-700 hover:bg-purple-800 text-white transition-all duration-300 ${
          isVisible ? "translate-y-0 opacity-100" : "translate-y-20 opacity-0"
        } hover:scale-110 ${
          isChatOpen ? "scale-0 opacity-0" : "animate-pulse"
        }`}
        aria-label="Buka Chat Bantuan"
      >
        <MessageCircle className="w-8 h-8" />
      </Button>
    </>
  );
};

export default FloatingChatWidget;
