const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface QuizRead {
  id: number;
  title: string;
  topic: string;
  owner_id: number;
  is_published: boolean;
  created_at: string;
}

export interface QuestionRead {
  id: number;
  quiz_id: number;
  prompt: string;
  options: string[];
  correct_index?: number;
}

export interface QuizResultsSummary {
  quiz_id: number;
  quiz_title: string;
  total_attempts: number;
  average_score: number;
  average_percent: number;
  results: Array<{
    attempt_id: number;
    student_id: number;
    student_name: string;
    student_email: string;
    score: number;
    total: number;
    percent: number;
    submitted_at: string;
  }>;
}

function buildHeaders(token?: string): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function apiLogin(email: string, password: string) {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: buildHeaders(),
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiListQuizzes(token?: string): Promise<QuizRead[]> {
  const res = await fetch(`${API_BASE_URL}/api/quizzes`, {
    headers: buildHeaders(token),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiCreateQuiz(
  payload: { title: string; topic: string },
  token?: string
): Promise<QuizRead> {
  const res = await fetch(`${API_BASE_URL}/api/quizzes`, {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiGenerateQuestions(
  quizId: number,
  payload: { topic: string; count: number },
  token?: string
) {
  const res = await fetch(`${API_BASE_URL}/api/quizzes/${quizId}/generate-questions`, {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiGetQuizResults(
  quizId: number,
  token?: string
): Promise<QuizResultsSummary> {
  const res = await fetch(`${API_BASE_URL}/api/quizzes/${quizId}/results`, {
    headers: buildHeaders(token),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function getQuizResultsCsvUrl(quizId: number): string {
  return `${API_BASE_URL}/api/quizzes/${quizId}/results/export`;
}
