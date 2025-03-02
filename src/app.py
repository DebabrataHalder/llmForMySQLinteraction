from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import streamlit as st


def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    try:
        db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        return SQLDatabase.from_uri(db_uri)
    except Exception as e:
        raise ConnectionError(f"Could not connect to the database: {str(e)}")


def get_sql_chain(db, model_name):
    try:
        template = """
            You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
            Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
            
            <SCHEMA>{schema}</SCHEMA>
            
            Conversation History: {chat_history}
            
            Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
            
            For example:
            Question: which 3 artists have the most tracks?
            SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
            Question: Name 10 artists
            SQL Query: SELECT Name FROM Artist LIMIT 10;
            
            Your turn:
            
            Question: {question}
            SQL Query:
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        llm = ChatGroq(model=model_name, temperature=0)
        
        def get_schema(_):
            return db.get_table_info()
        
        return (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
        )
    except Exception as e:
        raise RuntimeError(f"Error initializing the SQL chain: {str(e)}")


def get_response(user_query: str, db: SQLDatabase, chat_history: list, model_name: str):
    try:
        sql_chain = get_sql_chain(db, model_name)
        
        template = """
            You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
            Based on the table schema below, question, sql query, and sql response, write a natural language response.
            <SCHEMA>{schema}</SCHEMA>

            Conversation History: {chat_history}
            SQL Query: <SQL>{query}</SQL>
            User question: {question}
            SQL Response: {response}"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        llm = ChatGroq(model=model_name, temperature=0)
        
        chain = (
            RunnablePassthrough.assign(query=sql_chain).assign(
                schema=lambda _: db.get_table_info(),
                response=lambda vars: db.run(vars["query"]),
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain.invoke({
            "question": user_query,
            "chat_history": chat_history,
        })
    
    except ConnectionError as db_error:
        return f"""
        Oops! An error occurred while connecting to the database:

        **Error:** {str(db_error)}
        
        Please check your database credentials and try again.
        """
    except ValueError as api_key_error:
        return f"""
        Oops! An error occurred while connecting to the LLM API:

        **Error:** {str(api_key_error)}

        Ensure that your API key is set in the environment variables or provided as a parameter.
        """
    except Exception as e:
        return f"""
        Oops! An unexpected error occurred:

        **Error:** {str(e)}
        
        Please contact support or try again later.
        """


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]

# Load environment variables
load_dotenv()

# Set Streamlit configuration
st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")
st.title("Chat with MySQL")

# Sidebar for database connection settings
with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    st.text_input("Host", value="sql12.freesqldatabase.com", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="sql12765508", key="User")
    st.text_input("Password", type="password", value="YuF15SFqm4", key="Password")
    st.text_input("Database", value="sql12765508", key="Database")
    
    model_name = st.selectbox(
        "Select Model", 
        # options=["llama-3.1-70b-versatile", "mixtral-8x7b-32768","gemma2-9b-it"],
        # index=0
        options=["llama-3.3-70b-versatile","gemma2-9b-it"],
        index=0
    )
    
    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            try:
                db = init_database(
                    st.session_state["User"],
                    st.session_state["Password"],
                    st.session_state["Host"],
                    st.session_state["Port"],
                    st.session_state["Database"]
                )
                st.session_state.db = db
                st.session_state.model_name = model_name
                st.success("Connected to database!")
            except Exception as e:
                st.error(f"Failed to connect to database: {str(e)}")

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

# User input for chat
user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
    
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history, st.session_state.model_name)
        
        # Display response or error message gracefully
        if "Oops! An error occurred" in response:
            st.error(response)
        else:
            st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))




        
#     with st.chat_message("AI"):
#         response = get_response(user_query, st.session_state.db, st.session_state.chat_history, st.session_state.model_name)
#         st.markdown(response)
        
#     st.session_state.chat_history.append(AIMessage(content=response))
