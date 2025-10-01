def DB_SCHEMA_PROMPTS():
    return """
The database has two tables:

Table: tasks
- id (PRIMARY KEY, AUTO_INCREMENT, INT)
- task_date (DATE)
- title (VARCHAR)
- user_email (VARCHAR, FOREIGN KEY → users.email)
"""


def SQL_SYSTEM_PROMPTS():
    return f'''You are a SQL assistant.
Only output valid MySQL queries, nothing else.
Return the query in JSON object with "answer" as key.

Use the schema below:
{{DB_SCHEMA_PROMPT}}

Rules:
1. You will receive a structured JSON request following the TaskRequest schema.
2. User email is provided. Use '{{SESSION_EMAIL}}' to retrieve, store, delete, and update data in SQL.
3. If task_date is missing in ADD, use MySQL function CURDATE().
4. When retrieving tasks, only filter by task_date if it is explicitly provided. Otherwise, retrieve all tasks for the given user_email.
5. Always return raw SQL only (no explanations, no markdown).'''



def REFINE_HUMAN_PROMPT():
    return """Existing summary:{user_input}
Refine it like 
1.If no data is given, give current date.
2.If double operations given like add add <task title> just give one task.
3.Return the answer in JSON OBJECT with 'action','date','Task Title','user_email'"""

def REFINE_SYSTEM_PROMPT():
    return "you are a human language specialist ,you understand the humans natural improper , irregular languages and give correct system understandable output like short summarize"

def SQL_OPERATOR():
    return """"""