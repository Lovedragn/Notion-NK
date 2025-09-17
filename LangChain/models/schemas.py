from typing import Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
	query: str = Field(..., description="Natural language question about tasks")
	userId: Optional[int] = Field(None, description="Optional user id to scope data fetch")
	token: Optional[str] = Field(None, description="Optional JWT to call Spring Boot")


class SummarizeRequest(BaseModel):
	userId: Optional[int] = None
	token: Optional[str] = None


class CreateTaskRequest(BaseModel):
	prompt: str = Field(..., description="Natural language like 'Add a meeting tomorrow 3pm'")
	userId: Optional[int] = None
	hash: Optional[str] = Field(None, description="Optional hashed user URL for creation endpoint")
	token: Optional[str] = None


class UpdateTaskRequest(BaseModel):
	prompt: str = Field(..., description="Natural language like 'Mark task 5 completed'")
	userId: Optional[int] = None
	token: Optional[str] = None
