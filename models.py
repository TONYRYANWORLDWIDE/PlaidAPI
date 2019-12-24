import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import urllib
import json


Base = declarative_base()
class MonthlyBills(Base):
    __tablename__ = 'monthlyBills'
    id = Column(Integer, primary_key = True)
    bill = Column(String(80), nullable = False)
    cost = Column(Float)
    date = Column(String(2))
    UserID = Column(String(128))
    
class BringHomePay(Base):
    __tablename__ = 'bringHomePay'
    id =Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    amount = Column(Float) 
    dayOfWeek =  Column(String(9))
    Frequency = Column(String(25))
    UserID = Column(String(128), nullable = False)
    
class BankBalance(Base):
    __tablename__ = 'keybalance'
    id =Column(Integer, primary_key = True)
    KeyBalance = Column(Float, nullable = False)
    DateTime = Column(DateTime, nullable = True)
    UserID = Column(String(128), nullable = False)
    AvailableBalance = Column(Float, nullable = True)