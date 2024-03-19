import streamlit as st
import re
import json
import os
import pathlib
import io
import sqlglot
from sqlglot import parse_one, exp


st.set_page_config(
    page_title="Scanning MR",
    page_icon="👋",
)
st.title("Scanning MR")

def validateInput():
    sqlstr = st.session_state['sqlQueryScan']
    if sqlstr == "" or sqlstr == None:
        st.error ("No sql queries input",icon="🚨")
        return False
    
    approvedfields = st.session_state['approvedFieldScan']
    if approvedfields == "" or approvedfields == None:
        st.error("No log to tally",icon="🚨")
        return False
    
    sensFields = st.session_state['sensitiveFields']
    if sensFields == "" or sensFields == None:
        st.warning("Using Internal Configured PII List")
        return True


def startScanning():
    if validateInput() == False :
        return
    mrjira_name = ""

    sqlstr = st.session_state['sqlQueryScan']
    approvedfields = st.session_state['approvedFieldScan']
    sqlstrs = sqlstr.split(";")
    appFieldsList = approvedfields.split("\n")
    sensFields = st.session_state['sensitiveFields']
    if sensFields == "" or sensFields == None:
        sensitive_fields = st.secrets["sensitive_fields"]
    else:
        sensitive_fields = sensFields.split("\n")

    #st.write(sqlstrs)
    count = 0 # used for first level filtering for jira name and sets of tbl names and queries
    sqlqueries = [] # used to store all the queries, in relation to the table names stored in sqltblNames[]
    sqltblNames = [] # used to store all table names in relation to the queries stored in sqlqueries
    approvedTblNames = [] #used to store all the approved tbl names in relation to the approved fields stored in approvedfieldstrs
    approvedFieldStrs = [] #used to store all the approved fields in relation to approvedtblnames

    tblName = ""
    queryStr = ""
    cnt = 0 # second level filtering for table and queries
    for substr in sqlstrs:
        substrwords = substr.strip().split("\n")
        if len(substrwords) == 0:
            count += 1
            continue

        for substr2 in substrwords:
            substr2 = substr2.strip().lower()
            #st.text(substr2)
            if substr2 == "":
                cnt += 1
                continue

            if "moesyspq" in substr2: #parse jira name
                mrjira_name = substr2
                st.text("Start Scanning MR: "+ mrjira_name)
                cnt += 1
                continue

            if  substr2.startswith("--"): #parse comments happen before qecho
                cnt += 1
                continue

            if "qecho" in substr2: # parse tbl Name
                tblStrlst = substr2.split(" ",1)
                if len(tblStrlst) == 2:
                    tblName = tblStrlst[1].strip()
                    #st.text(tblName)
                    sqltblNames.append(tblName)
            else:
                if queryStr == "":
                    queryStr = substr2
                else:
                    queryStr = queryStr +" "+ substr2
                    #st.text(queryStr)
            cnt += 1

        #st.text(queryStr)

        if queryStr != "":
            cols = []
            try:
                colls = parse_one(queryStr, dialect="postgres").find_all(exp.Select)
                collscnt = 0
                for column in colls:
                    if collscnt > 0: # this is to skip subqueries inside the main sql. if there are subqueries, colls will have more than 1 count
                        continue
                    for proj in column.expressions:
                        if proj.alias_or_name.lower() not in cols:
                            cols.append(proj.alias_or_name.lower())
                    collscnt += 1
            except sqlglot.errors.ParseError as e:
                    print(e.errors)
                    st.error(e.errors,icon="🚨")
                    #st.error(":red["+queryStr+"] has errors", icon="🚨")
   
            #st.write(cols)
            sqlqueries.append(cols)
            queryStr = ""

        count += 1

    fieldRowCnt = 0

    for appfield in appFieldsList:
        #st.text(appfield)

        if "row" in appfield.lower():
            if fieldRowCnt == 3:
                fieldRowCnt = 4
            continue
        
        if 'set' in appfield.lower():
            if fieldRowCnt == 4:
                fieldRowCnt = 5
            continue

        if "+" in appfield:
            if fieldRowCnt == 2:
                fieldRowCnt = 3
            continue
        
        if "|" in appfield: #these are fields string
            if fieldRowCnt == 1:
                approvedFieldStrs.append(appfield.strip())
                fieldRowCnt = 2
            continue
        
        tblNList = appfield.strip().split()
        if len(tblNList) == 1:
            if fieldRowCnt == 0:
                approvedTblNames.append(tblNList[0])
                fieldRowCnt = 1
            continue


    if len(sqltblNames) != len(sqlqueries):
        st.text("There are "+ str(len(sqltblNames))+ " tables and " + str(len(sqlqueries))+ " queries")
        st.error("There are mismatched tables and queries in SQL text scan",icon="🚨")
        return
    
    if len(approvedTblNames) != len(approvedFieldStrs) :
        st.text("There are "+ str(len(approvedTblNames))+ " approved tables and " + str(len(approvedFieldStrs))+ " fields")
        st.error("There are mismatched approved tables and fields in approved fields input", icon="🚨")
        return

    if len(sqltblNames) != len(approvedTblNames):
        st.text("There are "+ str(len(sqltblNames))+ " tables and " + str(len(approvedTblNames))+ " approved tables")
        st.error("There are mismatched tables and approved tables",icon="🚨")
        return
    
    if len(sqlqueries) != len(approvedFieldStrs):
        st.text("There are "+ str(len(sqlqueries))+ " queries and " + str(len(approvedFieldStrs))+ " approved fields")
        st.error("There are mismatched sql queries and approved fields",icon="🚨")
        return

    #start matching
    errorFound = 0
    count = 0
    for actTblName in sqltblNames:
        for appTblName in approvedTblNames:
            if actTblName.strip() == appTblName.strip():
                break
        sqlq = sqlqueries[count] # this is a list now
        appFStr = approvedFieldStrs[count]
        appFStrLst = appFStr.split("|")
        found = False
        for qstr in sqlq:
            found = False
            for aFS in appFStrLst:
                if qstr == aFS.strip():
                    found = True
                    if qstr.strip() != "" and qstr.strip() in sensitive_fields:
                        st.warning("Table: "+ actTblName+ " Field :"+aFS+" is :red[sensitive]", icon="⚠️")
                    break
            if found == False:
                st.text(qstr)
                if qstr.strip() != "" and qstr.strip() in sensitive_fields:
                    st.error("Table Name: "+actTblName+" Field: "+ qstr+" is not matched, :red[This field is sensitve also], Pls check", icon="🚨")
                    errorFound += 1
                elif qstr.strip() != "":
                    st.error("Table Name: "+actTblName+" Field: "+qstr+" is not matched, Pls check", icon="🚨")
                    errorFound += 1
                    
        count += 1
    
    st.text("End of Scanning, "+ str(errorFound)+ " Errors found")

def initLayout2():
    st.header("SQL Queries to Scan")
    st.text_area("Input SQL queries to scan",key="sqlQueryScan", height=500)
    st.header("Log Files for tally")
    st.text_area("Input log file to tally with the queries",key="approvedFieldScan", height=500)
    st.header("Approved PII Fields")
    st.text_area(" Approved PII fields to check against the queries",key="approvedPIIFields", height=500)
    st.header("Sensitive PII Fields")
    sensitiveFields = ""
    sfs = st.secrets["sensitive_fields"]
    for sf in sfs:
        sensitiveFields = sensitiveFields + "\n" + sf
        
    st.text_area("Input Sensitive PII fields to check against the queries",value= sensitiveFields,key="sensitiveFields", height=500)

    st.button("Start Scanning", on_click=startScanning, type= "primary")


initLayout2()
