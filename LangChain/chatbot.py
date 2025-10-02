import os
import json
from dotenv import load_dotenv

from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pydantic import Field, BaseModel
from langchain_core.output_parsers import StrOutputParser , JsonOutputParser
from langchain_core.runnables import RunnablePassthrough


from prompts import DB_SCHEMA_PROMPTS, SQL_SYSTEM_PROMPTS, REFINE_HUMAN_PROMPT, REFINE_SYSTEM_PROMPT ,FINAL_OUTPUT

################### IMPORTS ######################

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

DB_URL = "mysql+mysqlconnector://root:Sujith%406212@localhost:3306/knot"
db = SQLDatabase.from_uri(DB_URL)

################## Connections  ####################

async def main(user_input: str, session_email: str ):
    refine_input = await refine_user_input(user_input)
    sql_query = sql_generator(refine_input, session_email)
    sql_execution = sql_run(sql_query["answer"])
    finalized_output = await final_output(refine_input,DB_SCHEMA_PROMPTS(),sql_query,sql_execution)
        
    return finalized_output


async def refine_user_input(user_input:str):
    refine_prompt_templete = ChatPromptTemplate([SystemMessagePromptTemplate.from_template(REFINE_SYSTEM_PROMPT()),
                                                 HumanMessagePromptTemplate.from_template(REFINE_HUMAN_PROMPT())])

    request = RunnablePassthrough() | refine_prompt_templete | llm_model | StrOutputParser()
    response = await request.ainvoke({"user_input" : user_input})
    print(response)
    return  response


def sql_generator(refine_user_input: str, SESSION_EMAIL: str):

    MAIN_PROMPT = (ChatPromptTemplate.from_messages([("system", SQL_SYSTEM_PROMPTS()),
                                                     ("human", "{refine_user_input}")])
                   .partial(DB_SCHEMA_PROMPT=DB_SCHEMA_PROMPTS(), SESSION_EMAIL=SESSION_EMAIL,refine_user_input= refine_user_input))

    chain = MAIN_PROMPT | llm_model | JsonOutputParser()
    request = chain.invoke({"refine_user_input": refine_user_input})
    print(request)
    return request

def sql_run(sql_query:str):
    res = db.run(sql_query)
    return res

async def final_output(question: str, schema: str,query:str, response: str):
    MAIN_PROMPT = ChatPromptTemplate.from_template(FINAL_OUTPUT())
    chain = MAIN_PROMPT | llm_model | StrOutputParser()

    request = await chain.ainvoke({
        "question": question,
        "schema": schema,
        "query":query,
        "response": response
    })
    return {"answer":request}

