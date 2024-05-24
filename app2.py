# main_app.py
import streamlit as st
import pandas as pd
import azuresql_new
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
import re


def query_database(query, conn):
    """Run SQL query and return results in a dataframe"""
    return pd.read_sql(query, conn)

# Function to extract JSON from mixed response
def extract_json_from_response(response):
    try:
        # Use a regular expression to find the JSON part
        json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
        return json.loads(json_str)
    except (AttributeError, json.JSONDecodeError) as e:
        st.write(f"An error occurred while extracting JSON: {e}")
        return None

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

    # Extract JSON from the response
    json_response = extract_json_from_response(response)

    if json_response:
        query = json_response.get('query', '')

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
