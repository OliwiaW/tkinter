# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 16:38:24 2017

@author: Właściciel
"""

# do 10.11.2017
import pypyodbc
import pandas as pd

euro_df = pd.read_excel('Euro.xlsx')

connection = pypyodbc.connect('Driver={SQL Server};'
    
                                    'Server=abd.wwsi.edu.pl;'
    
                                    'Database=JiPPZ507;'
    
                                    'uid=JiPPowojtkowska;pwd=%s' %'qazwsx123456')
cursor = connection.cursor() 
SQLCommand = ("INSERT INTO Euro "
             "(date, course) "
             "VALUES (?, ?)")

for nr, row in euro_df.iterrows():
    cursor.execute(SQLCommand,[row[0],row[1]]) 

connection.commit()

connection.close()

import main
main.main()