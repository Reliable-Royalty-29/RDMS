# main_app.py

import streamlit as st
import pyodbc
import pandas as pd
import azuresql_new  # Make sure this is the correct import based on your file name
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://aipoctesting.openai.azure.com/"
openai.api_version = "2023-10-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion_from_messages(system_message, user_message, model="gpt-35-turbo", temperature=0, max_tokens=500) -> str:

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{user_message}"}
    ]
    
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    
    return response.choices[0].message["content"]

if __name__ == "__main__":
    system_message = "You are a helpful assistant"
    user_message = "Hello, how are you?"
    print(get_completion_from_messages(system_message, user_message))
def query_database(query, conn):
    """Run SQL query and return results in a dataframe"""
    return pd.read_sql(query, conn)

# Create or connect to Azure SQL Database
conn = azuresql_new.create_connection()

# Schema Representation for finances table
schemas = azuresql_new.get_schema_representation()

st.title("SQL Query Generator with GPT-4")
st.write("Enter your message to generate SQL and view results.")

# Input field for the user to type a message
user_message = st.text_input("Enter your message:")

if user_message:
    # Format the system message with the schema
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['finances'])

    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)

    # Debugging: Print the response to check its content
    st.write("API Response:")
    st.write(response)

    try:
        json_response = json.loads(response)
        query = json_response['query']

        # Display the generated SQL query
        st.write("Generated SQL Query:")
        st.code(query, language="sql")

        try:
            # Run the SQL query and display the results
            sql_results = query_database(query, conn)
            st.write("Query Results:")
            st.dataframe(sql_results)

        except Exception as e:
            st.write(f"An error occurred while querying the database: {e}")

    except json.JSONDecodeError as e:
        st.write(f"An error occurred while decoding the JSON response: {e}")
        st.write("Response content:")
        st.write(response)

