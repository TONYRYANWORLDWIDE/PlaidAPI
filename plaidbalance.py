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

credentials_file = 'C:/Users/tonyr/Desktop/PlaidAPIFinal/credentials.json'

def getplaid():
    with open(credentials_file) as json_file:
        data = json.load(json_file)
        return  data['codes']['plaid']['PLAID_CLIENT_ID'], \
                data['codes']['plaid']['PLAID_SECRET'], \
                data['codes']['plaid']['PLAID_PUBLIC_KEY'],  \
                data['codes']['plaid']['chase_access_token']
    
PLAID_CLIENT_ID,PLAID_SECRET,PLAID_PUBLIC_KEY,chase_access_token = getplaid()

PLAID_ENV = os.getenv('PLAID_ENV', 'development')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')


client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')

def getBalance(access_token):
    try:
        balance_response = client.Accounts.balance.get(access_token)
        return balance_response['accounts']
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    
balances = getBalance(chase_access_token)
for x in balances:
    if x['name'] == 'TOTAL CHECKING':
        bankbalance = x['balances']['available']
        print(bankbalance)