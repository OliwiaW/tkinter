# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:26:23 2017

@author: wojtkoo
"""

import tkinter as tk
from tkinter import ttk
from tkinter import Menu
import pandas as pd
import numpy as np
from tkinter import messagebox as mBox
import pickle
import os
import datetime
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from tkcalendar import Calendar
from PIL import Image, ImageTk
from io import BytesIO
import urllib.request
import smtplib



import widgets, model, tooltip, database_connector, download_currency, twitter

class APP():
    
    currency = 1
    course = download_currency.insert_into_database_Euro()
    currency_str = " Euros"
    warning = False
    
    
    def __init__(self): 
        
        self.win = tk.Tk() 
        self.win.configure(background="#2B1B17")
        self.win.title("Car price predictor")
        # fullscreen
        self.win.geometry("{0}x{1}+0+0".format(self.win.winfo_screenwidth(),
                                       self.win.winfo_screenheight()))
        
        try:
            self.win.iconbitmap(os.getcwd()+"\car-icon.ico")
            self.columns = pickle.load( open( "columns.pickle", "rb" ) )
            self.RandomForestRegressor = pickle.load( open( "model.pickle", "rb" ) )
            self.autos = pickle.load( open( "data_cleaned.pickle", "rb" ) )
            self.models_list = database_connector.read_from_Models()
            self.scaler = pickle.load( open( "scaler.pickle", "rb" ) )
        except ImportError:
            mBox.showerror('Import Error', 'One of the needed files cannot be load !', icon='error')
        else:     
            # define all variables for tab1
            self.seller, self.vehicle_type, self.gearbox , self.brand, self.model, self.fuel = \
                    tk.StringVar(), tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar()
                    
            self.seller, self.vehicle_type, self.gearbox , self.brand, self.model, self.fuel = "","","","","",""
            self.month_of_production = 1
            self.price = 0
            self.notRepairedDamage = 0
            
            # define all variables for tab2
            self.year_of_production, self.month_of_production, self.kilometers = \
                    tk.IntVar(), tk.IntVar(), tk.IntVar()
            
            # define all variables for tab3
            self.variable_for_x_ax = tk.StringVar()
            self.variable_for_x_ax = "brand"           
            self.list_of_var_to_plot = ["seller", "vehicleType", "gearbox" , "brand", "fuelType"]
            
            self.currency_on_plot = tk.StringVar()
            self.currency_on_plot = "Euro"
            # create app's elements
            self.create_menubar()
            self.createWidgets()        
        
    def create_menubar(self):
        
        menuBar = Menu(self.win)
        self.win.config(menu=menuBar)
        
        main_menu = Menu(menuBar)
        main_menu.add_command(label="refresh data", command=self.refresh_data)
        main_menu.add_command(label="author", command=self.about)
        main_menu.add_command(label="send email", command=self.send_mail)
        main_menu.add_command(label="Exit", command=self.quit)
        menuBar.add_cascade(label="Menu", menu=main_menu)
        
        currency_menu = Menu(menuBar)
        currency_menu.add_command(label="Euros", command=self.currency_euros)
        currency_menu.add_command(label="PLN", command=self.currency_pln)
        menuBar.add_cascade(label="Currency", menu=currency_menu)
        
    def quit(self):
        self.win.quit()
        self.win.destroy()
        exit()
        
    def about(self):
        mBox.showinfo('author', 'Created by Oliwia Wojtkowska, 2017', icon='info')
        
    def send_mail(self):
        self.email_popup = tk.Toplevel(self.win)
        tk.Label(self.email_popup,text="Write an email:").pack()
        self.email_entry = tk.Entry(self.email_popup)
        self.email_entry.pack()
        tk.Button(self.email_popup,text='Send',command=self.send_email_2).pack()
        
    def send_email_2(self):

        email_address = []
        email_address.append(self.email_entry.get())
        self.email_popup.destroy()

        SERVER = "192.168.1.100"
        
        FROM = "autos@email_sender.com"
        TO = email_address # must be a list
        
        SUBJECT = "Auto price prediction"
        
        TEXT = "This message was sent with Python's smtplib."
        
        message = """\
        From: %s
        To: %s
        Subject: %s\n
        %s
        """ % (FROM, TO, SUBJECT, TEXT)
        
        # Send the mail
        
        server = smtplib.SMTP(SERVER)
        server.sendmail(FROM, TO, message)
        server.quit()
        
    def refresh_data(self):
        answer = mBox.askquestion("Caution", "Process might take few minutes,\ndo you want to continue?", icon='warning')
        print(answer)
        if answer == 'yes':
            columns = ['seller', 'vehicleType', 'price', 'yearOfRegistration', 'monthOfRegistration',\
                       'brand', 'model', 'kilometer', 'fuelType', 'notRepairedDamage', 'gearbox']
            new_autos = database_connector.read_from_Autos()
            new_autos = pd.DataFrame([record for record in new_autos], columns=columns)
            new_autos.to_csv('autos.csv', encoding = "cp1252")
            new_autos = model.load_data()
            model.prepare_data(new_autos)
            mBox.showinfo('Success', 'Refreshing data process is done ! ', icon='info')
        
        
        
    def currency_euros(self):
        self.currency = 1
        self.currency_str = " Euros"
        
    def currency_pln(self):
        self.currency = self.course 
        self.currency_str = " PLN"
        
    def choose_currency(self, selected):
        if str(selected) == "Euro":
            self.currency_euros()
            self.axis.clear()
            self.create_plot_price()
        else:
            self.currency_pln()
            self.axis.clear()
            self.create_plot_price()
    
    def predict(self):
        #if (isinstance(self.year_of_production , int)) & (isinstance(self.kilometers , int)): 
        
        try:
            self.year_of_production = int(self.year_of_production_entry.get())
            self.kilometers = int(self.kilometers_entry.get())
        except ValueError:
            mBox.showerror('Value Error', 'Wrong type of variables: production or kilometers !', icon= 'error')
            return 0
        else:   
            # check data
            if (self.year_of_production<1900) | (self.year_of_production>datetime.datetime.now().year) | (self.kilometers<0):
                mBox.showerror('Type Error', 'Wrong values for year of production or kilometers !', icon='error')
                return 0    
            
            df_to_predict = pd.DataFrame([], columns = self.columns)
            df_to_predict.drop(["price"], axis=1, inplace=True)
            
            # create row(dataframe with only 0 row) for prediction
            df_to_predict.loc[0,"kilometer"] = self.kilometers
            df_to_predict.loc[0, "age"] = (datetime.datetime.now().year-(int(self.year_of_production)) -1 )*12 + (12-int(self.month_of_production)) + datetime.datetime.now().month
            df_to_predict.loc[0, "notRepairedDamage"] = self.notRepairedDamage
    
            # fill apriopriate columns with 1 
            try :
                col_names = ["seller_"+self.seller, "vehicleType_"+self.vehicle_type, "brand_"+self.brand, \
                         "model_"+self.model, "fuelType_"+self.fuel, "gearbox_"+self.gearbox]
            except KeyError:
                mBox.showerror('Key Error', 'Wrong column names in Pandas dataframe !\n\
                                Try to generate a new file named "columns.pickle"', icon='error')
                return 0
            
            for col in col_names:
                df_to_predict.loc[0, col] = 1
            
            # fill other columns as not chosen - 0                 
            df_to_predict = df_to_predict.fillna(0)            
            
            # use scaler to transform data to be in range (0,1)
            df_to_predict[['kilometer', "age"]] = self.scaler.transform(df_to_predict[['kilometer', "age"]])
            print("df_to_predict : ", df_to_predict)
            # predict price and show in message box
            self.price = self.RandomForestRegressor.predict(df_to_predict)[0]
            
            mBox.showinfo('Prediction', 'Suggested price:\n{}{}'.format(round(self.price*self.currency), self.currency_str), icon='info')
        
        
    def create_model(self): 
        answer = mBox.askquestion("Caution", "Process might take few minutes,\ndo you want to continue?", icon='warning')
        print(answer)
        if answer == 'yes':
            try:
                self.n_estimators = self.n_estimators_entry.get()
                self.max_features = self.max_features_entry.get()
                self.max_depth = self.max_depth_entry.get()
                self.random_state = self.random_state_entry.get()
            except TypeError:
                mBox.showerror('Type Error', 'Wrong type of variables !', icon='error')
                return 0
            else:   
                # create and test model using model.py module
                scores = model.create_model(self.n_estimators, self.max_features, self.max_depth, self.random_state)
                
                # in case of exception in scores
                if scores==0:
                    return 0
                
                scores = round(scores,2)
                
                # show model score and detailes in the label
                mBox.showinfo('Bravo !', "You've just created new model !\n Model R^2 score: {}".format(scores), icon='info')
                string = "n_estimators: {}, max_features: {}, max_depth: {}, random_state: {}\t R^2: {}\n".\
                                        format(self.n_estimators, self.max_features, self.max_depth, self.random_state, scores)
                self.results_label.configure(text=(self.results_label.cget("text") + string))
                
                # save model in database Models:
                self.add_model_to_database()
    
    # below functions to set given values in variables
    def select_seller(self, selected):
        self.seller = selected

    def select_vehicle_type(self, selected):
        self.vehicle_type = selected
        
    def select_gearbox(self, selected):
        self.gearbox = selected
        
    def select_brand(self, selected):
        self.brand = selected   
        self.combo_model['values'] = list(self.autos[self.autos["brand"]==selected]["model"].unique())
        
    def select_model(self, selected):
        self.model = selected    
        
    def select_fuel(self, selected):
        self.fuel = selected
        
    def select_year_of_production(self, selected):
        self.year_of_production = selected
         
    def select_month_of_production(self, selected):
        self.month_of_production = selected
         
    def select_kilometers(self, selected):
        self.kilometers = selected

    def select_notRepairedDamage(self):
        if self.notRepairedDamage==1:
            self.button_notRepairedDamage.configure(bg = "gray")
            self.notRepairedDamage=0.0
        else:
            self.button_notRepairedDamage.configure(bg = "yellow")
            self.notRepairedDamage=1.0
    
    def select_variable_for_x_ax(self, selected):
        self.variable_for_x_ax = selected
        self.axis.clear()
        self.create_plot_price()
        
                
    # toolitip for tab2 entires        
    def createToolTip(self, widget, text):
        toolTip = tooltip.ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)        
            
    def add_auto_to_database(self):
        
        values = [self.seller, self.vehicleType, self.price, self.yearOfRegistration, self.monthOfRegistration, self.brand, self.model,\
                  self.kilometer, self.fuelType, self.notRepairedDamage, self.gearbox] 
        
        database_connector.insert_into_database_Autos(values)
        
    def add_model_to_database(self):
        
        values = [self.n_estimators, self.max_features, self.max_depth, self.random_state, self.score]
        
        #database_connector.insert_into_database_Models(values)

    
    def refresh_euro_plot(self):
        self.date_from = self.calendar1.selection_get()
        self.date_to = self.calendar2.selection_get()
        self.axis_2.clear()
        self.create_plot_Euro_course()
        
        
    def createWidgets(self):
        # Create Tab Control
        tabControl = ttk.Notebook(self.win) 
        # create an universal label to create all widgets by calling its function
        universal_label = widgets.Label()
        universal_combobox = widgets.Combobox()
        universal_entry = widgets.Entry()
        
        #---------------------------------------------------------------------------------------------------------
        tab1 = tk.Frame(tabControl, bg = "#2B1B17") # Create a tab 
        tabControl.add(tab1, text='Predict Price') # Add the tab
        
        ttk.Label(tab1, text="Enter parameters to predict price", background="#2B1B17", foreground="#FFF2D1", font=("Vivaldi", 22)).\
                 grid(columnspan=4, column=1, row=0, padx=40, pady = 20)
     
        tk.Button(tab1, text="Predict price", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 20), command= self.predict)\
                 .grid(column=1, row=(5), columnspan=3, pady=40)
                 
        tk.Button(tab1, text="Add record to database", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 20), command= self.add_auto_to_database)\
                 .grid(column=4, row=(5), pady=40)
        
        # create a frame for tab1
        labelsFrame_1 = tk.LabelFrame(tab1, bg="#2B1B17")
        labelsFrame_1.grid(column=1, row=1,columnspan=5,rowspan=4, padx = 20, pady=40) 
        
        photo1 = tk.PhotoImage(file=os.getcwd()+"\img1.png")
        img1 = tk.Label(tab1, image = photo1)
        img1.image = photo1
        img1.grid(column=0, row = 1, rowspan = 3, padx=20, pady=40)
        
        universal_label.create_widget(labelsFrame_1, text="seller:", column=0, row=0)
        universal_label.create_widget(labelsFrame_1, text="vehicle type:", column=1, row=(0))
        universal_label.create_widget(labelsFrame_1, text="gearbox:",column=2, row=(0))
        universal_label.create_widget(labelsFrame_1, text="brand:", column=3, row=(0))
        universal_label.create_widget(labelsFrame_1, text="model:", column=4, row=(0))
        
        universal_label.create_widget(labelsFrame_1, text="year of production:", column=0, row=3)
        universal_label.create_widget(labelsFrame_1, text="month of production:", column=1, row=(3))
        universal_label.create_widget(labelsFrame_1, text="kilometers:", column=2, row=(3))
        universal_label.create_widget(labelsFrame_1, text="fuel:", column=3, row=(3))
        universal_label.create_widget(labelsFrame_1, text="have not repaired damage", column=4, row=(3))
        
        list_of_models = []
        self.combo_seller = universal_combobox.create_widget(labelsFrame_1, self.seller, ("private", "company"), column=0, row=1)
        self.combo_seller.bind("<<ComboboxSelected>>", lambda event: self.select_seller(self.combo_seller.get()))
        self.combo_vehicle_type = universal_combobox.create_widget(labelsFrame_1, self.vehicle_type, (list(self.autos["vehicleType"].unique())), column=1, row=1)
        self.combo_vehicle_type.bind("<<ComboboxSelected>>", lambda event: self.select_vehicle_type(self.combo_vehicle_type.get()))
        self.combo_gearbox = universal_combobox.create_widget(labelsFrame_1, self.gearbox, (list(self.autos["gearbox"].unique())), column=2, row=1)
        self.combo_gearbox.bind("<<ComboboxSelected>>", lambda event: self.select_gearbox(self.combo_gearbox.get()))
        self.combo_brand = universal_combobox.create_widget(labelsFrame_1, self.brand, (list(self.autos["brand"].unique())), column=3, row=1)
        self.combo_brand.bind("<<ComboboxSelected>>", lambda event: self.select_brand(self.combo_brand.get()))
        self.combo_model = universal_combobox.create_widget(labelsFrame_1, self.model, list_of_models, column=4, row=1)
        self.combo_model.bind("<<ComboboxSelected>>", lambda event: self.select_model(self.combo_model.get()))
        
        self.year_of_production_entry = universal_entry.create_widget(labelsFrame_1, textvariable=self.year_of_production, column=0, row=4)
        self.combo_month_of_production = universal_combobox.create_widget(labelsFrame_1, self.month_of_production, (list(np.arange(1,13))), column=1, row=4)
        self.combo_month_of_production.bind("<<ComboboxSelected>>", lambda event: self.select_month_of_production(self.combo_month_of_production.get()))
        self.kilometers_entry = universal_entry.create_widget(labelsFrame_1, textvariable=self.kilometers, column=2, row=4)
        self.combo_fuel = universal_combobox.create_widget(labelsFrame_1, self.fuel, (list(self.autos["fuelType"].unique())), column=3, row=4)
        self.combo_fuel.bind("<<ComboboxSelected>>", lambda event: self.select_fuel(self.combo_fuel.get()))
        
        self.button_notRepairedDamage = tk.Button(labelsFrame_1, text="Yes", background="gray", foreground="#FFA500", \
                                                  font=("Vivaldi", 16), command= self.select_notRepairedDamage)
        self.button_notRepairedDamage.grid(column=4, row=(4), padx = 40)
        
        #---------------------------------------------------------------------------------------------------------
        # create widgets for tab2
        tab2 = tk.Frame(tabControl, bg = "#2B1B17")
        tabControl.add(tab2, text='Create model')
        
        photo2 = tk.PhotoImage(file=os.getcwd()+"\img2.png")
        img2 = tk.Label(tab2, image = photo2)
        img2.image = photo2
        img2.grid(column=0, row = 1, rowspan = 3, padx=20, pady=40)
        
        ttk.Label(tab2, text="Enter parameters to create model", background="#2B1B17", foreground="#FFF2D1", font=("Vivaldi", 22)).\
                 grid(columnspan=3, column=1, row=0, padx=40, pady = 20)
        
        tk.Button(tab2, text="Create model", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 20), \
                  command=self.create_model).grid(column=1, row=(3), columnspan=3)
        
        labelsFrame_2 = tk.LabelFrame(tab2, bg="#2B1B17")
        labelsFrame_2.grid(column=1, row=1, columnspan=3,rowspan=2, padx=40)
        
        universal_label.create_widget(labelsFrame_2, text="number of estimators:", column=0, row=0)
        universal_label.create_widget(labelsFrame_2, text="max features:", column=1, row=(0))
        universal_label.create_widget(labelsFrame_2, text="max depth:", column=2, row=(0))
        universal_label.create_widget(labelsFrame_2, text="random state:", column=3, row=(0))
        
        self.n_estimators, self.max_features, self.max_depth, self.random_state = tk.IntVar(value=10), tk.IntVar(value=int(len(self.columns))-1), tk.IntVar(value=10), tk.IntVar(value=10)
        
        self.n_estimators_entry = universal_entry.create_widget(labelsFrame_2, textvariable=self.n_estimators, column=0, row=1)
        self.max_features_entry = universal_entry.create_widget(labelsFrame_2, textvariable=self.max_features, column=1, row=1)
        self.max_depth_entry = universal_entry.create_widget(labelsFrame_2, textvariable=self.max_depth, column=2, row=1)
        self.random_state_entry = universal_entry.create_widget(labelsFrame_2, textvariable=self.random_state, column=3, row=1)
        self.createToolTip(self.n_estimators_entry, 'The maximum number of estimators at which boosting is terminated')
        self.createToolTip(self.max_features_entry, 'The number of features to consider when looking for the best split')
        self.createToolTip(self.max_depth_entry, 'The maximum depth of the tree')
        
        setattr(universal_label, 'columnspan', 3)
        self.results_label = universal_label.create_widget(tab2, text=self.models_list, column=2, row=4)
        
        tabControl.pack(expand=2, fill="both")
        
        #---------------------------------------------------------------------------------------------------------
        # create widgets for tab3
        self.tab3 = tk.Frame(tabControl, bg = "#2B1B17")
        tabControl.add(self.tab3, text='Show dependency price plot') # Add the tab
        
        title = "Price dependence"
        ttk.Label(self.tab3, text=title, background="#2B1B17", foreground="#FFF2D1", font=("Vivaldi", 22)).pack()
        
        photo3 = tk.PhotoImage(file=os.getcwd()+"\img3.png")
        img3 = tk.Label(self.tab3, image = photo3)
        img3.image = photo3
        img3.pack(side="left", padx=40)
        
        # create plot for the first time
        self.fig = Figure(facecolor='#2B1B17', figsize = (8,6))
        self.axis = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab3)
        self.create_plot_price()
        self.canvas._tkcanvas.pack(side="left")
        self.fig.tight_layout()
        toolbar = NavigationToolbar2TkAgg(self.canvas, self.tab3)
        toolbar.update()
        
        ttk.Label(self.tab3, text="Show price variability", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 22)).\
                 pack(pady = 40)
                 
        self.combo_variable_for_x_ax = ttk.Combobox(self.tab3, width=20, textvariable= self.variable_for_x_ax)
        self.combo_variable_for_x_ax["values"] = self.list_of_var_to_plot
        self.combo_variable_for_x_ax.bind("<<ComboboxSelected>>", lambda event: self.select_variable_for_x_ax(self.combo_variable_for_x_ax.get()))
        self.combo_variable_for_x_ax.pack(pady = 40)
        
        ttk.Label(self.tab3, text="Choose currency", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 22)).\
                 pack(pady = 40)
        
        self.combo_currency = ttk.Combobox(self.tab3, width=20, textvariable= self.currency_on_plot)
        self.combo_currency["values"] = ["Euro", "PLN"]
        self.combo_currency.bind("<<ComboboxSelected>>", lambda event: self.choose_currency(self.combo_currency.get()))
        self.combo_currency.pack(pady = 40)
        
        self.tab3.update()
        
        #---------------------------------------------------------------------------------------------------------
        # create widgets for tab4
        self.tab4 = tk.Frame(tabControl, bg = "#2B1B17")
        tabControl.add(self.tab4, text='Show currency plot') # Add the tab
        
        title = "Euro Course"
        ttk.Label(self.tab4, text=title, background="#2B1B17", foreground="#FFF2D1", font=("Vivaldi", 22)).pack()
        
        photo4 = tk.PhotoImage(file=os.getcwd()+"\img4.png")
        img4 = tk.Label(self.tab4, image = photo4)
        img4.image = photo4
        img4.pack(side="left", padx=20)
        
        self.date_to = time.strftime("%Y-%m-%d")
        self.date_from = datetime.date.today() - datetime.timedelta(30)
        
        self.fig_2 = Figure(facecolor='#2B1B17', figsize = (10,6))
        self.axis_2 = self.fig_2.add_subplot(111)
        self.canvas_2 = FigureCanvasTkAgg(self.fig_2, master=self.tab4)
        self.create_plot_Euro_course()
        self.canvas_2._tkcanvas.pack(side="left")
        self.fig_2.tight_layout()
        
        toolbar_2 = NavigationToolbar2TkAgg(self.canvas, self.tab4)
        toolbar_2.update()
          
        tk.Button(self.tab4, text="refresh plot", command=lambda : self.refresh_euro_plot(), background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 16)).pack()
        
        ttk.Label(self.tab4, text="Date from:", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 16)).\
                 pack()
        
        self.calendar1 = Calendar(self.tab4, font="Vivaldi 12",background = '#2B1B17', foreground = '#FFF2D1',
               normalbackground= '#2B1B17', normalforeground = '#FFF2D1',
               selectbackground = '#FFA500', weekendbackground = '#2B1B17', weekendforeground = '#FFF2D1',
               year = datetime.date.today().year, month = datetime.date.today().month, day = datetime.date.today().day)
        
        self.calendar1.pack(fill="both", expand=True)
        
        ttk.Label(self.tab4, text="Date to:", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 16)).\
                 pack()
        
        self.calendar2 = Calendar(self.tab4, font="Vivaldi 12",background = '#2B1B17', foreground = '#FFF2D1',
               normalbackground= '#2B1B17', normalforeground = '#FFF2D1',
               selectbackground = '#FFA500', weekendbackground = '#2B1B17', weekendforeground = '#FFF2D1')
        self.calendar2.pack(fill="both", expand=True)
        
        
        self.tab4.update()
        #---------------------------------------------------------------------------------------
        """
        self.tab5 = tk.Frame(tabControl, bg = "#2B1B17")
        tabControl.add(self.tab5, text='Show social media info') # Add the tab
        
        ttk.Label(self.tab5, text="Twitter", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 22))\
                .grid(column=2, row=1, padx = 40, pady=40)
                
        ttk.Label(self.tab5, text="Facebook", background="#2B1B17", foreground="#FFA500", font=("Vivaldi", 22))\
                .grid(column=6, row=1, padx = 40, pady=40)
         
        if (len(str(self.brand))==0) & (len(str(self.model))==0):
            query = "#cars"
        else:
            query = "#" + str(self.brand) + str(self.model)
        
        tweet_string = twitter.search_tweets(query)
                
        #scrollbar = tk.Scrollbar(self.tab5)
        twitter_txt = tk.Text(self.tab5, height=5, width=60, font = ("Arial", 12))
        twitter_txt.grid(column=2, row=3, padx = 40, pady = 40)
        #scrollbar.grid(column=3, row=3)
        #scrollbar.config(command=twitter_txt.yview)
        #twitter_txt.config(yscrollcommand=scrollbar.set)
        #for tweet, url in zip(tweet_strings, media_urls):
        twitter_txt.insert('end',tweet_string)
         
        fb_string = twitter.facebook()
                
        #fb_scrollbar = tk.Scrollbar(self.tab5)
        facebook_txt = tk.Text(self.tab5, height=5, width=60, font = ("Arial", 12))
        #fb_scrollbar.grid(column=7, row=3)
        facebook_txt.grid(column=6, row=3, padx = 40, pady = 40)
        #fb_scrollbar.config(command=facebook_txt.yview)
        #facebook_txt.config(yscrollcommand=scrollbar.set)
        facebook_txt.insert('end',fb_string.encode('windows-1250', 'ignore'))
        
        photo_twitter = "image_twitter.png"
        photo_twitter = tk.PhotoImage(file=os.getcwd()+"\img1.png")
#        photo_twitter = Image.open(photo_twitter)
#        photo_twitter = ImageTk.PhotoImage(photo_twitter)
#        
#        photo_twitter_witdh = photo_twitter.size[0]
#        photo_twitter_height = photo_twitter.size[1]
#        standard_picture_witdh = 200
#        if photo_twitter_witdh>standard_picture_witdh:
#            percent = 100 / (photo_twitter_witdh /  standard_picture_witdh)
#            photo_twitter_witdh = photo_twitter_witdh * percent/100
#            photo_twitter_height =  photo_twitter_height * percent/100
#        photo_twitter = photo_twitter.resize((photo_twitter_height, photo_twitter_witdh), Image.ANTIALIAS)
        img_twitter = tk.Label(self.tab5, image = photo_twitter)
        img_twitter.image = photo_twitter
        img_twitter.grid(column=2, row=5, padx = 40, pady = 40)
        
        photo_fb = "image_fb.png"
        photo_fb = tk.PhotoImage(file=os.getcwd()+"\image_fb.png")
#        photo_fb = Image.open(photo_fb)
#        photo_fb = ImageTk.PhotoImage(photo_fb)
#        
#        photo_fb_witdh = photo_fb.size[0]
#        photo_fb_height = photo_fb.size[1]
#        standard_picture_witdh = 200
#        if photo_fb_witdh>standard_picture_witdh:
#            percent = 100 / (photo_fb_witdh /  standard_picture_witdh)
#            photo_fb_witdh = photo_fb_witdh * percent/100
#            photo_fb_height =  photo_fb_height * percent/100
#        photo_fb = photo_fb.resize((photo_fb_height, photo_fb_witdh), Image.ANTIALIAS)
        img_fb = tk.Label(self.tab5, image = photo_fb)
        img_fb.image = photo_fb
        img_fb.grid(column=6, row=5, padx = 40, pady = 40)
        
        
        #url_photo_fb = urlopen(url_fb).read()
        #image_photo_fb = Image.open(BytesIO(url_photo_fb))
        #photo_fb = tk.PhotoImage(image_photo_fb)
        #img_fb = tk.Label(self.tab5, image = photo_fb)
        #img_fb.image = photo_twitter
        #img_fb.grid(column=6, row=5, padx = 40, pady = 40)
        
        
        self.tab5.update()
        """
        
        #---------------------------------------------------------------------------------------------------------
        tabControl.pack(expand=2, fill="both")
        

    def create_plot_price(self):
        
        try:
            self.data_to_plot = self.autos[[self.variable_for_x_ax, "price"]]
        except KeyError:
            mBox.showerror('Key Error', 'Wrong column names in Pandas dataframe !\n\
                                Try to generate a new file named "data_cleaned.pickle"', icon='error')
            return 0

        self.data_to_plot["price"] = self.data_to_plot["price"]*self.currency
        self.data_to_plot.boxplot(column=['price'], by=self.variable_for_x_ax, ax=self.axis, rot=90)
        self.axis.set_xlabel(str.title(str(self.variable_for_x_ax)), fontsize = 16)
        self.axis.set_ylabel('Price in %s' %self.currency_str, fontsize = 16)
        self.axis.xaxis.label.set_color('white')
        self.axis.yaxis.label.set_color('white')
        self.fig.suptitle('')
      
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
               
    def create_plot_Euro_course(self):
         
         date, course = download_currency.read_from_Euro(str(self.date_from), str(self.date_to))
         x = range(len(date))
         self.axis_2.plot(x,course, color = '#FFA500', linewidth=4)
         self.axis_2.grid(True)
         self.axis_2.set_xticks(x)
         self.axis_2.set_xticklabels(date, rotation=90)
         #self.axis_2.plot_date(course)
         self.axis_2.set_xlabel("Date", fontsize = 16)
         self.axis_2.set_ylabel('Price', fontsize=16)
         self.axis_2.xaxis.label.set_color('white')
         self.axis_2.yaxis.label.set_color('white')
         self.fig.suptitle('')
      
         self.canvas_2.draw()
         self.canvas_2.get_tk_widget().pack()
         


