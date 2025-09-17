import os
from typing import Any, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI


_llm_instance: Optional[ChatGoogleGenerativeAI] = None


def get_llm() -> ChatGoogleGenerativeAI:
	global _llm_instance
	if _llm_instance is None:
		_llm_instance = ChatGoogleGenerativeAI(
			model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
			google_api_key=os.getenv("GOOGLE_API_KEY"),
		)
	return _llm_instance


def ask_model(prompt: str) -> str:
	llm = get_llm()
	resp = llm.invoke(prompt)
	return getattr(resp, "content", str(resp))


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
	import json
	try:
		return json.loads(text)
	except Exception:
		start = text.find("{")
		end = text.rfind("}")
		if start != -1 and end != -1 and end > start:
			candidate = text[start:end+1]
			try:
				return json.loads(candidate)
			except Exception:
				return None
	return None
