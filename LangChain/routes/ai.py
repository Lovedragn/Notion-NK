from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from models.schemas import AskRequest, SummarizeRequest, CreateTaskRequest, UpdateTaskRequest
from services.spring_client import fetch_tasks, create_task as spring_create_task, update_task as spring_update_task
from services.llm_service import ask_model, extract_json_from_text

router = APIRouter()


def _parse_date(date_str: str):
	from datetime import datetime
	for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
		try:
			return datetime.strptime(date_str[:len(fmt)], fmt)
		except Exception:
			continue
	return None


def _filter_tasks_for_query(tasks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
	q = (query or "").lower()
	from datetime import datetime
	today = datetime.now().date()

	# Heuristic: pending implies exclude completed/cancelled
	def is_pending(t: Dict[str, Any]) -> bool:
		status = str(t.get("status", "")).lower()
		return status not in ("completed", "done", "cancelled", "canceled")

	# Heuristic: due on/before today when asked for below/before/today/pending/overdue
	def is_due_on_or_before_today(t: Dict[str, Any]) -> bool:
		date_val = t.get("taskDate") or t.get("dueDate") or t.get("date")
		if not date_val:
			return False
		parsed = _parse_date(str(date_val))
		if not parsed:
			return False
		# Ignore obviously invalid historical dates (before 1900)
		if parsed.year < 1900:
			return False
		return parsed.date() <= today

	result = tasks
	if "pending" in q or "overdue" in q or "before today" in q or "below" in q or "before" in q or "today" in q:
		result = [t for t in result if is_pending(t)]
		# Only constrain by date when user hints at time-based filtering
		if any(k in q for k in ["overdue", "before today", "before", "below", "today"]):
			result = [t for t in result if is_due_on_or_before_today(t)]
	return result


@router.post("/ask")
async def ask_question(data: AskRequest):
	query = data.query.strip()
	if not query:
		raise HTTPException(status_code=400, detail="No query provided")
	try:
		tasks = await fetch_tasks(user_id=data.userId, token=data.token)
	except HTTPException:
		tasks = []

	filtered = _filter_tasks_for_query(tasks, query)
	prompt = (
		"User question: " + query + "\n\n" +
		"Filtered tasks JSON (may be empty):\n" + str(filtered) + "\n\n" +
		"Instructions: You are a helpful assistant for a task manager. "
		"Prefer the filtered tasks for answering. If the user asks for pending tasks below/before today, "
		"only include tasks due on or before today and exclude completed/cancelled items. "
		"Answer concisely in 1-3 sentences."
	)
	answer = ask_model(prompt)
	return {"answer": answer, "count": len(filtered)}


@router.post("/summarize")
async def summarize_tasks(data: SummarizeRequest):
	try:
		completed = await fetch_tasks(user_id=data.userId, status="completed", token=data.token)
	except HTTPException:
		completed = []
	if not completed:
		return {"summary": "No completed tasks available to summarize.", "completedCount": 0}
	prompt = (
		"Summarize the following completed tasks into 2-4 bullet insights, "
		"focusing on impact and themes.\n\nTasks JSON:\n" + str(completed)
	)
	summary = ask_model(prompt)
	return {"summary": summary, "completedCount": len(completed)}


@router.post("/create-task")
async def create_task_from_prompt(data: CreateTaskRequest):
	schema_hint = (
		"Return STRICT JSON with keys: title (string), description (string, optional), "
		"dueDate (ISO-8601 date string, optional), status (string, default 'pending'), userId (number, optional), hash (string, optional). "
		"Do not include any commentary."
	)
	prompt = f"User prompt: {data.prompt}\n\n{schema_hint}"
	model_text = ask_model(prompt)
	task_json = extract_json_from_text(model_text) or {}
	if not task_json.get("title"):
		task_json["title"] = data.prompt.strip()[:100]
	if data.userId is not None and "userId" not in task_json:
		task_json["userId"] = data.userId
	hash_value = data.hash
	created = await spring_create_task(task_json, hash_value=hash_value, token=data.token)
	return {"message": f"Created task: {created.get('title', task_json.get('title'))}", "task": created}


@router.post("/update-task")
async def update_task_from_prompt(data: UpdateTaskRequest):
	schema_hint = (
		"Return STRICT JSON with keys: id (required), title (optional), description (optional), "
		"dueDate (optional ISO-8601), status (optional), userId (optional). No commentary."
	)
	prompt = f"Instruction: {data.prompt}\n\n{schema_hint}"
	model_text = ask_model(prompt)
	update_json = extract_json_from_text(model_text)
	if not update_json or "id" not in update_json:
		raise HTTPException(status_code=400, detail="Could not parse task update with an 'id'")
	task_id = update_json.pop("id")
	updated = await spring_update_task(task_id, update_json, token=data.token)
	return {"message": f"Updated task {task_id}", "task": updated}
