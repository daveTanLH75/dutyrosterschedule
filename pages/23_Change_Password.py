import streamlit as st
import hashlib
from supabase import create_client, Client
import streamlit_authenticator
import pandas as pd

def initDb():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

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
        resetPassword()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')


def resetPassword():

    if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = False

    authentication_status = st.session_state['authentication_status']

    if authentication_status:
        try:
            authentication_status = st.session_state['authentication_status']
            username = st.session_state['username']
            authenticator = st.session_state['authenticator']
            credentials = st.session_state['credentials']
            if authenticator.reset_password(username,'main'):
                #st.write(credentials)
                newPassword = credentials['usernames'][username]['password']
                name = credentials['usernames'][username]['name']
                updatePassword(username,newPassword,name)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)
    else:
        loginApp()

def updatePassword(username, newPassword, name):
    supabase= initDb() 
    user = {}
    user['usrName'] = name
    user['password'] = newPassword
    user['username'] = username
    row = supabase.table(st.secrets['acct_user_tbl']).update(user).eq("username",username).execute()

resetPassword()