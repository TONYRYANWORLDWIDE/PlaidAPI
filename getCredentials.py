import base64
import os
import sys
import datetime
import json
import time
import urllib
import requests
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import plaid

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


def get_access_token():
    global access_token
    public_token = 'public-development-985370d5-31a1-4048-98b3-c9ad8063d7be'
    
    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        print(e.message)
        return
    access_token = exchange_response['access_token']
#     return jsonify(exchange_response)
    print('turkey')
    print(access_token)


get_access_token()