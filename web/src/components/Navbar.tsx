"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { GraduationCap, User, Bell, Check, Sparkles, Sun, Moon, Flame, Zap } from "lucide-react";

interface NotificationItem {
  id: number;
  title: string;
  message: string;
  time: string;
  isRead: boolean;
}

export default function Navbar() {
  const [isDark, setIsDark] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 1,
      title: "Жаңа баға қойылды",
      message: "Мұғалім 'PostgreSQL сұраныстары' үй тапсырмаңызды тексеріп, 95 балл қойды!",
      time: "10 минут бұрын",
      isRead: false,
    },
    {
      id: 2,
      title: "Жаңа тест жарияланды",
      message: "FastAPI және SQLAlchemy курсы бойынша жаңа бақылау тесті ашылды.",
      time: "1 сағат бұрын",
      isRead: false,
    },
  ]);

  // Қараңғы режимді анықтау және жүктеу
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    } else {
      document.documentElement.classList.remove("dark");
      setIsDark(false);
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  };

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-xl">
          <GraduationCap className="w-7 h-7" />
          <span>EduPlatform</span>
        </Link>

        <nav className="flex items-center gap-5">
          <Link
            href="/courses"
            className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition"
          >
            📚 Курстар
          </Link>
          <Link
            href="/gamification"
            className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition flex items-center gap-1"
          >
            🎮 Дағдылар & Рейтинг
          </Link>
          <Link
            href="/teacher"
            className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition"
          >
            👨‍🏫 Мұғалім
          </Link>
          <Link
            href="/student"
            className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition"
          >
            👨‍🎓 Студент
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          {/* XP ЖӘНЕ STREAK ИНДИКАТОРЫ */}
          <Link
            href="/gamification"
            className="hidden md:flex items-center gap-2 bg-gradient-to-r from-amber-50 to-indigo-50 dark:from-amber-950/40 dark:to-indigo-950/40 border border-amber-200/80 dark:border-amber-800/40 px-3 py-1.5 rounded-full text-xs font-bold text-slate-800 dark:text-slate-200 hover:shadow-sm transition"
          >
            <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
              <Flame className="w-3.5 h-3.5 fill-amber-500" />
              7 күн
            </span>
            <span className="text-slate-300 dark:text-slate-600">|</span>
            <span className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400">
              <Zap className="w-3.5 h-3.5 fill-indigo-500" />
              1,450 XP
            </span>
          </Link>
          {/* ҚАРАҢҒЫ / ЖАРЫҚ РЕЖИМ БАТЫРМАСЫ (DARK MODE TOGGLE) */}
          <button
            onClick={toggleTheme}
            aria-label="Тақырыпты ауыстыру"
            className="p-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-amber-400" />
            ) : (
              <Moon className="w-5 h-5 text-slate-600" />
            )}
          </button>

          {/* ХАБАРЛАМАЛАР ҚОҢЫРАУШАСЫ */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* ХАБАРЛАМАЛАР ТЕРЕЗЕСІ */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-4 z-50">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-2">
                  <div className="flex items-center gap-1.5 font-bold text-slate-900 dark:text-slate-100 text-sm">
                    <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <span>Хабарламалар</span>
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                    >
                      <Check className="w-3 h-3" /> Барлығын оқу
                    </button>
                  )}
                </div>

                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`p-3 rounded-xl border transition ${
                        n.isRead
                          ? "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800"
                          : "bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-100 dark:border-indigo-900"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">{n.title}</h4>
                        <span className="text-[10px] text-slate-400">{n.time}</span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">{n.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ЖЕКЕ ПРОФИЛЬ */}
          <Link
            href="/profile"
            className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 px-3.5 py-1.5 rounded-full text-sm font-semibold transition border border-slate-200 dark:border-slate-700"
          >
            <User className="w-4 h-4 text-slate-500 dark:text-slate-400" />
            <span>Жеке Профиль</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
