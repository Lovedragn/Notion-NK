import os
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

import pymysql

from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*")

# ----- App -----
app = FastAPI()
allow_origins = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()] or ["*"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# ----- DB Helpers -----

def get_conn():
	return pymysql.connect(
		host=os.getenv("MYSQL_HOST", "localhost"),
		port=int(os.getenv("MYSQL_PORT", "3306")),
		user=os.getenv("MYSQL_USER", "root"),
		password=os.getenv("MYSQL_PASSWORD", "Sujith@6212"),
		database=os.getenv("MYSQL_DB", "knot"),
		cursorclass=pymysql.cursors.DictCursor,
		autocommit=True,
	)


def fetch_tasks_by_hash(url_hash: str) -> List[Dict[str, Any]]:
	query = (
		"SELECT t.id, t.task_date AS taskDate, t.title, t.user_email AS userEmail "
		"FROM tasks t JOIN users u ON u.email = t.user_email WHERE u.url_hash = %s ORDER BY t.task_date ASC"
	)
	with get_conn() as conn:
		with conn.cursor() as cur:
			cur.execute(query, (url_hash,))
			return list(cur.fetchall())


def get_user_email_by_hash(url_hash: str) -> Optional[str]:
	with get_conn() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT email FROM users WHERE url_hash=%s", (url_hash,))
			row = cur.fetchone()
			return row["email"] if row else None


def create_task_for_hash(url_hash: str, title: str, task_date_iso: Optional[str]) -> Dict[str, Any]:
	# Resolve user email from hash
	email = get_user_email_by_hash(url_hash)
	if not email:
		raise HTTPException(status_code=404, detail="User not found for hash")
	# If date missing/invalid, default to today
	from datetime import datetime
	if not task_date_iso:
		task_date_iso = datetime.now().strftime("%Y-%m-%d")
	with get_conn() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO tasks (task_date, title, user_email) VALUES (%s, %s, %s)",
				(task_date_iso, title, email),
			)
			new_id = cur.lastrowid
			return {"id": new_id, "taskDate": task_date_iso, "title": title, "userEmail": email}


def update_task_title_or_date(task_id: int, title: Optional[str], task_date_iso: Optional[str], owner_hash: Optional[str]) -> Dict[str, Any]:
	# Optional ownership check by hash
	with get_conn() as conn:
		with conn.cursor() as cur:
			if owner_hash:
				cur.execute(
					"SELECT t.id FROM tasks t JOIN users u ON u.email=t.user_email WHERE t.id=%s AND u.url_hash=%s",
					(task_id, owner_hash),
				)
				if not cur.fetchone():
					raise HTTPException(status_code=403, detail="Task does not belong to user")
			# Build dynamic update
			sets = []
			args: List[Any] = []
			if title is not None and title != "":
				sets.append("title=%s")
				args.append(title)
			if task_date_iso is not None and task_date_iso != "":
				sets.append("task_date=%s")
				args.append(task_date_iso)
			if not sets:
				raise HTTPException(status_code=400, detail="Nothing to update")
			args.extend([task_id])
			cur.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=%s", args)
			cur.execute("SELECT id, task_date AS taskDate, title, user_email AS userEmail FROM tasks WHERE id=%s", (task_id,))
			row = cur.fetchone()
			if not row:
				raise HTTPException(status_code=404, detail="Task not found")
			return row


def delete_task_by_id(task_id: int, owner_hash: str) -> None:
	with get_conn() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"DELETE t FROM tasks t JOIN users u ON u.email=t.user_email WHERE t.id=%s AND u.url_hash=%s",
				(task_id, owner_hash),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Task not found or not owned by user")
  
# ----- In-memory chat history -----
HISTORY: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))

# ----- Models -----
class AskBody(BaseModel):
	query: str
	token: Optional[str] = Field(None, description="user hash for scoping and history")

class SummarizeBody(BaseModel):
	hash: Optional[str] = Field(None, description="user hash for scoping tasks")

class CreateBody(BaseModel):
	prompt: str
	hash: str

class UpdateBody(BaseModel):
	prompt: str
	hash: str

class DeleteBody(BaseModel):
	id: int
	hash: str

class RefineBody(BaseModel):
	prompt: str
	hash: Optional[str] = None

# ----- Utilities -----

def parse_date(text: str) -> Optional[str]:
	import re
	m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}|\d{4}[\-]\d{1,2}[\-]\d{1,2})", text)
	if not m:
		return None
	value = m.group(1)
	value = value.replace("/", "-")
	from datetime import datetime
	for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"):
		try:
			return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
		except Exception:
			continue
	return None


def strip_date_tokens(text: str, date_iso: Optional[str]) -> str:
	import re
	res = text
	if date_iso:
		res = re.sub(r"\b" + re.escape(date_iso) + r"\b", "", res).strip()
	res = re.sub(r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b", "", res).strip()
	return res


def clean_title_verbs(text: str) -> str:
	# Remove leading verbs like 'add', 'create', 'new', 'task', 'tasks'
	import re
	res = re.sub(r"^(?:\s*(add|create|new|task|tasks)\b)+\s*", "", text, flags=re.IGNORECASE)
	# Remove dangling prepositions at the end after date removal (e.g., 'at', 'on')
	res = re.sub(r"\b(at|on)\b\s*$", "", res, flags=re.IGNORECASE).strip()
	# Collapse multiple spaces
	res = re.sub(r"\s{2,}", " ", res).strip()
	return res


def find_task_id_by_title_fragment(url_hash: str, text: str) -> Optional[int]:
	text_l = text.lower()
	items = fetch_tasks_by_hash(url_hash)
	for t in items:
		title = str(t.get("title") or "").lower()
		if not title:
			continue
		if title in text_l or any(w and w in title for w in text_l.split()):
			return int(t["id"]) if t.get("id") is not None else None
	return None

# ----- LangChain-based extraction (optional) -----
def llm_extract_intent_and_fields(prompt: str) -> Optional[Dict[str, Any]]:
	model_name = os.getenv("LLM_MODEL")
	api_key = os.getenv("GOOGLE_API_KEY")
	if not api_key:
		return None
	try:
		# Import lazily so environments without langchain still work
		from langchain_core.prompts import ChatPromptTemplate
		from langchain_core.output_parsers import JsonOutputParser
		from langchain_core.pydantic_v1 import BaseModel as LCBaseModel, Field as LCField
		# Select a model provider based on available keys
		llm = None
		if os.getenv("GOOGLE_API_KEY"):
			from langchain_google_genai import ChatGoogleGenerativeAI
			llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash" or "gpt-4o-mini", temperature=0.3)

		class ExtractSchema(LCBaseModel):
			intent: str = LCField(description="one of: ask, create, update, delete, summarize")
			id: Optional[int] = LCField(default=None, description="task id if mentioned")
			title: Optional[str] = LCField(default=None, description="task title if present")
			date: Optional[str] = LCField(default=None, description="date in ISO YYYY-MM-DD if present")

		parser = JsonOutputParser(pydantic_object=ExtractSchema)
		prompt_t = ChatPromptTemplate.from_messages([
			("system", "You extract task intents and fields from natural language. Output strict JSON."),
			("user", "{input}\n\nReturn fields: intent,id,title,date. Date must be ISO YYYY-MM-DD if any."),
		])
		chain = prompt_t | llm | parser
		res = chain.invoke({"input": prompt})
		# Ensure minimal shape
		if not isinstance(res, dict) or "intent" not in res:
			return None
		return res
	except Exception:
		# Fail silent to fallback
		return None

def ask(body: AskBody):
	query = body.query.strip()
	if not query:
		raise HTTPException(status_code=400, detail="Empty query")
	h = (body.hash or "default").strip() or "default"
	conv = HISTORY[h]
	conv_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in list(conv)])
	items = fetch_tasks_by_hash(body.hash) if body.hash else []
	prompt = (
		(("Conversation so far:\n" + conv_text + "\n\n") if conv_text else "")
		+ "User question: " + query + "\n\n"
		+ "Relevant tasks JSON (may be empty):\n" + str(items)
	)
	# Here you could call an LLM; we return a simple heuristic answer
	answer = f"You have {len(items)} tasks. Ask me to 'summarize' or 'add ...' or 'update ...'."
	conv.append({"role": "user", "content": query})
	conv.append({"role": "assistant", "content": answer})
	return {"answer": answer}


@app.post("/summarize")
def summarize(body: SummarizeBody):
	from datetime import datetime
	items = fetch_tasks_by_hash(body.hash) if body.hash else []
	today = datetime.now().date()
	overdue: List[Dict[str, Any]] = []
	upcoming: List[Dict[str, Any]] = []
	for it in items:
		date_str = it.get("taskDate")
		try:
			d = datetime.strptime(str(date_str), "%Y-%m-%d").date() if date_str else None
		except Exception:
			d = None
		if not d:
			continue
		if d < today:
			overdue.append(it)
		else:
			upcoming.append(it)
	def brief(ts: List[Dict[str, Any]], limit: int = 5) -> str:
		lines: List[str] = []
		for it in ts[:limit]:
			lines.append(f"- {it.get('title')} ({it.get('taskDate')})")
		if len(ts) > limit:
			lines.append(f"- ... and {len(ts)-limit} more")
		return "\n".join(lines) if lines else "- None"
	return {
		"summary": "Overdue:\n" + brief(overdue) + "\n\nUpcoming:\n" + brief(upcoming),
		"overdueCount": len(overdue),
		"upcomingCount": len(upcoming),
		"total": len(items),
	}


@app.post("/create-task")
def create_task(body: CreateBody):
	if not body.hash:
		raise HTTPException(status_code=400, detail="hash required")
	# Try LLM extraction first
	extracted = llm_extract_intent_and_fields(body.prompt)
	if extracted and extracted.get("intent") in ("create", "add"):
		date_iso = extracted.get("date") or parse_date(body.prompt)
		title = extracted.get("title") or body.prompt.strip()
	else:
		# Fallback to regex utilities
		title = body.prompt.strip()
		date_iso = parse_date(title)
		if date_iso:
			title = strip_date_tokens(title, date_iso)
		title = clean_title_verbs(title)
	created = create_task_for_hash(body.hash, title, date_iso)
	return {"message": f"Created task: {created.get('title')}", "task": created}


@app.post("/update-task")
def update_task(body: UpdateBody):
	if not body.hash:
		raise HTTPException(status_code=400, detail="hash required")
	text = body.prompt.strip()
	import re
	# Try LLM extraction first
	extracted = llm_extract_intent_and_fields(text)
	if extracted and extracted.get("intent") == "update":
		task_id = extracted.get("id")
		new_title = extracted.get("title")
		date_iso = extracted.get("date") or parse_date(text)
		# If LLM did not return an id, try resolving by title within user's scope
		if not task_id:
			task_id = find_task_id_by_title_fragment(body.hash, text)
	else:
		# Fallback to regex utilities
		id_match = re.search(r"(?:#|\b(?:id|task)\b\s*)(\d{1,10})\b", text, re.IGNORECASE)
		task_id: Optional[int] = int(id_match.group(1)) if id_match else None
		if not task_id:
			task_id = find_task_id_by_title_fragment(body.hash, text)
		date_iso = parse_date(text)
		new_title: Optional[str] = None
		m_to = re.search(r"\bto\s*(.+)$", text, re.IGNORECASE)
		if m_to:
			new_title = m_to.group(1).strip()
		else:
			m_as = re.search(r"\bas\s+(.+)$", text, re.IGNORECASE)
			if m_as:
				new_title = m_as.group(1).strip()
			else:
				m_title = re.search(r"\btitle\s+(.+)$", text, re.IGNORECASE)
				if m_title:
					new_title = m_title.group(1).strip()
	# Ensure we have an id before proceeding
	if not task_id:
		raise HTTPException(status_code=400, detail="Could not identify a task to update")
	if new_title:
		new_title = strip_date_tokens(new_title, date_iso)
	if (not new_title or new_title == "") and (not date_iso or date_iso == ""):
		raise HTTPException(status_code=400, detail="Nothing to update. Provide a new title (e.g., 'to <new title>') or a date.")
	row = update_task_title_or_date(task_id, new_title, date_iso, owner_hash=body.hash)
	return {"message": f"Updated task {task_id}", "task": row}


@app.post("/delete-task")
def delete_task(body: DeleteBody):
	if not body.hash:
		raise HTTPException(status_code=400, detail="hash required")
	delete_task_by_id(body.id, body.hash)
	return {"message": f"Deleted task {body.id}"}


@app.get("/history/{hash}")
def get_history(hash: str):
	return {"messages": list(HISTORY[(hash or 'default').strip() or 'default'])}


@app.post("/refine")
def refine(body: RefineBody):
	text = (body.prompt or "").strip()
	if not text:
		raise HTTPException(status_code=400, detail="Empty prompt")
	import re
	extracted = llm_extract_intent_and_fields(text)
	if extracted:
		# Normalize and guarantee ISO date fallback
		extracted["date"] = extracted.get("date") or parse_date(text)
		return extracted
	# Fallback regex heuristics
	lower = text.lower()
	intent: str = "ask"
	if any(k in lower for k in ["summarize", "summary"]):
		intent = "summarize"
	elif any(k in lower.split() for k in ["add", "create", "new"]):
		intent = "create"
	elif any(k in lower.split() for k in ["delete", "remove", "del"]):
		intent = "delete"
	elif any(k in lower.split() for k in ["update", "mark", "rename", "change"]):
		intent = "update"
	date_iso = parse_date(text)
	id_match = re.search(r"(?:#|\b(?:id|task)\b\s*)(\d{1,10})\b", text, re.IGNORECASE)
	ref_id: Optional[int] = int(id_match.group(1)) if id_match else None
	new_title: Optional[str] = None
	if intent == "create":
		raw = strip_date_tokens(text, date_iso)
		raw = re.sub(r"\b(add|create|new|task|tasks)\b", "", raw, flags=re.IGNORECASE).strip()
		raw = re.sub(r"\b(at|on)\b\s*$", "", raw, flags=re.IGNORECASE).strip()
		title = re.sub(r"\s{2,}", " ", raw).strip()
		return {"intent": intent, "title": title, "date": date_iso}
	elif intent == "update":
		m_to = re.search(r"\bto\s*(.+)$", text, re.IGNORECASE)
		if m_to:
			new_title = strip_date_tokens(m_to.group(1).strip(), date_iso)
		else:
			m_as = re.search(r"\bas\s+(.+)$", text, re.IGNORECASE)
			if m_as:
				new_title = strip_date_tokens(m_as.group(1).strip(), date_iso)
		return {"intent": intent, "id": ref_id, "title": new_title, "date": date_iso}
	elif intent == "delete":
		return {"intent": intent, "id": ref_id}
	elif intent == "summarize":
		return {"intent": intent, "hash": body.hash}
	return {"intent": intent}
