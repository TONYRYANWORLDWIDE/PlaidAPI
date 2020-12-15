import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json
import plaidbalance
import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import models
import ChimeModels
from pathlib import Path
from sqlalchemy import inspect
import requests




class getPlaid():
    def __init__(self):
        home = str(Path.home())
        self.credentials_file = os.path.join(home,'Desktop' ,'PlaidAPI' ,'credentials.json')
        self.PLAID_CLIENT_ID = ''
        self.PLAID_SECRET = ''
        self.PLAID_PUBLIC_KEY = ''
        self.chase_access_token = ''
        self.PLAID_ENV = ''
        self.server = ''
        self.user = ''
        self.password = ''
        self.database = ''
        self.userid = ''        

    def getCredentials(self):
        self.PLAID_ENV = os.getenv('PLAID_ENV', 'development')
        with open(self.credentials_file) as json_file:
            data = json.load(json_file)
            self.server =   data['codes']['connectionstring']['server']
            self.user =     data['codes']['connectionstring']['user']
            self.password = data['codes']['connectionstring']['password']
            self.database =  data['codes']['connectionstring']['database']
            self.userid = data['codes']['userid']['id']
            self.PLAID_CLIENT_ID =  data['codes']['plaid']['PLAID_CLIENT_ID']
            self.PLAID_SECRET =  data['codes']['plaid']['PLAID_SECRET']
            self.PLAID_PUBLIC_KEY = data['codes']['plaid']['PLAID_PUBLIC_KEY']
            self.chase_access_token =  data['codes']['plaid']['chase_access_token']
            self.ChimeToken =  data['codes']['plaid']['ChimeToken']
            self.client = plaid.Client(client_id = self.PLAID_CLIENT_ID, secret=self.PLAID_SECRET,
                            public_key=self.PLAID_PUBLIC_KEY, environment=self.PLAID_ENV, api_version='2019-05-29')
            self.params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                            "SERVER=" + self.server + ";"
                            "DATABASE=" + self.database + ";"
                            "UID=" + self.user + ";"
                            "PWD=" + self.password)
        return self    
class PlaidBalance():
    
    def __init__(self):
        self.chasebalance = 0

    def getBalance(self):
        PlaidCredentials = getPlaid()
        credentials = PlaidCredentials.getCredentials()
        chase_access_token = credentials.chase_access_token
        try:
            balance_response = credentials.client.Accounts.balance.get(credentials.chase_access_token)
            balances = balance_response['accounts']
            for x in balances:
                if x['name'] == 'TOTAL CHECKING':
                    self.chasebalance = x['balances']['available']
                    print(self.chasebalance)
            return self
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

class PlaidTransactions():

    def __init__(self,account):
        self.account = account

    def getTransactions(self):
        PlaidCredentials = getPlaid()
        credentials = PlaidCredentials.getCredentials()
        if self.account == 'Chase':
            access_token = credentials.chase_access_token
        elif self.account  =='Chime':
            access_token = credentials.ChimeToken
        else:
             access_token = None
        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(+1))
        print('start date:{} , end date{}'.format(start_date,end_date))
        try:
            transactions_response = credentials.client.Transactions.get(access_token, start_date, end_date, count = 50)
            return transactions_response
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
class updateDatabse():

    PlaidCredentials = getPlaid()
    credentials = PlaidCredentials.getCredentials()
    
    def databaseUpdateBalance(self):
        pb = PlaidBalance()
        pbalance = pb.getBalance()     
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(self.credentials.params))
        DBSession = sessionmaker(bind = engine)    
        session = DBSession()
        bankbalance = session.query(models.BankBalance).filter_by(UserID = self.credentials.userid).one()
        bankbalance.KeyBalance = pbalance.chasebalance
        bankbalance.DateTime = datetime.datetime.now()
        session.add(bankbalance)
        session.commit()

    def object_as_dict(self,obj): 
        c = {}       
        for x in inspect(obj).mapper.column_attrs:
            c[x.key] = getattr(obj, x.key)

        for key, value in c.items():
            if value is None:
                c[key] = ""  
            # if value == False:
            #     c[key] = False
            # if value == True:
            #     c[key] = True    
        return c

    def databaseUpdateTransactions(self,account):
        print('start trans')
        print(account)
        pt = PlaidTransactions(account=account)
        trans = pt.getTransactions()  
        transactions = trans['transactions']
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(self.credentials.params))
        DBSession = sessionmaker(bind = engine)   
        if account == 'Chase':
            for i in transactions:
                trans = models.Transactions(**i)                
                if trans.category != None:
                    category_to_string = ' '.join([str(elem) for elem in trans.category])   
                    trans.category = category_to_string

                location_to_string = ' '.join([str(elem) for elem in trans.location])   
                trans.location = location_to_string
                payment_meta_to_string = ' '.join([str(elem) for elem in trans.payment_meta])   
                trans.payment_meta = payment_meta_to_string
                trans.payment_meta = ''
                trandict = self.object_as_dict(trans)
                tranjson = json.dumps(trandict)
                tranjson2 = json.loads(tranjson)
                transactionid = trandict['transaction_id']
                accountid = trandict['account_id']
                # apibaseurl = 'http://localhost:64314/api/Transactions/'
                apibaseurl = 'https://monthlybillswebapitr.azurewebsites.net/api/Transactions/'
                print(apibaseurl)
                url = apibaseurl + transactionid + "/" + accountid
                headers = {"Content-Type" : "application/json"}
                print(url)
                req = requests.put(url = url, json =tranjson2, headers = headers)    
                # req2 = requests.Request('PUT', url = url, json = tranjson2,headers = headers)
                print("req2json")
                # print(req2.json)                
                # print(tranjson[0])
                # print(tranjson['account_id'])
                # print(req2.headers)
                # print(req2.url)
                # print(req2.data)
                print(trandict)
                # print(tranjson)
                print (req.status_code)
                # session = DBSession()
                # session.merge(trans)                
                # session.commit()
        elif account == 'Chime':
            for i in transactions:               
                trans = ChimeModels.Transactions(**i)

                if trans.category != None:
                    category_to_string = ' '.join([str(elem) for elem in trans.category])   
                    trans.category = category_to_string

                location_to_string = ' '.join([str(elem) for elem in trans.location])   
                trans.location = location_to_string
                payment_meta_to_string = ' '.join([str(elem) for elem in trans.payment_meta])   
                trans.payment_meta = payment_meta_to_string
                trans.payment_meta = ''

                trandict = self.object_as_dict(trans)
                tranjson = json.dumps(trandict)

                tranjson2 = json.loads(tranjson)
                transactionid = trandict['transaction_id']
                accountid = trandict['account_id']
                # apibaseurl = 'http://localhost:64314/api/TransactionsCMP/'
                apibaseurl = 'https://monthlybillswebapitr.azurewebsites.net/api/TransactionsCMP/'

                # print(tranjson2)
               
                url = apibaseurl #+ transactionid + "/" + accountid
                headers = {"Content-Type" : "application/json"}
                print(url)
                req = requests.put(url = url, json =tranjson2, headers = headers)    
                req2 = requests.Request('PUT', url = url, json = tranjson2,headers = headers)
                print(req.status_code)
                print("req2json")
                print(req2.json) 

                # session = DBSession()
                # session.merge(trans)
                # session.commit()            

def main():
    x = updateDatabse()
    x.databaseUpdateBalance()  
    x.databaseUpdateTransactions(account='Chime')       

main()
