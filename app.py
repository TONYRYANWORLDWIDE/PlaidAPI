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
class getPlaid():

    def __init__(self):
        self.credentials_file = 'C:/Users/tonyr/Desktop/PlaidAPIFinal/credentials.json'
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
    def getTransactions(self):
        PlaidCredentials = getPlaid()
        credentials = PlaidCredentials.getCredentials()
        chase_access_token = credentials.chase_access_token

        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-1))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        print('start date:{} , end date{}'.format(start_date,end_date))
        try:
            transactions_response = credentials.client.Transactions.get(credentials.chase_access_token, start_date, end_date)
            # transactions = response['transactions']
            return transactions_response
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
class updateBankBalanceInDatabase():

    def databaseUpdate(self):
        gp = getPlaid()
        plaidCredentials = gp.getCredentials()
        pb = PlaidBalance()
        # pbalance = pb.getBalance() 
        trans = pb.getTransactions()
        # print(trans)
        
        # engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(plaidCredentials.params))
        # DBSession = sessionmaker(bind = engine)    
        # session = DBSession()
        # bankbalance = session.query(models.BankBalance).filter_by(UserID = plaidCredentials.userid).one()
        # bankbalance.KeyBalance = pbalance.chasebalance
        # bankbalance.DateTime = datetime.datetime.now()
        # session.add(bankbalance)
        # session.commit()
        return trans
def main():
    x = updateBankBalanceInDatabase()
    thetrans = x.databaseUpdate()
    print(thetrans)
    
    # print(thetrans['accounts'])



main()