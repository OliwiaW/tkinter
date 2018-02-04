# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 18:46:58 2017

@author: Właściciel
"""

# zapis i odczyt z bazy danych do csv
# testy
# dokumentacja

import app
from tkinter import messagebox as mBox
    
def main():
    ap = app.APP()
    ap.win.mainloop()

try:
    if __name__ == "__main__":
        main()
except Exception as e: 
    mBox.showerror('Error', e)
    exit()


#main()      
