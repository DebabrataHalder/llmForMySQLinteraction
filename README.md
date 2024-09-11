## Project Overview

This project is a **Streamlit-based chat application** that allows users to interact with a **MySQL database** using **natural language queries**. The application uses the **LangChain** library to build a chain of prompts that converts user queries into SQL commands and executes them on the database. It then generates natural language responses based on the SQL query results.

### Key Features:
- **MySQL Database Connection:** Users can input their database credentials (host, port, user, password, and database name) to establish a connection.
- **Natural Language Queries:** Users can ask questions about their database schema and data using natural language, and the system automatically generates SQL queries to answer those questions.
- **AI-Powered Responses:** Using models like **ChatGroq**, the application processes the database responses and presents them as natural language answers.
- **Persistent Chat History:** The chat interface keeps track of the conversation history, enabling context-aware interactions.
- **Dynamic SQL Query Generation:** SQL queries are generated based on the conversation history and the database schema, ensuring accurate results.

### Libraries Used:
- **LangChain** for building the prompt and handling interactions between the user and the database.
- **SQLDatabase** for connecting and executing SQL queries.
- **Streamlit** for the web interface.
- **ChatGroq** for large language model (LLM)-based processing of user inputs and database results.

---

## How to Use

1. **Connect to the Database:** Enter the database connection details (host, port, username, password, and database name) in the sidebar and click "Connect".
2. **Ask Questions:** Once connected, start typing your questions about the database. The application will automatically generate and execute the relevant SQL query and return the results in natural language.
3. **Model Selection:** Choose an AI model from the sidebar to generate responses.
4. **View Responses:** The conversation history, including the user’s questions and the AI's responses, will be displayed in the chat interface.

