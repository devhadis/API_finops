import json
import time
import datetime import datetime as DT
import datetime import date
import requests
import urllib3
import locale
import calendar
import csv
import os 
from pathlib import Path

import mysql.connector
from mysql.connector import Error


script_path = Path(__file__).resolve()

script_dir = script_path.parent

os.chdir(script_dir)

print(f"Current working directoyr: {os.getcwd()}")

requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exception.InsecureRequestWarning)

turbo_ip = ""
userName = ""    #"turboscript"
password = ""    #"Scaleup@2026"



company_name = "" #Não esqueça  o nome da empresa 

data_base_name = "db_finops_turbonomic_" + company_name 

data_base_settings = {
    'host': 'localhost',
    'userName': '', 
    'password':'',
    'database': data_base_name
}

authToken =  ""


def login():
    
    global authToken, requestSession
    
    requestSession = requests.Session()
    
    payload = {"username": userName, "password":password}
    
    response =  requestSession.port("https://{}/api/v3/login".format(turbo_ip),data=payload, verify=False)
    
    if (response.status_code == 200):
        content = response.content.decode("utf8")
        api_response = json.loads(content)
        return api_response["authToken"]
        
    else:
        print(str(DT.now()), "API Call Failed: ", response.status_code, "\n",response.text, "\n" )



def get_json_from_url_turbo(url):
   
    response = requestSession.get(url, headers = {'content-type': 'application/json'}, verify = False, timeout = 15)
    
    if (response.status_code == 200):
        content = response.content.decode("utf8")
        api_response = json.loads(content)
    
    else:
        api_response =  None
        print(str(DT.now()), "API Call Failed", response.status_code, "\n", url, "\n")
        print("API Error:", response.text)
    return api_response
        
    
def post_json_from_url_turbo(url,data):
    
    response = requestSession.post(url, data = json.dumps(data), headers = {'accept': 'application/json', 'content-type': 'application/json'}, verify = False)    
    
    print(str(DT.now()), response)
    if (response.status_code == 200):
        content = response.content.decode("utf8")
        api_response = json.loads(content)
    else:
        api_response = None
        print(str(DT.now()), "API Call Failed:", response.status_code, "\n", url, "\n")
        print("API Error", response.text)
    
    return api_response
    


#NÃO É PARA SE UTILIZADO, ESTA AQUI POR PADRÃO DE PROJETO 
##########################################################################################################################
#def delete_json_from_url_turbo(url): #DELETE API Call                                                                   # 
#                                                                                                                        # 
#    response = requestSession.delete(url, headers= {'content-type': 'application/json'}, verify = False)                #
#    print(str(DT.now()), response)                                                                                      #
#    print(str(DT.now()),response)                                                                                       #
#    return response                                                                                                     # 
###########################################################################################################################    

authToken = login()

def getAllExecutedActions(startdate, enddate, filename):
    
    cursor_turbo = 0
    actionCountLimit = 500
    
    actionTotalURLEnpoint = "https://{}/api/v3/markets/Market/actions?limit={}".format(turbo_ip, actionCountLimit)
    
    actionPayload = {
        "startTime" : "{}". format(startdate), 
        "endTime" : "{}".format(enddate),
        "actionStateList": ["SUCCEEDED"],
        "environmentType":"CLOUD",
        "detailLevel": "EXECUTION"
    }
    
    print(actionPayload)
    totalActionCount = 2000
    
    
    #---------------------------------------- conexão ao Mysql --------------------------------------------------------------------------------------
    try:
        
        connection = mysql.connector.connect(**db_config)
        cursor_db = connection.cursor()
        print(f"CONECTADO com sucesso ao banco ")
    except Error as e:
        print(f"Errod ao conectar no MySQL: {e}")
        return
    
    with open (filename, 'w', encoding = 'utf8', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=';')
        csv_writer.writerow(['Date', 'Entity Type', 'Action Type', 'Entity', 'details', 'Account Name','Resource Group', 'Execucao', 'Mode','Usuario', 'Savings ($/hr)', 'Savings ($/mes)' ,'TAG XPCA'])
        
        for elements in range(0, totalActionCount, actionCountLimit):
            
            actionURLEndpoint = "https://{}/vmturbo/rest/markets/777777/actions?cursor={}&limit={}&order_by=NAME&ascending=true".format(turbo_ip, cursor_turbo, actionCountLimit)
            actionList = post_json_from_url_turbo(actionURLEndpoint, actionPayload)
            
        
        if not actionList:
            break
        
        for action in actionList:
            entitytype = action['target']['className']
            actiontype = action['actionType']
            
            try:
                details =  action['details']
            
            
            except KeyError:
                details = "N/A"
            
            try:
                XPCA = action['target']['tags']['xp-cost-allocation'][0]
            
            except: 
                resourcegroup = "NA"
            
            action_time - action['updateTime']
            
            mode = action['actionMode']
            
            userName =  action['userName']
            
            category = action['risk']['subCategory']
            
            accountName = (details.split(''))[-1].strip()
            
            try:
                entityname = action['target']['displayName']
            
            except:
                
                entityname = "VOLUME SEM NOME DEFINIDO "              
            
            try:
                saving = float(action['stats'][0]['value'])
            
            except (KeyError, IndexError, ValueError):
                saving = 0.0
            
            savingmensal = 0.0
            
            csv_writer.writerow([action_time, entitytype, actiontype, entityname, details, accountName, resourcegroup, category, ])
            
                
            
            
            
            
            
                           
                           
                           
                           

            
                 
