import streamlit as st
import hashlib
from supabase import create_client, Client
import streamlit_authenticator
import pandas as pd

def initDb():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

def app():
    st.set_page_config(
            page_title="Incident Journal",
            page_icon="👋",
        )
    
    loginApp()
    
    #btnReset = st.button("click here to reset password", on_click=resetPassword(),key="1")
    #if btnReset:
        #resetPassword()

def fetchAllUsers():
    supabase= initDb() 
    user = {}
    userList =[]

    rows = supabase.table(st.secrets['acct_user_tbl']).select("*", count='exact').execute()
    for row in rows.data:
        user['username'] = row['username']
        user['usrName'] = row['usrName']
        user['password'] = row['password']
        userList.append(user)


    return userList

def loginApp():
    users = fetchAllUsers()
    usernames = [user['username'] for user in users]
    names = [user['usrName'] for user in users]
    hash_passwords = [user['password'] for user in users]

    credentials = {'usernames':{}}

    for usrname, userN, pw in zip(usernames,names,hash_passwords):
        user_dict = {'name':userN,'password':pw}
        credentials['usernames'].update({usrname:user_dict})

    authenticator = streamlit_authenticator.Authenticate(credentials,'diary_incident','test',cookie_expiry_days=1)

    name,authentication_status,username = authenticator.login('main')
    st.session_state['name'] = name
    st.session_state['authentication_status'] = authentication_status
    st.session_state['username'] = username
    st.session_state['authenticator'] = authenticator
    st.session_state['credentials'] = credentials

    if authentication_status:
        loadIncidentPage()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

        

def hashText(password): #not use here
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode())
    hash_password = hash_obj.hexdigest()
    return hash_password

def convertDateValue(r):
    newDate = pd.to_datetime(r)
    newdate=newDate.strftime('%Y/%m/%d')
    return newdate

def resetPassword():
    
    authentication_status = st.session_state['authentication_status']
    username = st.session_state['username']
    authenticator = st.session_state['authenticator']
    credentials = st.session_state['credentials']

    if authentication_status:
        try:
            if authenticator.reset_password(username,'main'):
                #st.write(credentials)
                newPassword = credentials['usernames'][username]['password']
                name = credentials['usernames'][username]['name']
                updatePassword(username,newPassword,name)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

def updatePassword(username, newPassword, name):
    supabase= initDb() 
    user = {}
    st.write(newPassword)
    user['usrName'] = name
    user['password'] = newPassword
    user['username'] = username
    row = supabase.table(st.secrets['acct_user_tbl']).update(user).eq("username",username).execute()

def loadIncidentPage():
    authentication_status = st.session_state['authentication_status']
    username = st.session_state['username']
    name = st.session_state['name']
    if authentication_status:
        st.title("Incident Journal")
        st.write('Welcome *%s*' % (name))

        loadIncidentPageControls(username)
    else:
        st.error("Not Authenticated encountered")


def loadIncidentPageControls(username):
    supabase= initDb() 
    incident_dates = []
    incident_desc = []
    lesson_learnt = []
    root_cause = []
    projs_names = []
    ids = []

    rows = supabase.table(st.secrets['incident_tbl']).select("*", count='exact').eq('user_name',username).execute()
    
    for row in rows.data:
        incident_dates.append(row['incident_date'])
        incident_desc.append(row['incident_desc'])
        lesson_learnt.append(row['lesson_learnt'])
        root_cause.append(row['root_cause'])
        projs_names.append(row['proj_name'])
        ids.append(row['id'])
    data = {
        'Id':ids,
        'Date of Incident':incident_dates,
        'Incident Descriptions':incident_desc,
        'Root Cause':root_cause,
        'Lesson Learnt':lesson_learnt,
        'Project':projs_names
    }
    df = pd.DataFrame(data)
    
    st.dataframe(df,width=2000,hide_index=True)
    #st.table(data)


app()