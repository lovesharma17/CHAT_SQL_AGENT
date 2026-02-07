import streamlit as st
from pathlib import Path
import os
from langchain_classic.sql_database import SQLDatabase 
from langchain_classic.agents.agent_types import AgentType
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.callbacks import StreamlitCallbackHandler
from langchain_classic.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_classic.agents import AgentExecutor
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Langchain: Chat with SQL DB" , page_icon="🕊")
st.title("🕊 Langchain : Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio__opt = ["Use Sqlite3 Database - Student.db" , "Connect to your SQL Database"]

selected_opt = st.sidebar.radio(label="choose the Db which you want to chat" , options=radio__opt)
if radio__opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide My SQL Host")
    mysql_user= st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MYSQL password" , type="password")
    mysql_db = st.sidebar.text_input("MySQL database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API key" , type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the groq api key")

## LLM model
llm =ChatGroq( model_name = "llama-3.1-8b-instant" , streaming=False)


@st.cache_resource(ttl="2h")
def configure_db(db_uri , mysql_host=None , mysql_user=None , mysql_password = None , mysql_db = None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro" , uri=True)
        return SQLDatabase(create_engine("sqlite:///" , creator=creator))

    elif db_uri==MYSQL:
        if not (mysql_db and mysql_host and mysql_password and mysql_user):
            st.error("Please provide all MYSQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector:// {mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri==MYSQL:
    db = configure_db(db_uri , mysql_host , mysql_user , mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

callback = StreamlitCallbackHandler(st.container())



system_prompt = """IMPORTANT:
- You are a helpful SQL assistant
- After you get the SQL result, you MUST respond with a Final Answer.
- Do NOT continue thinking after the SQL query is executed.
- Summarize the result in plain English.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt = prompt,
    max_iterations=10,
    handle_parsing_errors=True,
    callbacks=[callback],
)



if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"assistant" , "content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    with st.chat_message("assistant"):
        response = agent_executor.invoke({"input": user_query})
        final_answer = response["output"]

        st.session_state.messages.append(
            {"role": "assistant", "content": final_answer}
        )

        st.write(final_answer)
