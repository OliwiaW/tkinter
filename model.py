# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 14:25:38 2017

@author: wojtkoo
"""
import pandas as pd
import numpy as np
import datetime
import pickle

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
#from sklearn.model_selection import cross_val_predict
#from sklearn.tree import DecisionTreeRegressor
#from sklearn.ensemble import AdaBoostRegressor
#from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import r2_score
from tkinter import messagebox as mBox
import os

# create files:
# - data_cleaned.pickle -> after load function
# - columns.pickle -> list of auto's columns after get_dummies function
# - scaler.pickle -> need for client's example prediction
# - data_ready_to_train.pickle -> data after cleaning, get_dummies and MinMaxScaler
# - model.pickle -> save model after training
# - data_to_plot.pickle -> data for further plotting in application



def load_data():
    if not os.path.isfile('autos.csv'):
        mBox.showerror('Import Error', "File named 'autos.csv' cannot be load !")
        quit()
        return 0
        
    autos = pd.read_csv("autos.csv", index_col = 0, encoding = "cp1252")
    autos = autos.loc[:, ["seller", "vehicleType", "price", "yearOfRegistration", "monthOfRegistration", "brand", "model", "kilometer", "fuelType", "notRepairedDamage", "gearbox"]]
    autos = autos.drop_duplicates()
    autos["notRepairedDamage"] = autos["notRepairedDamage"].fillna(value = 0)
    autos["notRepairedDamage"] = [1 if x!=0 else x for x in autos["notRepairedDamage"]]
    autos = autos.dropna()
    autos = autos[(autos["price"]<15000) & (autos["yearOfRegistration"]>1990)]
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    autos["age"]= [(year-y-1)*12 + 12-x + month for x,y in zip(autos["monthOfRegistration"], autos["yearOfRegistration"])  ]
    autos = autos.drop(["monthOfRegistration","yearOfRegistration"], axis=1)
    autos = autos.reset_index(drop=True)
    
    # translate to english:
        
    dic_translate = {"andere":"other", "elektro":"electro", "kleinwagen":"small","nan":0, "nein":0,"ja":1,"privat":"private",\
                         "gewerblich":"company","benzin":"petrol", "manuell":"manual", "automatik":"automatic"}
    column_to_translate = ["fuelType", "vehicleType","seller","brand","model","gearbox"]
    for column in column_to_translate:
        autos[column] = [ dic_translate[x] if x in dic_translate.keys() else x for x in autos[column] ]
    
    
    pickle.dump(autos, open("data_cleaned.pickle", 'wb'))
    return autos

def prepare_data(autos):
    
    autos = pd.get_dummies(autos, columns=["seller","vehicleType","brand","model", "fuelType", "gearbox"])
    
    pickle.dump(list(autos.columns.values), open("columns.pickle", 'wb'))
    
    scaler = MinMaxScaler().fit(autos[['kilometer', "age"]])
    autos[['kilometer', "age"]] = scaler.transform(autos[['kilometer', "age"]])
    
    pickle.dump(scaler, open("scaler.pickle", 'wb'))
    
    pickle.dump(autos, open("data_ready_to_train.pickle", 'wb'))
    return autos

def create_model(n_estimators, max_features, max_depth, random_state):
    
    autos = load_data()
    autos = prepare_data(autos)
    
    model = RandomForestRegressor(n_estimators=int(n_estimators), max_features=int(max_features), max_depth=int(max_depth), random_state=int(random_state)).fit(autos.drop(["price"],axis=1), autos["price"])
    #model  = AdaBoostRegressor(DecisionTreeRegressor\
    #                           (max_features=int(max_features), max_depth=int(max_depth)),
    #                        n_estimators=int(n_estimators), random_state=int(random_state))
    X = autos.drop(["price"],axis=1)
    y = autos["price"]
    model= model.fit(X,y)
    pickle.dump(model, open("model.pickle", 'wb'))
    y_pred = model.predict(X)
    
    #svd = TruncatedSVD(n_components=2, n_iter=7, random_state=int(random_state))
    #X_2_dim = svd.fit_transform(X)
    
    #evr = svd.explained_variance_ratio_.sum()
    r2 = r2_score(y, y_pred)# multioutput='raw_values'
    
    #pickle.dump([X_2_dim ,r2,evr], open("data_to_plot.pickle", 'wb'))
    scores = np.mean(r2)
    #scores = model.score(X,y)
    print(scores)
    return scores