# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 23:44:44 2017

@author: Właściciel
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 23:27:34 2017

@author: Właściciel
"""
import pypyodbc
import pandas as pd
"""
connection = pypyodbc.connect('Driver={SQL Server};'

                                'Server=abd.wwsi.edu.pl;'

                                'Database=JiPPZ507;'

                                'uid=JiPPowojtkowska;pwd=qazwsx123456')
    


cursor = connection.cursor() 
SQLCommand = ("INSERT INTO Autos "
                 "(seller, vehicleType, price, yearOfRegistration, monthOfRegistration, brand, model, kilometer, fuelType, notRepairedDamage, gearbox) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

autos = pd.read_csv("autos.csv", index_col = 0, encoding = "cp1252")
autos = autos.loc[:, ["seller", "vehicleType", "price", "yearOfRegistration", "monthOfRegistration", "brand", "model", "kilometer", "fuelType", "notRepairedDamage", "gearbox"]]
autos = autos.drop_duplicates()
autos["notRepairedDamage"] = autos["notRepairedDamage"].fillna(value = 0)
autos["notRepairedDamage"] = [1 if x!=0 else x for x in autos["notRepairedDamage"]]
autos = autos.dropna()
autos = autos[(autos["price"]<15000) & (autos["yearOfRegistration"]>1990)]
autos = autos.reset_index(drop=True)
dic_translate = {"andere":"other", "elektro":"electro", "kleinwagen":"small","nan":0, "nein":0,"ja":1,"privat":"private",\
                     "gewerblich":"company","benzin":"petrol", "manuell":"manual", "automatik":"automatic"}
column_to_translate = ["fuelType", "vehicleType","seller","brand","model","gearbox"]
for column in column_to_translate:
        autos[column] = [ dic_translate[x] if x in dic_translate.keys() else x for x in autos[column] ]
    
for index, row in autos.iterrows():
     cursor.execute(SQLCommand,[x for x in row]) 
     connection.commit()
connection.close()
"""