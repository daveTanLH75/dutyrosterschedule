import streamlit as st
import json
import csv
from io import StringIO


st.set_page_config(page_title="Data Import", page_icon="🌍")

def viewCSVData():
    importStr = st.session_state['textToImport']
    if importStr is None or importStr == "":
         return
    jsonStr = StringIO(importStr)
    data = json.load(jsonStr)
    entities = []

    for d in data['Entities']:
            dd = d['Data']['AWS:InstanceInformation']
            ddd = dd['Content'][0]
            entity = {}
            entity['Id'] = d['Id']
            entity['TypeName'] = dd['TypeName']
            entity['SchemaVersion'] = dd['SchemaVersion']
            entity['CaptureTime'] = dd['CaptureTime']
            entity['InstanceId'] = ddd['InstanceId']
            entity['InstanceStatus'] = ddd['InstanceStatus']
            entity['InstanceType'] = "NA"
            entity['InstanceName'] = "NA"
            entity["InstancePurpose"] = "NA"
            if ddd['InstanceStatus'] != 'Terminated':
                entity['AgentType'] = ddd['AgentType']
                entity['AgentVersion'] = ddd['AgentVersion']
                entity['ComputerName'] = ddd['ComputerName']
                entity['IpAddress'] = ddd['IpAddress']
                entity['PlatformName'] = ddd['PlatformName']
                entity['PlatformType'] = ddd['PlatformType']
                entity['PlatformVersion'] = ddd['PlatformVersion']
                entity['ResourceType'] = ddd['ResourceType']
            else :
                entity['AgentType'] = "NA"
                entity['AgentVersion'] = "NA"
                entity['ComputerName'] = "NA"
                entity['IpAddress'] = "NA"
                entity['PlatformName'] = "NA"
                entity['PlatformType'] = "NA"
                entity['PlatformVersion'] = "NA"
                entity['ResourceType'] = "NA"
                 

            entities.append(entity)
        
            #st.write(entity)
    
    ec2Str = st.session_state['ec2txt']
    if ec2Str is None or ec2Str == "":
         return
    jsonec2Str = StringIO(ec2Str)
    ec2Data = json.load(jsonec2Str)

    for ec2Da in ec2Data['Reservations']:
         for intData in ec2Da['Instances']: #instances can be more than 1
            for ec2dict in entities:
                if ec2dict['Id'] == intData['InstanceId'] :
                    ec2dict['InstanceType'] = intData['InstanceType'] #instance family of ec2
                    for tagData in intData['Tags']:
                        if tagData['Key'] =='Purpose' :
                            ec2dict['InstancePurpose'] = tagData['Value']
                        elif tagData['Key'] == 'Name':
                            ec2dict['InstanceName'] = tagData['Value']
        
    with open('test.csv','w') as csv_file:
         #fieldNames = ['Id','TypeName','SchemaVersion','CaptureTime','InstanceId','InstanceStatus','AgentType','AgentVersion','ComputerName','IpAddress','PlatformName','PlatformType','PlatformVersion','ResourceType']
        writer = csv.DictWriter(csv_file, fieldnames=entities[0].keys())
        writer.writeheader()
        for ent in entities:
              writer.writerow(ent)
    with open('test.csv','r') as file:
        st.download_button(
            label="Click here to download asset list csv",
            data= file,
            file_name= 'asset.csv',
            mime="text/csv"
            )
    


st.header("Generate AWS Assets Tool")
st.text_area("Copy and paste in the EC2 SSM Output Data in JSON Format",key="textToImport", height=500)
st.text_area('Copy and paste in the AWS Describe EC2 Instances output in JSON Format to get instance family', key='ec2txt' , height=500)
st.button("Export to CSV", on_click=viewCSVData)


