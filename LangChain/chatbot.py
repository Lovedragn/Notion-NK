import os
from dotenv import load_dotenv
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import ChatPromptTemplate
from pydantic import Field, BaseModel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from prompts import DB_SCHEMA_PROMPTS, SQL_SYSTEM_PROMPTS, REFINE_HUMAN_PROMPT, REFINE_SYSTEM_PROMPT

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

async def test(user_input:str):
    res = llm_model.invoke(user_input)
    return res.content

async def main(user_input: str, session_email: str):
    refine_input = await refine_user_input(user_input)
    sql_query = sql_generator(refine_input, session_email)
    return sql_query


async def refine_user_input(user_input:str):
    refine_prompt_templete = ChatPromptTemplate([SystemMessagePromptTemplate.from_template(REFINE_SYSTEM_PROMPT()),
                                                 HumanMessagePromptTemplate.from_template(REFINE_HUMAN_PROMPT())])

    request = RunnablePassthrough() | refine_prompt_templete | llm_model | StrOutputParser()
    response = await request.ainvoke({"user_input" : user_input})
    return  response


def sql_generator(refine_user_input: str, SESSION_EMAIL: str):

    MAIN_PROMPT = (ChatPromptTemplate.from_messages([("system", SQL_SYSTEM_PROMPTS()),
                                                     ("human", "{refine_user_input}")])
                   .partial(DB_SCHEMA_PROMPT=DB_SCHEMA_PROMPTS(), SESSION_EMAIL=SESSION_EMAIL))

    chain = MAIN_PROMPT | llm_model

    request = chain.invoke({"refine_user_input": refine_user_input})
    return request.content

def sql_execution(sql_query:str):
    from langchain_community.utilities import SQLDatabase
    DB_URL = "mysql+mysqlconnector://root:Sujith@6212@localhost:3306/knot"
    # DB_URL = "mysql+mysqlconnector://root:Sujith%406212@localhost:3306/knot"
    db = SQLDatabase.from_uri(DB_URL)
    db.run(sql_query)


    