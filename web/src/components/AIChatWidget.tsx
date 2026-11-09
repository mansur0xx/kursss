"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, X, Send, Sparkles, User, Minimize2 } from "lucide-react";

interface Message {
  id: number;
  sender: "user" | "ai";
  text: string;
}

export default function AIChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "ai",
      text: "Сәлеметсіз бе! Мен EduPlatform-ның Ollama AI көмекшісімін. Бағдарламалау, тест сұрақтары немесе үй жұмысы бойынша қандай көмек қажет?",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const quickPrompts = [
    "FastAPI негіздері туралы айтып берші",
    "SQLAlchemy 2-де асинхронды сұраныс қалай жазылады?",
    "Next.js App Router қалай жұмыс істейді?",
  ];

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now(),
      sender: "user",
      text: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: textToSend }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          { id: Date.now() + 1, sender: "ai", text: data.reply },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: "ai",
            text: "Керемет сұрақ! Жергілікті Ollama AI серверімен байланыс орнатылуда. FastAPI және Next.js архитектурасы бойынша кез келген бағытта көмектесуге дайынмын.",
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "ai",
          text: `Сіздің сұрағыңыз қабылданды: "${textToSend}". Жергілікті Ollama контейнерін іске қосқан соң толық AI генерациясы бірден жұмыс істейді.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* 1. БҮКТЕЛГЕН БАТЫРМА (FLOATING ACTION BUTTON) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center gap-3 bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:to-purple-700 text-white p-4 rounded-full shadow-2xl transition-all duration-300 hover:scale-105"
        >
          <div className="relative">
            <Bot className="w-6 h-6 animate-pulse" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-white"></span>
          </div>
          <span className="font-semibold text-sm pr-1 hidden sm:inline-block">
            Ollama AI Көмекші
          </span>
        </button>
      )}

      {/* 2. АШЫЛҒАН ЧАТ ТЕРЕЗЕСІ (EXPANDED CHAT MODAL) */}
      {isOpen && (
        <div className="w-[360px] sm:w-[420px] h-[540px] bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Чат тақырыбы */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 text-white flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                  Ollama AI Ментор
                  <span className="w-2 h-2 bg-emerald-400 rounded-full inline-block"></span>
                </h3>
                <span className="text-[11px] text-indigo-100">Жергілікті білім көмекшісі</span>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 hover:bg-white/20 rounded-lg transition text-white/80 hover:text-white"
            >
              <Minimize2 className="w-4 h-4" />
            </button>
          </div>

          {/* Хабарламалар аймағы */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/50 dark:bg-slate-950/50">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-2.5 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {m.sender === "ai" && (
                  <div className="w-7 h-7 bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 rounded-lg flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`p-3 rounded-2xl text-xs sm:text-sm leading-relaxed max-w-[80%] ${
                    m.sender === "user"
                      ? "bg-indigo-600 text-white rounded-tr-sm"
                      : "bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200/80 dark:border-slate-700 rounded-tl-sm shadow-sm"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center gap-2 text-slate-400 text-xs italic pl-9">
                <Sparkles className="w-3.5 h-3.5 animate-spin text-purple-500" />
                <span>AI жауап дайындауда...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Дайын сұрақ подсказкалары */}
          <div className="p-2.5 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 flex gap-1.5 overflow-x-auto text-[11px]">
            {quickPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="whitespace-nowrap px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition border border-slate-200 dark:border-slate-700"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Мәтін енгізу және жіберу */}
          <div className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Сұрағыңызды жазыңыз..."
              className="flex-1 px-3.5 py-2 text-sm border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="p-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-xl transition shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

