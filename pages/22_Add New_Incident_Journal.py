import streamlit as st
import hashlib
from supabase import create_client, Client
import streamlit_authenticator
import pandas as pd
from datetime import datetime

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

    #st.write(credentials['usernames']['lipheng']['name'])

    authenticator = streamlit_authenticator.Authenticate(credentials,'diary_incident','test',cookie_expiry_days=1)

    name,authentication_status,username = authenticator.login('main')
    st.session_state['name'] = name
    st.session_state['authentication_status'] = authentication_status
    st.session_state['username'] = username
    st.session_state['authenticator'] = authenticator
    st.session_state['credentials'] = credentials

    if authentication_status:
        loadAddNewPage()    
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

    #st.button("Reset Password",on_click=resetPassword) #, on_click=resetPassword())
    #st.button("Reset Password", type='primary',on_click=resetPassword())
        

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


def loadAddNewPage():
        #st.title('Add New Incident Diary')
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = False

        if st.session_state['authentication_status'] == True:
            ids = getIds()
            st.sidebar.title("Add New Incident Jorunal")
            st.sidebar.selectbox('Update/Add New Incident',options=ids,key='updateaddmode')#,on_change=loadAddNewModifyPage)
            loadAddNewModifyPage()
            #st.date_input('Incident Date', key='incidentdate')
            #st.text_area('Description',help='This is to key in the description of incident',key='incidentdesc')
            #st.text_area('Root Cause', help='This is to document the root cause of incident', key='rootcause')
            #st.text_area('Lesson Learnt', help='This is to document the lesson learnt during the incident',key='lessonlearnt')
            #st.selectbox("Project", st.secrets['project_list'],key="project")
            #submitted = st.button("Submit", on_click=validateAndSubmit)
        else:
            loginApp()

def loadAddNewModifyPage():
    incident = {}
    #st.write(st.session_state['updateaddmode'])
    if st.session_state['updateaddmode'] == 'Add New' or st.session_state['updateaddmode'] == 'Select Mode':
            st.date_input('Incident Date', value='today', key='incidentdate')
            st.text_area('Description',help='This is to key in the description of incident',key='incidentdesc')
            st.text_area('Root Cause', help='This is to document the root cause of incident', key='rootcause')
            st.text_area('Lesson Learnt', help='This is to document the lesson learnt during the incident',key='lessonlearnt')
            st.selectbox("Project", st.secrets['project_list'],key="project")
            submitted = st.button("Submit", on_click=validateAndSubmit)
    else:
        incident = getIncidentDetails(st.session_state['updateaddmode'])
        st.date_input('Incident Date',value=convertToDate(incident['incident_date']), key='incidentdate')
        st.text_area('Description',value=incident['incident_desc'],help='This is to key in the description of incident',key='incidentdesc')
        st.text_area('Root Cause', value=incident['root_cause'],help='This is to document the root cause of incident', key='rootcause')
        st.text_area('Lesson Learnt', value= incident['lesson_learnt'],help='This is to document the lesson learnt during the incident',key='lessonlearnt')
        st.selectbox("Project", index=getProjIndex(incident['proj_name']), options=st.secrets['project_list'],key="project")
        submitted = st.button("Submit", on_click=validateAndSubmit)

def convertToDate(dateStr):
    dateObj = datetime.strptime(dateStr,'%Y/%m/%d')
    return dateObj


def getProjIndex(proj):
    id = 0
    for idx in st.secrets['project_list']:
        if idx == proj:
            return id
        else:
            id = id + 1

    return id

def getIncidentDetails(id):
    #st.write(id)
    supabase= initDb() 
    incident = {}
    
    rows = supabase.table(st.secrets['incident_tbl']).select("*", count='exact').eq('id',str(id)).execute()
    for row in rows.data:
        incident['incident_date'] = row['incident_date']
        incident['incident_desc'] = row['incident_desc']
        incident['root_cause'] = row['root_cause']
        incident['lesson_learnt'] = row['lesson_learnt']
        incident['proj_name'] = row['proj_name']

    return incident

def validateAndSubmit():
    if st.session_state['incidentdesc'] == "":
        st.error("Please key incident description", icon="🚨")
    elif st.session_state['rootcause'] == "":
        st.error("Please key root cause", icon="🚨")
    elif st.session_state['lessonlearnt'] == "":
        st.error("Please key lesson learnt", icon="🚨")
    else:
        if st.session_state['updateaddmode'] != "Add New" and st.session_state['updateaddmode'] != 'Select Mode':
            updateNewIncident(st.session_state['updateaddmode'])
        else:
            insertNewIncident()


def insertNewIncident():
    supabase= initDb() 
    incident = {}
    #st.write(newPassword)
    incident['incident_date'] = convertDateValue(st.session_state['incidentdate'])
    incident['incident_desc'] = st.session_state['incidentdesc']
    incident['root_cause'] = st.session_state['rootcause']
    incident['lesson_learnt'] = st.session_state['lessonlearnt']
    incident['user_name'] = st.session_state['username']
    incident['proj_name'] = st.session_state['project']
    row = supabase.table(st.secrets['incident_tbl']).insert(incident).execute()
    st.success("New Incident Diary created", icon="✅")

def updateNewIncident(id):
    supabase= initDb() 
    incident = {}
    #st.write(newPassword)
    incident['incident_date'] = convertDateValue(st.session_state['incidentdate'])
    incident['incident_desc'] = st.session_state['incidentdesc']
    incident['root_cause'] = st.session_state['rootcause']
    incident['lesson_learnt'] = st.session_state['lessonlearnt']
    incident['user_name'] = st.session_state['username']
    incident['proj_name'] = st.session_state['project']
    row = supabase.table(st.secrets['incident_tbl']).update(incident).eq("id",id).execute()
    st.success("Incident Diary updated", icon="✅")

def getIds():
    supabase= initDb() 
    ids = []
    ids.append('Select Mode')
    ids.append('Add New')
    username = st.session_state['username']
    rows = supabase.table(st.secrets['incident_tbl']).select("id", count='exact').eq('user_name',username).execute()
    for row in rows.data:
        ids.append(str(row['id']))

    return ids

loadAddNewPage()