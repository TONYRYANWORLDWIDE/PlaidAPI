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
class plaidApp():

    def __init__(self):
        self.credentials_file = 'C:/Users/tonyr/Desktop/PlaidAPIFinal/credentials.json'
        self.PLAID_CLIENT_ID = ''
        self.PLAID_SECRET = ''
        self.PLAID_PUBLIC_KEY = ''
        self.chase_access_token = ''
        self.PLAID_ENV = ''
        self.chase_access_token = ''
        self.server = ''
        self.user = ''
        self.password = ''
        self.database = ''
        self.userid = ''
        self.params = ''

    def getplaid(self):
        self.PLAID_ENV = os.getenv('PLAID_ENV', 'development')
        with open(self.credentials_file) as json_file:
            data = json.load(json_file)
            self.PLAID_CLIENT_ID =  data['codes']['plaid']['PLAID_CLIENT_ID']
            self.PLAID_SECRET =  data['codes']['plaid']['PLAID_SECRET']
            self.PLAID_PUBLIC_KEY = data['codes']['plaid']['PLAID_PUBLIC_KEY']
            self.chase_access_token =  data['codes']['plaid']['chase_access_token']
    
    def getPa(self):
        self.getplaid()        
        self.client = plaid.Client(client_id = self.PLAID_CLIENT_ID, secret=self.PLAID_SECRET,
                        public_key=self.PLAID_PUBLIC_KEY, environment=self.PLAID_ENV, api_version='2019-05-29')
        return self

    def getBalance(self):
        self.getPa()
        chase_access_token = self.chase_access_token
        try:
            balance_response = self.client.Accounts.balance.get(chase_access_token)
            balances = balance_response['accounts']
            for x in balances:
                if x['name'] == 'TOTAL CHECKING':
                    self.chasebalance = x['balances']['available']
                    print(self.chasebalance)
            return self
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

    def getConnection(self):
        with open(self.credentials_file) as json_file:
            data = json.load(json_file)
            self.server =   data['codes']['connectionstring']['server']
            self.user =     data['codes']['connectionstring']['user']
            self.password = data['codes']['connectionstring']['password']
            self.database =  data['codes']['connectionstring']['database']
            self.userid = data['codes']['userid']['id']
        return self

    def getparams(self):
        self.getConnection()
        self.params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=" + self.server + ";"
                                 "DATABASE=" + self.database + ";"
                                 "UID=" + self.user + ";"
                                 "PWD=" + self.password)
        return self

    def databaseUpdate(self):
        self.getBalance()    
        self.getparams()
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(self.params))
        DBSession = sessionmaker(bind = engine)    
        session = DBSession()
        bankbalance = session.query(models.BankBalance).filter_by(UserID = self.userid).one()
        bankbalance.KeyBalance = self.chasebalance
        bankbalance.DateTime = datetime.datetime.now()
        session.add(bankbalance)
        session.commit()

def main():
    pa = plaidApp()
    pa.databaseUpdate()

main()