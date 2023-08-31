import streamlit as st
import datetime
import pandas as pd
from datetime import date
from supabase import create_client, Client

st.set_page_config(
    page_title="Day 2 OPS Process",
    page_icon="👋",
)
st.sidebar.title("Day 2 Ops")
st.title("Welcome to Day 2 ops 👋")


def initDb():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

def convertDate(r):
	newDate = pd.to_datetime(r)
	newdate=newDate.strftime('%Y/%m/%d')
	
	return newdate
	
#def migrationFunc():
	supabase= initDb()
	rows = supabase.table("mrdownloadstatistics").select("*").gte("id",5001).execute()
	st.write(rows.data.count)
	for row in rows.data:
		#st.write(row)
		newdate= convertDate(row['request_date'])
		st.write(newdate)
		supabase.table("mrdownloadstatistics").update({"request_date": newdate}).eq("id",row['id']).execute()
		#st.write(f"request id:{row['id']} date is{row['request_date']}:")

def initLayout():
    st.write("Welcome 👋")


def startApp():
	supabase = initDb()
	
def main():
		initLayout()
		
if __name__ == "__main__":
	main()
