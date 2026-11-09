import Link from "next/link";
import { BookOpen, BrainCircuit, CheckCircle2, ArrowRight, Trophy, Flame } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Басты тақырып */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 mb-4">
          <BrainCircuit className="w-3.5 h-3.5" />
          Жергілікті Ollama AI менторымен
        </span>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Заманауи Білім Беру және Тестілеу Платформасы
        </h1>
        <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
          FastAPI backend, Next.js 16 frontend, Keycloak OIDC қауіпсіздігі және интерактивті Skill Tree & Геймификация жүйесі.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link
            href="/gamification"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-600 hover:to-indigo-700 text-white font-semibold px-6 py-3 rounded-xl shadow-md transition"
          >
            <Trophy className="w-4 h-4 text-amber-200" />
            🎮 Оқу картасы & XP Рейтинг
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/teacher"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-xl shadow-sm transition"
          >
            👨‍🏫 Мұғалім ретінде кіру
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/student"
            className="inline-flex items-center gap-2 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 font-semibold px-6 py-3 rounded-xl shadow-sm transition"
          >
            👨‍🎓 Студент ретінде кіру
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Мүмкіндіктер карточкалары */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="w-12 h-12 bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 rounded-xl flex items-center justify-center mb-4">
            <Trophy className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Геймификация & XP</h3>
          <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
            RPG стиліндегі Skill Tree, деңгейлер (Levels), күнделікті Streak жалыны және үздік студенттер лидерборды.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 rounded-xl flex items-center justify-center mb-4">
            <BookOpen className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Мұғалім кабинеті</h3>
          <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
            Тесттер құрастыру, уақыт шегін (таймер) белгілеу, үй тапсырмаларын беру және журналды CSV экспорттау.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 rounded-xl flex items-center justify-center mb-4">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Студент кабинеті</h3>
          <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
            Онлайн тестілеу, анти-списывание бақылауы, тапсырмаларды файлмен тапсыру және бағаларды көру.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="w-12 h-12 bg-purple-100 dark:bg-purple-950 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center mb-4">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Ollama AI Ментор</h3>
          <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
            Сұрақтарды автоматты генерациялау және студенттің қате жауаптарын қазақша түсіндіріп беру.
          </p>
        </div>
      </div>
    </div>
  );
}
