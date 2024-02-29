import streamlit as st
import re
import json
import os
import pathlib

st.set_page_config(
    page_title="Scanning MR",
    page_icon="👋",
)
st.title("Scanning MR")

def load_sensitive_data_config(config_file):
    #with open(config_file, 'r') as f:
    config = json.load(config_file)
    return {field.lower() for field in config['sensitive_fields']}

def load_approved_sensitive_fields(approved_config_file):
    #with open(approved_config_file, 'r') as f:
    config = json.load(approved_config_file)
    return {field.lower() for field in config['approved_sensitive_fields']}

def categorize_queries(query_results):
    approved_sensitive_queries = []
    unsafe_queries = []
    safe_queries = []
    not_allowed_queries = []

    for filename, query_result, query in query_results:
        if query_result == "APPROVED_SENSITIVE_FIELD_FOUND":
            approved_sensitive_queries.append((filename, query_result, query))
        elif query_result in ["SENSITIVE_FIELD_FOUND", "SELECT_ALL_DATA_FOUND", "SELECT_ALL_FIELDS_FOUND"]:
            unsafe_queries.append((filename, query_result, query))
        elif query_result == "SAFE_QUERY":
            safe_queries.append((filename, query_result, query))
        elif query_result == "NOT_ALLOWED_STATEMENT":
            not_allowed_queries.append((filename, query_result, query))

    return approved_sensitive_queries, unsafe_queries, safe_queries, not_allowed_queries

def validate_queries_in_folder(sensitive_fields, approved_sensitive_fields, queries):
   
    # Get a list of query files in the specified folder
    query_results = []
   
    # Display queries with approved sensitive fields
    for query in queries:
        #st.write(query)
        qur = query[0]
        qur_fileName = query[1]
       # st.write(qur)
       # st.write(qur_fileName)
        if qur:
            query_result = is_sensitive_query(qur, sensitive_fields, approved_sensitive_fields)
            query_results.append((qur_fileName, query_result, query))

    approved_sensitive_queries, unsafe_queries, safe_queries, not_allowed_queries = categorize_queries(query_results)

    # Display queries with approved sensitive fields
    st.text("Queries with Approved Sensitive Fields:")
    st.text(f"{'Filename':<30} {'Query Result':<30} {'Query'}")
    for filename, query_result, query in approved_sensitive_queries:
        st.text(f"{filename:<30} {query_result:<30} {query}")

    # Display unsafe queries
    st.text("\nUnsafe Queries:")
    st.text(f"{'Filename':<30} {'Query Result':<30} {'Query'}")
    for filename, query_result, query in unsafe_queries:
        st.text(f"{filename:<30} {query_result:<30} {query}")

    # Display safe queries
    st.text("\nSafe Queries:")
    st.text(f"{'Filename':<30} {'Query Result':<30} {'Query'}")
    for filename, query_result, query in safe_queries:
        st.text(f"{filename:<30} {query_result:<30} {query}")

    # Display not allowed queries
    st.text("\nNot Allowed SQL Statements:")
    st.text(f"{'Filename':<30} {'Query Result':<30} {'Query'}")
    for filename, query_result, query in not_allowed_queries:
        st.text(f"{filename:<30} {query_result:<30} {query}")

    # Display a listing of all queries
    st.text("\nListing of All Queries:")
    st.text(f"{'Filename':<30} {'Query Result':<30} {'Query'}")
    for filename, query_result, query in query_results:
        st.text(f"{filename:<30} {query_result:<30} {query}")
    

def is_sensitive_query(query, sensitive_fields, approved_sensitive_fields):
    normalized_query = query.lower()

    # Check if any sensitive field is referenced in the query
    for field in sensitive_fields:
        if field in normalized_query:
            # Check if it's an approved sensitive field
            if field in approved_sensitive_fields:
                return "APPROVED_SENSITIVE_FIELD_FOUND"
            else:
                return "SENSITIVE_FIELD_FOUND"

    # Check if the query contains "SELECT *"
    if "select *" in normalized_query:
        return "SELECT_ALL_FIELDS_FOUND"

    # Check if the query contains "SELECT" without specifying columns and lacks a "WHERE" clause
    if "select " in normalized_query and "from " in normalized_query and " where " not in normalized_query:
        return "SELECT_ALL_DATA_FOUND"

    # Check if the query is not a SELECT statement
    if not normalized_query.startswith("select "):
        return "NOT_ALLOWED_STATEMENT"

    # If none of the above conditions are met, the query is safe
    return "SAFE_QUERY"

def initLayout():
    sql_files = []
    sensitive_fields=[]
    approved_sensitive_fields=[]
    queries = []
    FILE_TYPES = ["json","sql"]
    uploaded_files = st.file_uploader("Choose 2 json files approved_sensitive_fields.json and sensitive_fields.json. Then choose the rest of the sql files you need to scan", type=FILE_TYPES,accept_multiple_files=True)
    for uploaded_file in uploaded_files:
       if uploaded_file.name == 'sensitive_fields.json' :
        sensitive_fields = load_sensitive_data_config(uploaded_file)
       elif uploaded_file.name == 'approved_sensitive_fields.json':
        approved_sensitive_fields = load_approved_sensitive_fields(uploaded_file)
       elif pathlib.Path(uploaded_file.name).suffix == '.sql':
           sql_files.append(uploaded_file)
           data_string = uploaded_file.read()
           str_sql = bytes.decode(data_string)
           str_sql_str = str_sql.split(';')
           for str_sql_str_str in str_sql_str:
               #st.text(str_sql_str_str)
               queries.append((str_sql_str_str,uploaded_file.name))

           
	
    if len(sensitive_fields) > 0 and len(approved_sensitive_fields) > 0 and len(queries) > 0 :
        st.text("Approved Sensitive Fields:")
        st.write(approved_sensitive_fields)
        st.text("Sensitive Fields:")
        st.write(sensitive_fields)
        validate_queries_in_folder(sensitive_fields,approved_sensitive_fields,queries)
        #st.write(queries[0][1])
        #st.text("Approved Sensitive Fields:")
        #st.write(approved_sensitive_fields)
        #st.text("Sensitive Fields:")
        #st.write(sensitive_fields)
        #st.write(sql_files)
	


initLayout()
		
