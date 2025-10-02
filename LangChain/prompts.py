def DB_SCHEMA_PROMPTS():
    return """tasks:
- id (PRIMARY KEY, AUTO_INCREMENT, INT)
- task_date (DATE)
- title (VARCHAR)
- user_email (VARCHAR, FOREIGN KEY -> users.email)
"""


def SQL_SYSTEM_PROMPTS():
    return """You are a SQL assistant.
Return the query in JSON object with "answer" as key.
Use the schema below:
{DB_SCHEMA_PROMPT}
Rules:
1. User email is provided. Use '{SESSION_EMAIL}' to retrieve, store, delete, and update data in SQL.
2. When retrieving tasks, only filter by user_email if it is explicitly provided. Otherwise, retrieve all tasks for the given title.
3. Always return raw SQL only (no explanations, no markdown)."""


def REFINE_HUMAN_PROMPT():
    return """Existing summary:{user_input}"""

def REFINE_SYSTEM_PROMPT():
    return """you are a human language specialist ,
you understand the humans natural improper , irregular languages and give correct system understandable output like short summarize. 
Refine it like: 
1.If no date is given for creating a new task,then only use MySQL function CURDATE() to autoassign the todays date.
'"""

def FINAL_OUTPUT():
    return  """Based on the question , table schema, sql query , sql query response , write a short natural language response :
{question}
{schema}
{query}
{response}
"""