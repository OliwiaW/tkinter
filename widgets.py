# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 15:59:19 2017

@author: wojtkoo
"""


from tkinter import ttk

class Widget():
    
    _bg="#2B1B17"
    _fg="#FFF2D1"
    _font=("Vivaldi", 16)
    _width=20
    _padx = 40
    _pady = 20
    _columnspan=1
    
    def __init__(self):
        pass # nic sie nie dzieje, ale nastepuje stworzenie pustego obiektu
        
    def create_widget(self, labelsFrame, column, row):
        self._labelsFrame = labelsFrame
        self._column = column
        self._row = row
    
class Label(Widget):
    
    def create_widget(self, labelsFrame, text, column, row):
        super() # dziedziczy z clasy Widget
        lb = ttk.Label(labelsFrame, text=text, background=self._bg, foreground=self._fg, font=self._font)
        lb.grid(column = column, row=row, padx=self._padx, pady = self._pady, columnspan=self._columnspan)
        return lb
    
class Combobox(Widget):

    def create_widget(self, labelsFrame, textvariable, values, column, row):
        super()
        cb = ttk.Combobox(labelsFrame, width=self._width, textvariable=textvariable)
        cb["values"] = values
        cb.grid(column = column, row=row)
        return cb
    
class Entry(Widget):
    
    def create_widget(self, labelsFrame, textvariable, column, row):
        super()
        en = ttk.Entry(labelsFrame, width=self._width, textvariable=textvariable)
        en.grid(column = column, row=row)
        return en
        
        
        