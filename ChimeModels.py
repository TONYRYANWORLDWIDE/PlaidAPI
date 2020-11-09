import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json
ChimeBase = declarative_base()

class ChimeTransactions(ChimeBase):
    __table_args__ = {"schema":"CMP"}
    __tablename__ = 'cTransactions'
    account_id = Column(String(55), nullable = False)
    account_owner = Column(String(55), nullable = True)
    amount = Column(Float, nullable = False)
    authorized_date = Column(String(55) , nullable = True)
    category = Column(String(55), nullable = True)
    category_id = Column(String(20), nullable = True)
    date = Column(DateTime, nullable = False)
    iso_currency_code = Column(String(55), nullable = True)
    location = Column(String(255), nullable = True)
    merchant_name = Column(String(255), nullable = True)
    name = Column(String(255), nullable = True)
    payment_channel = Column(String(55), nullable = True)
    payment_meta = Column(String(255), nullable = True)
    pending = Column(String(255), nullable = True)
    pending_transaction_id = Column(String(255), nullable = True)
    transaction_code = Column(String(255), nullable = True)
    transaction_id = Column(String(255), primary_key = True)
    transaction_type = Column(String(255), nullable = True)
    unofficial_currency_code = Column(String(255), nullable = True)