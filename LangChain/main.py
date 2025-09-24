import os
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ----- Config -----
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Sujith@6212")
MYSQL_DB = os.getenv("MYSQL_DB", "knot")

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
		host=MYSQL_HOST,
		port=MYSQL_PORT,
		user=MYSQL_USER,
		password=MYSQL_PASSWORD,
		database=MYSQL_DB,
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
	hash: Optional[str] = Field(None, description="user hash for scoping and history")

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

# ----- Endpoints -----
@app.post("/ask")
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
	title = body.prompt.strip()
	# If prompt contains a date, split title and date
	date_iso = parse_date(title)
	if date_iso:
		# remove a matching date token from title for cleanliness (both iso and common dd/mm/yyyy)
		import re
		title = re.sub(r"\b" + re.escape(date_iso) + r"\b", "", title).strip()
		title = re.sub(r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b", "", title).strip()
	created = create_task_for_hash(body.hash, title, date_iso)
	return {"message": f"Created task: {created.get('title')}", "task": created}


@app.post("/update-task")
def update_task(body: UpdateBody):
	if not body.hash:
		raise HTTPException(status_code=400, detail="hash required")
	text = body.prompt.strip()
	# Try to extract id first
	import re
	m = re.search(r"\b(\d{1,10})\b", text)
	task_id: Optional[int] = int(m.group(1)) if m else None
	if not task_id:
		task_id = find_task_id_by_title_fragment(body.hash, text)
	if not task_id:
		raise HTTPException(status_code=400, detail="Could not identify a task to update")
	# Find new title and/or date in the text
	date_iso = parse_date(text)
	new_title: Optional[str] = None
	# naive patterns: 'to XYZ' or 'as XYZ' or 'title XYZ'
	m2 = re.search(r"\bto\s+(.+)$", text, re.IGNORECASE)
	if m2:
		new_title = m2.group(1).strip()
	if not new_title:
		m3 = re.search(r"\bas\s+(.+)$", text, re.IGNORECASE)
		if m3:
			new_title = m3.group(1).strip()
	if not new_title:
		m4 = re.search(r"\btitle\s+(.+)$", text, re.IGNORECASE)
		if m4:
			new_title = m4.group(1).strip()
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
