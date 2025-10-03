import os
from dotenv import load_dotenv

from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from prompts import REFINE_SYSTEM_PROMPT , REFINE_HUMAN_PROMPT , SQL_SYSTEM_PROMPTS , DB_SCHEMA_PROMPTS , FINAL_OUTPUT
################### IMPORTS #####################
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

DB_URL = "mysql+mysqlconnector://root:Sujith%406212@localhost:3306/knot"
db = SQLDatabase.from_uri(DB_URL)

################### FUNCTIONS ####################

async def refine_user_input(user_input: str):
    refine_prompt_template = ChatPromptTemplate([
        SystemMessagePromptTemplate.from_template(REFINE_SYSTEM_PROMPT()),
        HumanMessagePromptTemplate.from_template(REFINE_HUMAN_PROMPT())
    ])
    
    request = RunnablePassthrough() | refine_prompt_template | llm_model | StrOutputParser()
    response = await request.ainvoke({"user_input": user_input})
    return response

async def sql_generator(refined_input: str, session_email: str):
    MAIN_PROMPT = (ChatPromptTemplate.from_messages([
                    ("system", SQL_SYSTEM_PROMPTS()),
                    ("human", "{refined_input}")
                  ])
                  .partial(DB_SCHEMA_PROMPT=DB_SCHEMA_PROMPTS(), SESSION_EMAIL=session_email, refined_input=refined_input))
    
    chain = MAIN_PROMPT | llm_model | JsonOutputParser()
    request = await chain.ainvoke({"refined_input": refined_input})
    return request

def sql_run(sql_query: str):
    return db.run(sql_query)

async def final_output(question: str, schema: str, query: dict, response: str):
    MAIN_PROMPT = ChatPromptTemplate.from_template(FINAL_OUTPUT())
    chain = MAIN_PROMPT | llm_model | StrOutputParser()
    request = await chain.ainvoke({
        "question": question,
        "schema": schema,
        "query": query,
        "response": response
    })
    return {"answer": request}

# ----- Conversational memory using RunnableWithMessageHistory -----
message_histories = {}

def get_history(session_email: str):
    if session_email not in message_histories:
        message_histories[session_email] = InMemoryChatMessageHistory()
    return message_histories[session_email]

def clear_user_memory(session_email: str):
    if session_email in message_histories:
        del message_histories[session_email]

def get_conversation_chain_with_history():
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    base_chain = prompt | llm_model
    return RunnableWithMessageHistory(
        base_chain,
        get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


################### MAIN ####################


async def main(user_input: str, session_email: str):   
    # store refined input in memory and run SQL workflow
    refined_input = await refine_user_input(user_input)
    sql_query_result = await sql_generator(refined_input, session_email)
    sql_execution = sql_run(sql_query_result["answer"])
    
    final_resp = await final_output(
        refined_input,
        DB_SCHEMA_PROMPTS(),
        sql_query_result,
        sql_execution
    )
    # Append the refined input to the conversational history (replaces ConversationChain)
    conversation = get_conversation_chain_with_history()
    await conversation.ainvoke(
        {"input": refined_input},
        config={"configurable": {"session_id": session_email}},
    )
    return final_resp