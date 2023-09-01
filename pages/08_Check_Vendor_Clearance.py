import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date
import re


st.set_page_config(page_title="Vendor Clearance Checker", page_icon="🌍")

#st.markdown(
 #   """This is under construction"""
#)


def initDb():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

def convertDate(r):
	newDate = pd.to_datetime(r)
	newdate=newDate.strftime('%Y/%m/%d')
	
	return newdate


def convertDateValue(r):
    newDate = pd.to_datetime(r)
    newdate=newDate.strftime('%Y-%m-%d')
    return newdate


def searchPersonnelByEmail():
    supabase= initDb()
    addressToSearch = st.session_state['addressToSearch']

    st.title("Vendor Personnel")
    if inputValidationText(addressToSearch):
        rows = supabase.table(st.secrets['vendor_pers_tbl']).select("*", count='exact').ilike("company_email","%"+addressToSearch+"%").execute()
        st.success(str(rows.count) + " records retrieved", icon="✅")
        for row in rows.data:
            id = row['id']
            techPassId = searchForTechpass(row['company_email'])
            st.write(row)
            if checkPersonnelClearance(row['name'], row['ipa_date'], row['security_clear_date'],row['onshore_offshore'],row['roll_off_date']):
                st.write(row['name']+ " is cleared and working onshore")

            if techPassId is not None:
                st.write("TechPass Id is "+techPassId)
            else:
                st.write("Techpass Id has not been applied yet")

    else:
        st.success("0 records retrieved", icon="✅")

def searchPersonnelByName():
    supabase= initDb()
  
    nameToSearch = st.session_state['nameToSearch']

    st.title("Vendor Personnel")
    if inputValidationText(nameToSearch):
        rows = supabase.table(st.secrets['vendor_pers_tbl']).select("*", count='exact').ilike("name","%"+nameToSearch+"%").execute()
        st.success(str(rows.count) + " records retrieved", icon="✅")
        for row in rows.data:
            id = row['id']
            techPassId = searchForTechpass(row['company_email'])
            st.write(row)
            if checkPersonnelClearance(row['name'], row['ipa_date'], row['security_clear_date'],row['onshore_offshore'],row['roll_off_date']):
                st.write(row['name']+ " is cleared and working onshore")

            if techPassId is not None:
                st.write("TechPass Id is "+techPassId)
            else:
                st.write("Techpass Id has not been applied yet")
            

    else:
        st.success("0 records retrieved", icon="✅")


def inputValidationText(txtToCheck):
    if txtToCheck is None:
        return False

    if len(txtToCheck) <= 3:
        return False

    regex = re.compile('[_!#$%^&*()<>?/\|}{~:]') #check for any characters within the [ ]

    if regex.search(txtToCheck) == None:
        return True
    
    return False

def searchForTechpass(compEmail):
    supabase= initDb()
    if compEmail is None or compEmail == "":
        return ""

    rows = supabase.table(st.secrets['email_techpass_tbl']).select("techpass_email", count='exact').eq("company_email",compEmail).execute()
   
    if len(rows.data) != 0:
        for row in rows.data:
            return row['techpass_email']


def getCompanyEmail(techpassId):
    supabase= initDb()
    
    co_email = ""

    if techpassId != "":
        techpassId = techpassId.strip()
        rows = supabase.table(st.secrets['email_techpass_tbl']).select("company_email", count='exact').eq("techpass_email",techpassId).execute()
        for row in rows.data:
            #id = row['id']
            co_email = row['company_email']
            break
    
    return co_email

def checkPersonnelClearance(name,ipa_date, clearance_date, onshore_offshore, roll_off_date):

    if clearance_date is None and ipa_date is None:
        st.write(name + " has not been cleared yet")
        return False 
    
    if roll_off_date is not None:
        roll_date = pd.to_datetime(roll_off_date)
        if roll_date.date() <= datetime.today().date():
            st.write(name +" is leaving or has been rolled off")
            return False

    if onshore_offshore == "Offshore":
        st.write(name + " is Cleared but working Offshore, do not allocate notebook to the personnel")
        return False
    
    

    return True



st.sidebar.header("Check Vendor Clearance")
st.sidebar.text_input("Enter personnel name: ",key="nameToSearch")
st.sidebar.button("Search by Name", on_click=searchPersonnelByName)

st.sidebar.text_input("Enter email address: ",key="addressToSearch")
st.sidebar.button("Search by email", on_click=searchPersonnelByEmail)

