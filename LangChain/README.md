## LangChain Service (single-file) - Workflow

### Overview
- Service: FastAPI app in `LangChain/main.py` (single file)
- Storage: MySQL (`users`, `tasks`) on `localhost:3306`
- Identity: All task scoping uses `users.url_hash` (the frontend passes `hash`)
- Memory: In-process chat history per `hash` (last 50 messages)

### Tables (expected)
- `users(email, password, url_hash)`
- `tasks(id, task_date, title, user_email)`
  - `tasks.user_email` → FK to `users.email`

### Data Flow
1) Frontend passes `hash` from the URL/local storage to scope requests.
2) API joins `tasks` with `users` via `url_hash` to fetch/update/delete only the owner’s data.
3) Create and update operations parse dates from natural language; missing/invalid dates default to today (server-side).
4) Chat memory maintains minimal context per `hash` to keep the conversation coherent.

### Endpoints
- `POST /refine` → Normalize free text into structured actions
  - Body: `{ prompt, hash? }`
  - Returns: `{ intent: 'create'|'update'|'delete'|'summarize'|'ask', id?, title?, date?, hash? }`
  - Notes: Avoids treating stray numbers (e.g., durations) as IDs. IDs are only recognized as `#12`, `id 12`, or `task 12`.

- `POST /create-task` → Create a task for `hash`
  - Body: `{ prompt, hash }`
  - Extracts `date` from prompt; if missing/invalid, uses today.
  - Returns: `{ message, task }`

- `POST /update-task` → Update title/date
  - Body: `{ prompt, hash }`
  - ID is read from `#12`/`id 12`/`task 12`; if not present, resolves by title fragment within the same `hash`.
  - Ownership enforced: updating a task outside the `hash` returns 403.
  - Returns: `{ message, task }`

- `POST /delete-task` → Delete by id with ownership
  - Body: `{ id, hash }`
  - Returns: `{ message }`

- `POST /summarize` → Overdue vs upcoming summary
  - Body: `{ hash }`
  - Returns: `{ summary, overdueCount, upcomingCount, total }`

- `POST /ask` → Basic assistant reply with memory
  - Body: `{ query, hash? }`
  - Returns: `{ answer }`

- `GET /history/{hash}` → Chat history for a user
  - Returns: `{ messages: [{ role, content }] }`

### Frontend Usage Pattern
Recommended 2-step for natural language:
1) Send raw input to `/refine`.
2) Call the appropriate endpoint:
   - `create-task` with `{ prompt, hash }` from refined `title`/`date` (or reuse the original prompt)
   - `update-task` with `{ prompt, hash }` (set explicit `id` if refine found it; otherwise rely on title matching)
   - `delete-task` with `{ id, hash }` if refine returned an `id`
   - `summarize` with `{ hash }`

### Date Handling
- Parses `dd/mm/yyyy` or `yyyy-mm-dd`.
- Normalizes to ISO `yyyy-mm-dd`.
- Missing/invalid date on create → defaults to today.
- Update: removes any date tokens from new titles.

### Errors (common)
- `400 Nothing to update` → Provide new title via `to <title>` or include a date.
- `400 Could not identify a task to update` → Make ID explicit (e.g., `task 12`) or use a more unique title fragment.
- `403 Task does not belong to user` → The `id` resolved is not owned by `hash`.
- `404 User not found for hash` / `404 Task not found` when data doesn’t exist.

### Setup
- Env (optional overrides): `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`, `FRONTEND_ORIGINS`.
- Install deps inside `LangChain/venv`:
  - `pip install fastapi uvicorn pymysql pydantic`
- Run: `uvicorn main:app --reload --port 8000`

### Notes
- This service no longer depends on separate routers/services; everything lives in `main.py`.
- In-memory history resets on server restart.

## Endpoints
- POST `/ask` — Ask natural language questions about your tasks.
- POST `/summarize` — Summarize completed tasks into insights.
- POST `/create-task` — Parse natural language to create a task in Spring Boot.
- POST `/update-task` — Parse natural language to update an existing task.

## Install & Run

Using the existing virtual environment in `LangChain/venv` is recommended.

- Install dependencies:
```
venv\Scripts\pip.exe install -r requirements.txt
```

- Run the API:
```
venv\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8000
```

## Request Examples

- Ask:
```
POST /ask
{
  "query": "Show my pending tasks this week",
  "userId": 1
}
```

- Summarize:
```
POST /summarize
{
  "userId": 1
}
```

- Create task:
```
POST /create-task
{
  "prompt": "Add a meeting with client tomorrow at 3pm",
  "userId": 1
}
```

- Update task:
```
POST /update-task
{
  "prompt": "Mark task 5 as completed",
  "userId": 1
}
```

## Notes
- The service calls the Spring Boot `/tasks` endpoints via `httpx`.
- If Spring endpoints are protected, set `SPRING_JWT` to a valid token.

