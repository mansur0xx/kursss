import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import AIChatWidget from "@/components/AIChatWidget";

export const metadata: Metadata = {
  title: "EduPlatform - Оқу платформасы (FastAPI + Next.js)",
  description: "Мұғалімдер мен студенттерге арналған толық циклді білім беру жүйесі",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="kk">
      <body className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased transition-colors duration-200">
        <Navbar />
        <main className="flex-1">{children}</main>
        <AIChatWidget />
        <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 text-center text-sm text-slate-500 dark:text-slate-400 transition-colors">
          EduPlatform © 2026. FastAPI + Next.js 16 + Keycloak + Ollama.
        </footer>
      </body>
    </html>
  );
}

