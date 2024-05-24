# sql_db.py

import pyodbc
import random
from datetime import date, timedelta
import pandas as pd

# Replace with your Azure SQL Database connection string
CONNECTION_STRING = ("Driver={ODBC Driver 18 for SQL Server};Server=tcp:aipocsqlser.database.windows.net,1433;Database=testaipocsqldatabase;Uid=userop;Pwd=Independent12#;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

def create_connection():
    """Create or connect to an Azure SQL Database"""
    conn = None
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
    except pyodbc.Error as e:
        print("Error connecting to database:", e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table with the specified SQL command"""
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
    except pyodbc.Error as e:
        print("Error creating table:", e)

def insert_data(conn, table_name, data_dict):
    """Insert new data into a table"""
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join('?' * len(data_dict))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor = conn.cursor()
    cursor.execute(sql, list(data_dict.values()))
    conn.commit()

def query_database(query):
    """Run SQL query and return results in a dataframe"""
    conn = create_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def setup_financial_table():
    conn = create_connection()
    if conn is not None:
        # Check if table exists, create if it does not
        sql_check_table = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'finances')
        BEGIN
            CREATE TABLE finances (
                id INT PRIMARY KEY IDENTITY(1,1),
                date DATE NOT NULL,
                revenue FLOAT NOT NULL,
                expenses FLOAT NOT NULL,
                profit FLOAT NOT NULL
            );
        END;
        """
        create_table(conn, sql_check_table)

        # Insert 100 rows with random data
        start_date = date.today() - timedelta(days=99)
        for i in range(100):
            revenue = random.randint(5000, 20000)  # Random revenue between 5000 and 20000
            expenses = random.randint(1000, 15000)  # Random expenses between 1000 and 15000
            profit = revenue - expenses
            data = {
                "date": start_date + timedelta(days=i),
                "revenue": revenue,
                "expenses": expenses,
                "profit": profit
            }
            insert_data(conn, "finances", data)

        conn.close()
    else:
        print("Connection to database failed. Table setup aborted.")

def get_schema_representation():
    """Get the database schema in a JSON-like format"""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()

        # Query to get all table names
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE';")
        tables = cursor.fetchall()

        db_schema = {}

        for table in tables:
            table_name = table[0]

            # Query to get column details for each table
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = cursor.fetchall()

            column_details = {}
            for column in columns:
                column_name = column[0]
                column_type = column[1]
                column_details[column_name] = column_type

            db_schema[table_name] = column_details

        conn.close()
        return db_schema
    else:
        print("Connection to database failed. Schema retrieval aborted.")
        return {}

# This will create the table and insert 100 rows when you run sql_db.py
if __name__ == "__main__":
    setup_financial_table()
    print(get_schema_representation())
