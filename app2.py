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
from models import Base, BankBalance


class plaidApp():

    def __init__(self):
        self.credentials_file = 'C:/Users/tonyr/Desktop/PlaidAPIFinal/credentials.json'
        self.PLAID_CLIENT_ID = ''
        self.PLAID_SECRET = ''
        self.PLAID_PUBLIC_KEY = ''
        self.chase_access_token = ''
        self.PLAID_ENV = ''
        self.chase_access_token = ''

    def getplaid(self):
        self.PLAID_ENV = os.getenv('PLAID_ENV', 'development')
        with open(self.credentials_file) as json_file:
            data = json.load(json_file)
            self.PLAID_CLIENT_ID =  data['codes']['plaid']['PLAID_CLIENT_ID']
            self.PLAID_SECRET =  data['codes']['plaid']['PLAID_SECRET']
            self.PLAID_PUBLIC_KEY = data['codes']['plaid']['PLAID_PUBLIC_KEY']
            self.chase_access_token =  data['codes']['plaid']['chase_access_token']


def getPa():
    pa = plaidApp()
    pa.getplaid()
    pa.client = plaid.Client(client_id = pa.PLAID_CLIENT_ID, secret=pa.PLAID_SECRET,
                      public_key=pa.PLAID_PUBLIC_KEY, environment=pa.PLAID_ENV, api_version='2019-05-29')
    return pa

# # PLAID_CLIENT_ID,PLAID_SECRET,PLAID_PUBLIC_KEY,chase_access_token = getplaid()



def getBalance():
    pa = getPa()
    chase_access_token = pa.chase_access_token
    try:
        balance_response = pa.client.Accounts.balance.get(chase_access_token)
        balances = balance_response['accounts']
        for x in balances:
            if x['name'] == 'TOTAL CHECKING':
                bankbalance = x['balances']['available']
                print(bankbalance)
        return bankbalance
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

_pa = plaidApp()
bankbalance = getBalance()

# def getConnection():
#     with open(credentials_file) as json_file:
#         data = json.load(json_file)
#         return  data['codes']['connectionstring']['server'], \
#                 data['codes']['connectionstring']['user'], \
#                 data['codes']['connectionstring']['password'],  \
#                 data['codes']['connectionstring']['database']

# server,user,password,database = getConnection()

# def getuserid():
#     with open(credentials_file) as json_file:
#         data = json.load(json_file)
#         return data['codes']['userid']['id']
# userid = getuserid() 

# params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
#                                  "SERVER=" + server + ";"
#                                  "DATABASE=" + database + ";"
#                                  "UID=" + user + ";"
#                                  "PWD=" + password)

# engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
# DBSession = sessionmaker(bind = engine)
# session = DBSession()
# balance = session.query(BankBalance).filter_by(UserID = userid).one()
# balance.KeyBalance = bankbalance
# balance.DateTime = datetime.datetime.now()
# session.add(balance)
# session.commit()