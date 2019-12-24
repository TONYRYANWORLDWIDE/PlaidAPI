import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json
import plaidbalance


balances = getBalance(chase_access_token)
for x in balances:
    if x['name'] == 'TOTAL CHECKING':
        bankbalance = x['balances']['available']
        print(bankbalance)


credentials_file = 'C:/Users/tonyr/Desktop/PlaidAPIFinal/credentials.json'


def getConnection():
    with open(credentials_file) as json_file:
        data = json.load(json_file)
        return  data['codes']['connectionstring']['server'], \
                data['codes']['connectionstring']['user'], \
                data['codes']['connectionstring']['password'],  \
                data['codes']['connectionstring']['database']

server,user,password,database = getConnection()

def getuserid():
    with open(credentials_file) as json_file:
        data = json.load(json_file)
        return data['codes']['userid']['id']
userid = getuserid() 

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=" + server + ";"
                                 "DATABASE=" + database + ";"
                                 "UID=" + user + ";"
                                 "PWD=" + password)

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

DBSession = sessionmaker(bind = engine)
session = DBSession()
balance = session.query(BankBalance).filter_by(UserID = userid).one()
balance.KeyBalance = bankbalance
session.add(balance)
session.commit()

