import streamlit as st
import json
import csv
from io import StringIO


st.set_page_config(page_title="Data Import", page_icon="🌍")

def viewCSVData():
    importStr = st.session_state['textToImport']
    importStr = importStr.strip()
    if importStr == "":
         return
    jsonStr = StringIO(importStr)

    try:
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

    except Exception as e:
            st.write(e)
            st.error("Invalid json for SSM EC2 ", icon="🚨")
            #print ('Invalid json for SSM EC2',e)
            return
    
    ec2Str = st.session_state['ec2txt']
    ec2Str = ec2Str.strip()
    if ec2Str != "":
        jsonec2Str = StringIO(ec2Str)

        try:
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
        except Exception as e:
            st.write(e)
            st.error("Invalid json for describe ec2 ", icon="🚨")
            #print ('Invalid json for describe ec2',e)
            return
        
    with open('test_ec2.csv','w') as csv_file:
         #fieldNames = ['Id','TypeName','SchemaVersion','CaptureTime','InstanceId','InstanceStatus','AgentType','AgentVersion','ComputerName','IpAddress','PlatformName','PlatformType','PlatformVersion','ResourceType']
        writer = csv.DictWriter(csv_file, fieldnames=entities[0].keys())
        writer.writeheader()
        for ent in entities:
              writer.writerow(ent)
    with open('test_ec2.csv','r') as file:
        st.download_button(
            label="Click here to download EC2 asset list csv",
            data= file,
            file_name= 'asset.csv',
            mime="text/csv"
            )


def viewRDSData():
    rdsStr = st.session_state['rdstxt']
    
    rdsStr =rdsStr.strip() 
    if rdsStr == "":
         return
    try:
        jsonStr = StringIO(rdsStr)
        data = json.load(jsonStr)
        entities = []
        for d in data['DBInstances']:
            certificateDetails = d['CertificateDetails']
            entity = {}
            entity['DBInstanceIdentifier'] = d['DBInstanceIdentifier']
            entity['DBInstanceClass'] = d['DBInstanceClass']
            entity['Engine'] = d['Engine']
            entity['DBInstanceStatus'] = d['DBInstanceStatus']
            entity['MasterUsername'] = d['MasterUsername']
            if d.get('DBName'):
                entity['DBName'] = d['DBName']
            else:
                 entity['DBName'] = "NA"

            entity['AllocatedStorage'] = d['AllocatedStorage']
            entity['InstanceCreateTime'] = d['InstanceCreateTime']
            entity['PreferredBackupWindow'] = d['PreferredBackupWindow']
            entity['BackupRetentionPeriod'] = d['BackupRetentionPeriod']
            entity['PreferredMaintenanceWindow'] = d['PreferredMaintenanceWindow']
            entity['MultiAZ'] = d['MultiAZ']
            entity['EngineVersion'] = d['EngineVersion']
            entity['AutoMinorVersionUpgrade'] = d['AutoMinorVersionUpgrade']
            entity['PubliclyAccessible'] = d['PubliclyAccessible']
            entity['StorageType'] = d['StorageType']
            entity['PerformanceInsightsEnabled'] = d['PerformanceInsightsEnabled']
            if d.get('PerformanceInsightsRetentionPeriod'):
                entity['PerformanceInsightsRetentionPeriod'] = d['PerformanceInsightsRetentionPeriod']
            else:
                 entity['PerformanceInsightsRetentionPeriod'] = 'NA'

            entity['DeletionProtection'] = d['DeletionProtection']
            entity['KmsKeyId'] = d['KmsKeyId']
            entity['StorageEncrypted'] = d['StorageEncrypted']
            entity['MonitoringInterval'] = d['MonitoringInterval']
            entity['CAIdentifier'] = certificateDetails['CAIdentifier']
            entity['ValidTill'] = certificateDetails['ValidTill']
            for tagData in d['TagList']:
                entity[tagData['Key']] = tagData['Value']
                #if tagData['Key'] == 'Backup_Group01':
                      #entity['Backup_Group01'] = tagData['Value']
                #if tagData['Key'] == 'Project-Code':
                      #entity['Project-Code'] = tagData['Value']
               # if tagData['Key'] == 'Tier':
                    #entity['Tier'] = tagData['Value']
                #if tagData['Key'] == 'Compartment':
                    #entity['Compartment'] = tagData['Value']
                #if tagData['Key'] == 'Zone':
                    #entity['Zone'] = tagData['Value']
                #if tagData['Key'] == 'Environment':
                    #entity['Environment'] = tagData['Value']
                
                

            #st.write(d)
            entities.append(entity)

    except  Exception as e:
        st.write(e)
        st.error("Invalid JSON For RDS ", icon="🚨")
        return
            #st.write(entity)
    
    with open('test_rds.csv','w') as csv_file:
         #fieldNames = ['Id','TypeName','SchemaVersion','CaptureTime','InstanceId','InstanceStatus','AgentType','AgentVersion','ComputerName','IpAddress','PlatformName','PlatformType','PlatformVersion','ResourceType']
        writer = csv.DictWriter(csv_file, fieldnames=entities[0].keys())
        writer.writeheader()
        for ent in entities:
              writer.writerow(ent)
    with open('test_rds.csv','r') as file:
        st.download_button(
            label="Click here to download RDS asset list csv",
            data= file,
            file_name= 'asset_rds.csv',
            mime="text/csv"
            )



st.header("Generate AWS Assets Tool")
st.text_area("Copy and paste in the EC2 SSM Output Data in JSON Format",key="textToImport", height=500)
st.text_area('Copy and paste in the AWS Describe EC2 Instances output in JSON Format to get instance family', key='ec2txt' , height=500)
st.button("Export for EC2 CSV", on_click=viewCSVData)

st.text_area('Copy and paste in the AWS Describe RDS Instances output in JSON Format', key='rdstxt' , height=500)
st.button("Export for RDS CSV", on_click=viewRDSData)




