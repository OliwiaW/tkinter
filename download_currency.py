# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 20:50:39 2017

@author: Właściciel
"""

from bs4 import BeautifulSoup
import requests
import pypyodbc
import pickle
from tkinter import messagebox as mBox
import os
import time

def download_currency():
    address = ("https://www.bankier.pl/waluty/kursy-walut/nbp/EUR")
    data = requests.get(address)
    soup = BeautifulSoup(data.content, "html.parser")
    currency_value = soup.find('td', class_='textBold').text.strip()[:-3]
    currency_value = float(currency_value.replace("," , "."))
    return currency_value

def open_connection():
    if os.path.isfile('password.pickle'):
        password = pickle.load( open( "password.pickle", "rb" ) )
        try:
            connection = pypyodbc.connect('Driver={SQL Server};'
    
                                    'Server=abd.wwsi.edu.pl;'
    
                                    'Database=JiPPZ507;'
    
                                    'uid=JiPPowojtkowska;pwd=%s' %password)
        except pypyodbc.Error as e:
            mBox.showerror('Database Connection Error', e)
            return 0
        else:
            return connection
    else:
        mBox.showerror('Import Error', "File named 'password.pickle' cannot be load !")
        return 0

def close_connection(connection):
    connection.close()
    
def insert_into_database_Euro():
    currency_value = download_currency()
    #current_date = time.strftime("%d/%m/%Y")
    current_date = time.strftime("%Y-%m-%d")
    connection = open_connection()
    cursor = connection.cursor() 
    SQLCommand = ("SELECT course FROM Euro WHERE date = '{}'".format(current_date))
    results = cursor.execute(SQLCommand)
    results = cursor.fetchall()

    if len(results)==0:
        SQLCommand = ("INSERT INTO Euro "
                         "(date, course) "
                         "VALUES (?, ?)")
        
        cursor.execute(SQLCommand, [current_date, currency_value]) 
        connection.commit()
    #else:
    #    mBox.showinfo('Info', 'Euro currency for today is already in database')
            
    close_connection(connection)
        
    return currency_value
    
def read_from_Euro(date_from, date_to):
    date = []
    course = []
    connection = open_connection()
    if connection:
        cursor = connection.cursor() 
        SQLCommand = ("SELECT * FROM Euro WHERE date BETWEEN '{}' and '{}' order by date".format(date_from, date_to)) 
        results = cursor.execute(SQLCommand)
        results = cursor.fetchall()
        for row in results:
            date.append(row[0])
            course.append(row[1])
        close_connection(connection)
    return date, course