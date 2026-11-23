# API спецификациясы (QuizAI)

## Служебный

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `GET /api/health` | все | `200`, статус БД (`"database": "up"` / `"down"`) |

## Модуль 1–2: регистрация и проверка входа

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `POST /api/auth/register` | все | `201`. Если email уже есть — `409`. Короткий пароль или `role: admin` в теле дают `422`. Пароля в ответе нет |
| `POST /api/auth/login` | все | `200` или `401` «Email немесе құпиясөз қате». Токен не выдаётся, это только проверка |

## Модуль 3: управление пользователями (только admin)

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `GET /api/users` | admin | `200`, список. Для teacher и student — `403` |
| `GET /api/users/{id}` | admin | `200` или `404` |
| `PATCH /api/users/{id}` | admin | `200` (меняются имя и роль). Свою роль менять нельзя: `400` |
| `DELETE /api/users/{id}` | admin | `204`. Удалить себя нельзя: `400` |

## Модуль 4: основной объект — тест (quiz)

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `GET /api/quizzes` | все роли | student видит опубликованные, teacher — свои и опубликованные, admin — все |
| `POST /api/quizzes` | teacher, admin | `201` |
| `GET /api/quizzes/{id}` | все роли | `200` или `404`. Студент получает тест без правильных ответов |
| `PATCH /api/quizzes/{id}` | teacher, admin | `200`. Чужой тест: `403` |
| `DELETE /api/quizzes/{id}` | teacher, admin | `204`. Чужой тест: `403` |

## Модуль 5: подчинённый объект — вопрос

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `POST /api/quizzes/{id}/questions` | teacher, admin | `201`. В опубликованный тест нельзя: `400`. `correct_index` больше числа вариантов: `400` |
| `PATCH /api/questions/{id}` | teacher, admin | `200`. Опубликованный тест: `400`. Чужой: `403` |
| `DELETE /api/questions/{id}` | teacher, admin | `204`, с теми же правилами |

## Модуль 6: основное действие — публикация и сдача

| Endpoint | Кто | Ответ |
| :--- | :--- | :--- |
| `POST /api/quizzes/{id}/publish` | teacher, admin | `200`. Тест без вопросов: `400` |
| `POST /api/quizzes/{id}/attempts` | student | `201`, результат. Если число ответов не совпадает с числом вопросов: `400` |
| `GET /api/attempts/me` | student | `200`, «мои попытки» |
