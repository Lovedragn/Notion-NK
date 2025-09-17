
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

