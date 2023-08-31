import streamlit as st
import datetime
import pandas as pd
from datetime import date
from supabase import create_client, Client
#streamlit-calendar==0.4.0 need to add in requirement
from streamlit_calendar import calendar


st.set_page_config(
    page_title="View MR and File Download Duty Roster Schedule",
    page_icon="📆"
)

st.title("View MR and File Download Duty Roster Schedule")
st.sidebar.header("View Duty Roster Schedule")
st.markdown(
    """For ITD to view Duty Roster Schedule"""
)


#mode = st.selectbox(
 #   "Calendar Mode:", ("daygrid", "timegrid", "timeline",
  #                     "resource-daygrid", "resource-timegrid", "resource-timeline",
  #                     "list", "multimonth")
#)
def initDb():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

def loadCalendar():
    supabase= initDb()
    mrRows = supabase.table(st.secrets['duty_roster_tbl']).select("*", count='exact').eq("duty_type","MR").execute()
    downloadRows = supabase.table(st.secrets['duty_roster_tbl']).select("*", count='exact').eq("duty_type","File Download").execute()
    
    calendar_options = {}
    calendar_download_events =[]
    calendar_mr_events = []

    #calendar_events = [
     #   {"title": "Sheryl", "color": "#008000", "start": "2023-08-01", "end": "2023-08-01", "resourceId": ""},
      #  {"title": "Paul", "color": "#0000FF", "start": "2023-08-01", "end": "2023-08-01", "resourceId": ""},
       #  {"title": "Sheryl", "color": "#008000", "start": "2023-08-02", "end": "2023-08-02", "resourceId": ""},
        #{"title": "Paul", "color": "#0000FF", "start": "2023-08-02", "end": "2023-08-02", "resourceId": ""}
    #] events are sorted by alphabetical order

    for mrRow in mrRows.data:   
        mrDict1={}
        mrDict2={}
        back_per = mrRow["backup_personnel"]
        #if back_per:
        #    mrDict1["title"]=mrRow["primary_personnel"]+"/"+mrRow["backup_personnel"]
        #else:
        #    mrDict1["title"]=mrRow["primary_personnel"]
        mrDict1["title"]=str(1) + " "+ mrRow["primary_personnel"]
        mrDict1["color"]="#0000FF"
        mrDict1["start"]=mrRow["date_duty"]
        mrDict1["end"] = mrRow["date_duty"]
        mrDict1["resourceId"]=""

        if back_per:
            mrDict2["title"]=str(2)+" "+ back_per
            mrDict2["color"]="#008000"
            mrDict2["start"]=mrRow["date_duty"]
            mrDict2["end"] = mrRow["date_duty"]
            mrDict2["resourceId"]=""
            calendar_mr_events.append(mrDict2)
        
        calendar_mr_events.append(mrDict1)

    for dlRow in downloadRows.data:
        dlDict={}
        dlDict2={}

        back_per = dlRow['backup_personnel']
        if back_per:
            dlDict2["title"]=str(2)+" "+dlRow['backup_personnel']
            dlDict2["color"]="#008000"
            dlDict2["start"]=dlRow["date_duty"]
            dlDict2["end"]=dlRow["date_duty"]
            dlDict2["resourceId"]=""
            calendar_download_events.append(dlDict2)
       
        dlDict["title"]=str(1)+" "+dlRow['primary_personnel']
        dlDict["color"]="#0000FF"
        dlDict["start"]=dlRow["date_duty"]
        dlDict["end"]=dlRow["date_duty"]
        dlDict["resourceId"]=""
        calendar_download_events.append(dlDict)


    st.write(":blue[Primary is blue]")
    st.write(":green[Backup is green]")


    st.header("MR DUTY ROSTER")
    
    calendar(events=calendar_mr_events, options=calendar_options, key="mr_duty_roster")

    st.header("FILE DOWNLOAD DUTY ROSTER")
   # st.write(downloadRows.count)
    #st.write(calendar_events)

    calendar(events=calendar_download_events, options=calendar_options, key="file_download_duty_roster")


loadCalendar()


