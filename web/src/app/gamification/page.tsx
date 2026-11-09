"use client";

import { useState } from "react";
import {
  Trophy,
  Flame,
  Zap,
  CheckCircle2,
  Lock,
  Play,
  Star,
  Crown,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  X,
  Target,
  Award,
  ChevronRight,
  RefreshCw,
} from "lucide-react";

interface SkillNode {
  id: string;
  title: string;
  description: string;
  category: string;
  xp_reward: int_or_number;
  status: "completed" | "active" | "locked";
  icon: string;
  quiz_question?: string;
  quiz_options?: string[];
  correct_option_index?: number;
}

type int_or_number = number;

interface LeaderboardUser {
  rank: number;
  name: string;
  avatar: string;
  level: number;
  xp: number;
  streak: number;
  league: string;
  isCurrentUser?: boolean;
}

export default function GamificationPage() {
  const [activeTab, setActiveTab] = useState<"tree" | "leaderboard" | "quests">("tree");
  const [userXP, setUserXP] = useState(1450);
  const [streakDays, setStreakDays] = useState(7);
  const [streakClaimed, setStreakClaimed] = useState(false);
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [quizError, setQuizError] = useState<string | null>(null);
  const [quizSuccess, setQuizSuccess] = useState<string | null>(null);

  // Оқу картасының түйіндері (Skill Tree nodes)
  const [nodes, setNodes] = useState<SkillNode[]>([
    {
      id: "node_1",
      title: "Python негіздері мен синтаксисі",
      description: "Айнымалылар, деректер типтері, циклдер мен шартты операторлар",
      category: "Негіздер",
      xp_reward: 100,
      status: "completed",
      icon: "🐍",
      quiz_question: "Python-да тізімге (list) жаңа элемент қосу үшін қандай әдіс қолданылады?",
      quiz_options: [".push()", ".append()", ".add()", ".insert_last()"],
      correct_option_index: 1,
    },
    {
      id: "node_2",
      title: "Функциялар мен Модульдер",
      description: "def, *args, **kwargs, lambda және құрылымдық модульдер",
      category: "Негіздер",
      xp_reward: 150,
      status: "completed",
      icon: "📦",
      quiz_question: "Функциядағы кездейсоқ атаулы кілттік параметрлерді қабылдау үшін не қолданылады?",
      quiz_options: ["*args", "**kwargs", "&params", "$props"],
      correct_option_index: 1,
    },
    {
      id: "node_3",
      title: "FastAPI REST API негіздері",
      description: "Pydantic модельдері, Path/Query параметрлері және асинхронды маршрутизация",
      category: "Backend",
      xp_reward: 200,
      status: "completed",
      icon: "⚡",
      quiz_question: "FastAPI-де сұраныс деректерін типтеу және валидациялау үшін қандай құрал қолданылады?",
      quiz_options: ["Marshmallow", "Cerberus", "Pydantic", "Django Forms"],
      correct_option_index: 2,
    },
    {
      id: "node_4",
      title: "PostgreSQL және SQLAlchemy 2.0 ORM",
      description: "Асинхронды сессиялар, реляциялық модельдер және байланыс түрлері",
      category: "Деректер қоры",
      xp_reward: 250,
      status: "active",
      icon: "🐘",
      quiz_question: "SQLAlchemy 2.0 нұсқасында кестеден мәлімет таңдаудың заманауи түрі қандай?",
      quiz_options: ["session.query()", "select() операторы", "db.find()", "raw_sql.execute()"],
      correct_option_index: 1,
    },
    {
      id: "node_5",
      title: "Docker және Контейнерлеу",
      description: "Dockerfile жазу, көп контейнерлі желіні Docker Compose арқылы көтеру",
      category: "DevOps",
      xp_reward: 300,
      status: "locked",
      icon: "🐳",
      quiz_question: "Бірнеше микросервисті бірге конфигурациялап, бір командамен іске қосу құралы?",
      quiz_options: ["Docker Compose", "Docker Swarm", "Kubectl", "Systemd"],
      correct_option_index: 0,
    },
    {
      id: "node_6",
      title: "Keycloak OIDC & RBAC Қауіпсіздік",
      description: "JWT токендер, Realm, рөлдер (Student / Teacher / Admin) бойынша қорғау",
      category: "Қауіпсіздік",
      xp_reward: 350,
      status: "locked",
      icon: "🔐",
      quiz_question: "OIDC токенінде қолданушының рөлдері мен құқықтары қай бөлімде сақталады?",
      quiz_options: ["Header", "Payload / Claims", "Signature", "Cookie"],
      correct_option_index: 1,
    },
    {
      id: "node_7",
      title: "Ollama және Жергілікті AI Интеграциясы (БОСС-ДЕҢГЕЙ)",
      description: "Llama 3.2 үлгісі, сұрақ генераторы және дербес AI ментор чат-виджеті",
      category: "Жасанды Интеллект",
      xp_reward: 500,
      status: "locked",
      icon: "👑",
      quiz_question: "Ollama моделінен жауапты асинхронды түрде тарту үшін FastAPI-де қандай HTTP клиент ыңғайлы?",
      quiz_options: ["requests", "httpx.AsyncClient", "urllib3", "socket"],
      correct_option_index: 1,
    },
  ]);

  // Лидерборд деректері
  const leaderboard: LeaderboardUser[] = [
    {
      rank: 1,
      name: "Айгерім Смағұлова",
      avatar: "👩‍💻",
      level: 8,
      xp: 3420,
      streak: 19,
      league: "Бриллиант Лига 💎",
    },
    {
      rank: 2,
      name: "Дәулет Серікқали",
      avatar: "👨‍🎓",
      level: 7,
      xp: 2890,
      streak: 14,
      league: "Алтын Лига 🥇",
    },
    {
      rank: 3,
      name: "Мансұр Төлеген (Сіз)",
      avatar: "🚀",
      level: 5,
      xp: userXP,
      streak: streakDays,
      league: "Алтын Лига 🥇",
      isCurrentUser: true,
    },
    {
      rank: 4,
      name: "Әсел Қайратқызы",
      avatar: "👩‍🎓",
      level: 5,
      xp: 1380,
      streak: 6,
      league: "Күміс Лига 🥈",
    },
    {
      rank: 5,
      name: "Нұрлан Бақытұлы",
      avatar: "👨‍💻",
      level: 4,
      xp: 1120,
      streak: 4,
      league: "Күміс Лига 🥈",
    },
    {
      rank: 6,
      name: "Мадина Әлім",
      avatar: "🎨",
      level: 3,
      xp: 890,
      streak: 3,
      league: "Қола Лига 🥉",
    },
  ];

  // Күнделікті квесттер
  const [quests, setQuests] = useState([
    { id: 1, title: "1 квиз/тест тапсыр", reward: 50, current: 1, target: 1, completed: true, icon: "📝" },
    { id: 2, title: "Ollama AI менторға 1 сұрақ қой", reward: 30, current: 1, target: 1, completed: true, icon: "🤖" },
    { id: 3, title: "Skill Tree бойынша жаңа түйінді аяқта", reward: 70, current: 0, target: 1, completed: false, icon: "🗺️" },
  ]);

  // Streak бонусын алу
  const handleClaimStreak = () => {
    if (streakClaimed) return;
    setUserXP((prev) => prev + 50);
    setStreakClaimed(true);
  };

  // Түйінді ашу және сұрақ тапсыру
  const handleOpenNode = (node: SkillNode) => {
    if (node.status === "locked") return;
    setSelectedNode(node);
    setSelectedOption(null);
    setQuizError(null);
    setQuizSuccess(null);
  };

  const handleVerifyQuiz = () => {
    if (!selectedNode || selectedOption === null) return;

    if (selectedOption !== selectedNode.correct_option_index) {
      setQuizError("Жауап дұрыс емес! Тақырыпты қайталап, қайта таңдаңыз.");
      setQuizSuccess(null);
      return;
    }

    // Дұрыс жауап!
    setQuizError(null);
    setQuizSuccess(`Керемет! Сіз +${selectedNode.xp_reward} XP ұтып алдыңыз! 🎉`);
    setUserXP((prev) => prev + selectedNode.xp_reward);

    // Түйіндерді жаңарту
    setNodes((prevNodes) => {
      const idx = prevNodes.findIndex((n) => n.id === selectedNode.id);
      if (idx === -1) return prevNodes;

      const newNodes = [...prevNodes];
      newNodes[idx] = { ...newNodes[idx], status: "completed" };

      // Келесі түйінді unlock ету
      if (idx + 1 < newNodes.length && newNodes[idx + 1].status === "locked") {
        newNodes[idx + 1] = { ...newNodes[idx + 1], status: "active" };
      }
      return newNodes;
    });

    // Квестті жаңарту
    setQuests((prev) =>
      prev.map((q) => (q.id === 3 ? { ...q, current: 1, completed: true } : q))
    );

    setTimeout(() => {
      setSelectedNode(null);
    }, 2000);
  };

  // Есептеулер
  const currentLevel = Math.floor(userXP / 400) + 1;
  const xpInCurrentLevel = userXP % 400;
  const progressPercent = Math.min(100, Math.round((xpInCurrentLevel / 400) * 100));

  const weekDays = [
    { day: "Дс", active: true },
    { day: "Сс", active: true },
    { day: "Ср", active: true },
    { day: "Бс", active: true },
    { day: "Жм", active: true },
    { day: "Сб", active: true },
    { day: "Жк", active: true },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. БАСТЫ ГЕЙМИФИКАЦИЯ БАННЕРІ */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-700 via-purple-700 to-indigo-900 text-white p-6 sm:p-8 shadow-xl">
        <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          {/* СОЛ ЖАҚ: Деңгей және XP */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="px-3.5 py-1 bg-white/20 backdrop-blur-md text-amber-300 text-xs font-black rounded-full uppercase tracking-wider flex items-center gap-1 border border-white/20">
                <Crown className="w-3.5 h-3.5 text-amber-300" />
                Алтын Лига 🥇 (3-орын)
              </span>
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-black flex items-center gap-2">
                Level {currentLevel}: Backend Шебері
              </h1>
              <p className="text-indigo-200 text-sm mt-1">
                Келесі деңгейге жету үшін тағы {400 - xpInCurrentLevel} XP қажет
              </p>
            </div>

            {/* Прогресс-бар */}
            <div className="space-y-1.5 pt-1">
              <div className="flex justify-between text-xs font-bold text-indigo-100">
                <span>{xpInCurrentLevel} XP</span>
                <span>400 XP ({progressPercent}%)</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden backdrop-blur-sm">
                <div
                  className="bg-gradient-to-r from-amber-400 to-emerald-400 h-full rounded-full transition-all duration-500 shadow-sm"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          </div>

          {/* ОРТА: Жүйелілік (Streak Days) */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/15 text-center flex flex-col items-center justify-center">
            <div className="flex items-center gap-2 text-amber-300 font-black text-2xl">
              <Flame className="w-7 h-7 text-amber-400 animate-pulse fill-amber-400" />
              <span>{streakDays} Күн қатарынан!</span>
            </div>
            <p className="text-xs text-indigo-200 mt-1">Үздіксіз оқу белсенділігі</p>

            <div className="flex items-center gap-2 mt-3.5">
              {weekDays.map((item, idx) => (
                <div key={idx} className="flex flex-col items-center gap-1">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold transition shadow-sm ${
                      item.active
                        ? "bg-amber-400 text-slate-900 shadow-amber-500/50"
                        : "bg-white/10 text-white/50"
                    }`}
                  >
                    🔥
                  </div>
                  <span className="text-[10px] text-indigo-200">{item.day}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ОҢ ЖАҚ: Күнделікті Бонус және Статистика */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/15 flex flex-col justify-between h-full space-y-4">
            <div>
              <span className="text-xs font-bold text-indigo-200 uppercase">Жалпы жинаған ұпай</span>
              <div className="text-3xl font-black text-white flex items-center gap-2 mt-0.5">
                <Zap className="w-7 h-7 text-amber-300 fill-amber-300" />
                <span>{userXP} XP</span>
              </div>
            </div>

            <button
              onClick={handleClaimStreak}
              disabled={streakClaimed}
              className={`w-full py-2.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition shadow-md ${
                streakClaimed
                  ? "bg-emerald-600/80 text-white cursor-default"
                  : "bg-amber-400 hover:bg-amber-300 text-slate-900 active:scale-95"
              }`}
            >
              {streakClaimed ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-white" />
                  <span>Бүгінгі бонус алынды (+50 XP)</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-slate-900" />
                  <span>Күнделікті бонус алу (+50 XP)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 2. ТАБТАР АУЫСТЫРУ (NAV TABS) */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-4">
        <button
          onClick={() => setActiveTab("tree")}
          className={`pb-3 text-sm sm:text-base font-bold flex items-center gap-2 border-b-2 transition ${
            activeTab === "tree"
              ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
              : "border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          }`}
        >
          <Target className="w-4 h-4" />
          <span>🗺️ Оқу картасы (Skill Tree)</span>
        </button>

        <button
          onClick={() => setActiveTab("leaderboard")}
          className={`pb-3 text-sm sm:text-base font-bold flex items-center gap-2 border-b-2 transition ${
            activeTab === "leaderboard"
              ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
              : "border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          }`}
        >
          <Trophy className="w-4 h-4" />
          <span>🏆 Лидерлер тақтасы (Top Students)</span>
        </button>

        <button
          onClick={() => setActiveTab("quests")}
          className={`pb-3 text-sm sm:text-base font-bold flex items-center gap-2 border-b-2 transition ${
            activeTab === "quests"
              ? "border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
              : "border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          }`}
        >
          <Award className="w-4 h-4" />
          <span>🎯 Күнделікті квесттер</span>
        </button>
      </div>

      {/* 3. ТАБТАР МАЗМҰНЫ */}
      {/* -------------------- TAB 1: SKILL TREE -------------------- */}
      {activeTab === "tree" && (
        <div className="space-y-6">
          <div className="bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 rounded-2xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🧭</span>
              <div>
                <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                  Интерактивті Дағдылар Жолы
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Әрбір белсенді түйінді шерткенде мини-тапсырма ашылады. Сәтті орындап, қосымша XP және келесі құлыпты ашыңыз!
                </p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-3 text-xs font-semibold">
              <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Аяқталды
              </span>
              <span className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400">
                <Play className="w-3.5 h-3.5 fill-indigo-600 dark:fill-indigo-400" /> Белсенді
              </span>
              <span className="flex items-center gap-1 text-slate-400">
                <Lock className="w-3.5 h-3.5" /> Құлыптаулы
              </span>
            </div>
          </div>

          {/* ЖОЛ БОЙЫНША ТҮЙІНДЕР (SKILL TREE PATH) */}
          <div className="relative max-w-3xl mx-auto py-8">
            {/* Орталық байланыс сызығы */}
            <div className="absolute left-8 sm:left-1/2 top-4 bottom-4 w-1 bg-slate-200 dark:bg-slate-800 -translate-x-1/2 -z-0" />

            <div className="space-y-8 relative z-10">
              {nodes.map((node, index) => {
                const isEven = index % 2 === 0;
                const isCompleted = node.status === "completed";
                const isActive = node.status === "active";
                const isLocked = node.status === "locked";

                return (
                  <div
                    key={node.id}
                    className={`flex items-center gap-6 ${
                      isEven ? "sm:flex-row-reverse" : "sm:flex-row"
                    } flex-row`}
                  >
                    {/* Карточка */}
                    <div
                      onClick={() => handleOpenNode(node)}
                      className={`flex-1 p-5 rounded-2xl border transition duration-200 cursor-pointer ${
                        isActive
                          ? "bg-white dark:bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/10 hover:border-indigo-600 ring-2 ring-indigo-500/20"
                          : isCompleted
                          ? "bg-white dark:bg-slate-900 border-emerald-200 dark:border-emerald-900/40 hover:border-emerald-400"
                          : "bg-slate-50 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800 opacity-60 cursor-not-allowed"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{node.icon}</span>
                            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                              {node.category}
                            </span>
                          </div>
                          <h4 className="font-bold text-slate-900 dark:text-slate-100 text-base mt-1">
                            {node.title}
                          </h4>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                            {node.description}
                          </p>
                        </div>

                        <div className="flex flex-col items-end shrink-0">
                          <span className="px-2.5 py-1 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-xs font-bold rounded-lg border border-amber-200 dark:border-amber-900 flex items-center gap-1">
                            <Zap className="w-3 h-3 fill-amber-500 text-amber-500" />
                            +{node.xp_reward} XP
                          </span>
                        </div>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs">
                        {isCompleted && (
                          <span className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Тапсырма аяқталды
                          </span>
                        )}
                        {isActive && (
                          <span className="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 animate-pulse">
                            <Play className="w-3.5 h-3.5 fill-indigo-600 dark:fill-indigo-400" /> Тапсырманы орындау
                          </span>
                        )}
                        {isLocked && (
                          <span className="font-semibold text-slate-400 flex items-center gap-1">
                            <Lock className="w-3.5 h-3.5" /> Алдыңғы деңгейді аяқтаңыз
                          </span>
                        )}

                        <span className="text-slate-400 flex items-center gap-0.5 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium">
                          Толығырақ <ChevronRight className="w-3.5 h-3.5" />
                        </span>
                      </div>
                    </div>

                    {/* Орталық шеңбер (Node Icon Indicator) */}
                    <div
                      className={`w-12 h-12 rounded-full border-4 flex items-center justify-center shrink-0 z-10 transition-all shadow-md ${
                        isCompleted
                          ? "bg-emerald-500 border-white dark:border-slate-900 text-white"
                          : isActive
                          ? "bg-indigo-600 border-indigo-200 dark:border-indigo-950 text-white animate-bounce"
                          : "bg-slate-200 dark:bg-slate-800 border-white dark:border-slate-900 text-slate-400"
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-6 h-6" />
                      ) : isActive ? (
                        <Play className="w-5 h-5 fill-white text-white ml-0.5" />
                      ) : (
                        <Lock className="w-5 h-5" />
                      )}
                    </div>

                    <div className="hidden sm:block flex-1" />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* -------------------- TAB 2: LEADERBOARD -------------------- */}
      {activeTab === "leaderboard" && (
        <div className="space-y-6">
          {/* ТОП-3 ПОДИУМ */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
            {/* 2-ОРЫН */}
            <div className="order-2 md:order-1 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 text-center shadow-sm relative flex flex-col items-center justify-between">
              <span className="text-3xl mb-1">🥈</span>
              <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-800 text-4xl flex items-center justify-center border-4 border-slate-300 dark:border-slate-700 shadow-inner my-2">
                {leaderboard[1].avatar}
              </div>
              <h3 className="font-black text-slate-900 dark:text-slate-100 text-lg">{leaderboard[1].name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">{leaderboard[1].league}</p>
              <div className="mt-4 px-4 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl w-full flex items-center justify-between text-sm font-bold">
                <span className="text-slate-500">🔥 {leaderboard[1].streak} күн</span>
                <span className="text-indigo-600 dark:text-indigo-400">{leaderboard[1].xp} XP</span>
              </div>
            </div>

            {/* 1-ОРЫН (АЛТЫН ЖӘНЕ ҮЛКЕНДЕУ) */}
            <div className="order-1 md:order-2 bg-gradient-to-b from-amber-500/10 via-white to-white dark:from-amber-950/20 dark:via-slate-900 dark:to-slate-900 rounded-3xl border-2 border-amber-400/60 dark:border-amber-500/40 p-6 text-center shadow-lg relative flex flex-col items-center justify-between -translate-y-2">
              <div className="flex items-center gap-1 text-amber-500 font-black text-sm uppercase tracking-wider">
                <Crown className="w-5 h-5 fill-amber-500 text-amber-500" /> Чемпион 🥇
              </div>
              <div className="w-24 h-24 rounded-full bg-amber-100 dark:bg-amber-950/50 text-5xl flex items-center justify-center border-4 border-amber-400 shadow-md my-2">
                {leaderboard[0].avatar}
              </div>
              <h3 className="font-black text-slate-900 dark:text-slate-100 text-xl">{leaderboard[0].name}</h3>
              <p className="text-xs text-amber-600 dark:text-amber-400 font-bold">{leaderboard[0].league}</p>
              <div className="mt-4 px-4 py-2.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 rounded-xl w-full flex items-center justify-between text-sm font-black">
                <span className="text-amber-700 dark:text-amber-300">🔥 {leaderboard[0].streak} күн</span>
                <span className="text-amber-600 dark:text-amber-400">{leaderboard[0].xp} XP</span>
              </div>
            </div>

            {/* 3-ОРЫН (СІЗ) */}
            <div className="order-3 md:order-3 bg-white dark:bg-slate-900 rounded-3xl border border-indigo-300 dark:border-indigo-800 p-6 text-center shadow-sm relative flex flex-col items-center justify-between ring-2 ring-indigo-500/20">
              <span className="text-3xl mb-1">🥉</span>
              <div className="w-20 h-20 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-4xl flex items-center justify-center border-4 border-amber-600 dark:border-amber-700 shadow-inner my-2">
                {leaderboard[2].avatar}
              </div>
              <h3 className="font-black text-slate-900 dark:text-slate-100 text-lg">{leaderboard[2].name}</h3>
              <span className="text-xs bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold px-2.5 py-0.5 rounded-full mt-1">
                Сіздің нәтижеңіз
              </span>
              <div className="mt-4 px-4 py-2 bg-slate-50 dark:bg-slate-800 rounded-xl w-full flex items-center justify-between text-sm font-bold">
                <span className="text-slate-500">🔥 {leaderboard[2].streak} күн</span>
                <span className="text-indigo-600 dark:text-indigo-400">{userXP} XP</span>
              </div>
            </div>
          </div>

          {/* ТОЛЫҚ КЕСТЕ */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div className="p-5 border-b border-slate-100 dark:border-slate-800 font-bold text-slate-900 dark:text-slate-100 flex items-center justify-between">
              <span>Студенттердің апталық рейтингі</span>
              <span className="text-xs text-slate-400 font-normal">Әр дүйсенбі сағат 00:00-де жаңарады</span>
            </div>

            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {leaderboard.map((item) => (
                <div
                  key={item.rank}
                  className={`p-4 flex items-center justify-between transition ${
                    item.isCurrentUser
                      ? "bg-indigo-50/70 dark:bg-indigo-950/30 font-bold"
                      : "hover:bg-slate-50 dark:hover:bg-slate-800/40"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span
                      className={`w-8 text-center font-black text-sm ${
                        item.rank === 1
                          ? "text-amber-500"
                          : item.rank === 2
                          ? "text-slate-400"
                          : item.rank === 3
                          ? "text-amber-700"
                          : "text-slate-500"
                      }`}
                    >
                      #{item.rank}
                    </span>

                    <span className="text-2xl">{item.avatar}</span>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-900 dark:text-slate-100 text-sm font-bold">
                          {item.name}
                        </span>
                        {item.isCurrentUser && (
                          <span className="px-2 py-0.5 text-[10px] bg-indigo-600 text-white rounded-full">
                            Сіз
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-400">Level {item.level} • {item.league}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 hidden sm:flex items-center gap-1">
                      🔥 {item.streak} күн
                    </span>
                    <span className="text-sm font-black text-indigo-600 dark:text-indigo-400">
                      {item.xp} XP
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* -------------------- TAB 3: DAILY QUESTS -------------------- */}
      {activeTab === "quests" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quests.map((q) => (
              <div
                key={q.id}
                className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-3xl">{q.icon}</span>
                    <span className="px-2.5 py-1 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-xs font-bold rounded-lg border border-amber-200 dark:border-amber-900 flex items-center gap-1">
                      <Zap className="w-3 h-3 fill-amber-500 text-amber-500" />
                      +{q.reward} XP
                    </span>
                  </div>
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-base mt-3">
                    {q.title}
                  </h4>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold text-slate-500">
                    <span>Прогресс</span>
                    <span>
                      {q.current} / {q.target}
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        q.completed ? "bg-emerald-500" : "bg-indigo-600"
                      }`}
                      style={{ width: `${(q.current / q.target) * 100}%` }}
                    />
                  </div>

                  <div className="pt-2">
                    {q.completed ? (
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-4 h-4" /> Тапсырма орындалды
                      </span>
                    ) : (
                      <span className="text-xs font-semibold text-slate-400">
                        Орындау күтілуде...
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. ИНТЕРАКТИВТІ СҰРАҚ МОДАЛЬДЫ ТЕРЕЗЕСІ (QUIZ CHALLENGE MODAL) */}
      {selectedNode && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-6 relative">
            <button
              onClick={() => setSelectedNode(null)}
              className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3">
              <span className="text-3xl p-3 bg-indigo-50 dark:bg-indigo-950/40 rounded-2xl">
                {selectedNode.icon}
              </span>
              <div>
                <span className="text-xs uppercase font-bold text-indigo-600 dark:text-indigo-400">
                  {selectedNode.category}
                </span>
                <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">
                  {selectedNode.title}
                </h3>
              </div>
            </div>

            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {selectedNode.description}
            </p>

            {/* Сұрақ блогы */}
            {selectedNode.quiz_question && (
              <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 space-y-3">
                <div className="flex items-center gap-1.5 font-bold text-xs text-indigo-600 dark:text-indigo-400 uppercase tracking-wide">
                  <Sparkles className="w-3.5 h-3.5" />
                  Экспресс Сұрақ (+{selectedNode.xp_reward} XP)
                </div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {selectedNode.quiz_question}
                </p>

                <div className="space-y-2 pt-1">
                  {selectedNode.quiz_options?.map((opt, i) => (
                    <button
                      key={i}
                      disabled={selectedNode.status === "completed"}
                      onClick={() => setSelectedOption(i)}
                      className={`w-full text-left p-3 rounded-xl border text-xs sm:text-sm font-medium transition ${
                        selectedOption === i
                          ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                          : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:border-indigo-400"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Хабарламалар */}
            {quizError && (
              <div className="p-3 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded-xl text-xs font-semibold flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span>{quizError}</span>
              </div>
            )}

            {quizSuccess && (
              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs font-bold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{quizSuccess}</span>
              </div>
            )}

            {/* Батырмалар */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setSelectedNode(null)}
                className="px-4 py-2 text-sm font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              >
                Жабу
              </button>

              {selectedNode.status === "active" && (
                <button
                  onClick={handleVerifyQuiz}
                  disabled={selectedOption === null}
                  className="px-5 py-2.5 rounded-xl font-bold text-sm bg-indigo-600 hover:bg-indigo-700 text-white transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Жауапты тексеру (+{selectedNode.xp_reward} XP)
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

