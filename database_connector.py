# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 22:15:03 2017

@author: Właściciel
"""
"""
create table JiPPowojtkowska.Autos
    (seller varchar(255),
	vehicleType varchar(255),
	price INT,
	yearOfRegistration INT,
	monthOfRegistration INT, 
	brand varchar(255), 
	model varchar(255), 
	kilometer INT, 
	fuelType varchar(255), 
	notRepairedDamage INT, 
	gearbox varchar(255)
); 
    
create table JiPPowojtkowska.Models(
   n_estimators INT, 
   max_features INT, 
   max_depth INT, 
   random_state INT, 
   score FLOAT
);
"""

# password = "qazwsx123456"

import pypyodbc
import pickle
from tkinter import messagebox as mBox
import os

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
    
def insert_into_database_Autos(values):
    # values has to be a list :
    # [self.seller, self.vehicleType, self.price, self.yearOfRegistration, self.monthOfRegistration, \
    # self.brand, self.model, self.kilometer, self.fuelType, self.notRepairedDamage, self.gearbox] 
    connection = open_connection()
    if connection:
        cursor = connection.cursor() 
        SQLCommand = ("INSERT INTO Autos "
                     "(seller, vehicleType, price, yearOfRegistration, monthOfRegistration, brand, model, kilometer, fuelType, notRepairedDamage, gearbox) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    
        cursor.execute(SQLCommand,values) 
        connection.commit()
        
        close_connection(connection)
    
def insert_into_database_Models(values):
    # values has to be a list :
    # [n_estimators, max_features, max_depth, random_state, score]
    connection = open_connection()
    if connection:
        cursor = connection.cursor() 
        SQLCommand = ("INSERT INTO Models "
                     "(n_estimators, max_features, max_depth, random_state, score) "
                     "VALUES (?, ?, ?, ?, ?)")
    
        cursor.execute(SQLCommand,values) 
        connection.commit()
        
        close_connection(connection)
    
def read_from_Autos_to_plot(variable_for_x_ax):
    df_to_plot = []
    connection = open_connection()
    if connection!=0:
        cursor = connection.cursor() 
        SQLCommand = ("SELECT ?, price "
                      "FROM Autos ") 
        values = [variable_for_x_ax ]
        results = cursor.execute(SQLCommand,values)
        while results:
            df_to_plot.append(results)
        close_connection(connection)
        return df_to_plot
    else:
        return None
    
def read_from_Autos():
    autos = []
    connection = open_connection()
    if connection:
        cursor = connection.cursor() 
        SQLCommand = ("SELECT * FROM Autos ") 
        results = cursor.execute(SQLCommand)
        results = cursor.fetchall()
        for row in results:
            autos.append(row)
        close_connection(connection)
        return autos
    else:      
        return None
    
def read_from_Models():
    models = ""
    connection = open_connection()
    if connection:
        cursor = connection.cursor() 
        SQLCommand = ("SELECT top 3 * FROM Models order by score desc") 
        results = cursor.execute(SQLCommand)
        results = cursor.fetchall()
        for row in results:
            models += "n_estimators: {}, max_features: {}, max_depth: {}, random_state: {}\t R^2: {}\n".\
                                    format(row[0], row[1], row[2], row[3], row[4])
        close_connection(connection)
    return models