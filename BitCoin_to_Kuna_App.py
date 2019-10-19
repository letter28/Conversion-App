# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 23:56:30 2019

@author: Leon
"""

from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
import pandas as pd
import pandastable

class Conversion_App(object):
    #TODO: napisati funkciju za dohvat vrijednosti valuta

    def __init__(self, master):
        self.home_frame = ttk.Notebook(master)
        self.home_frame.grid(sticky="nsew")
        self.home_frame.grid_configure(ipadx=10, ipady=10, padx=10, pady=10)
        
#        homeLabel = ttk.Label(self.home_frame, text="Dobrodošli u aplikaciju za pretvorbu i računanje!")
#        homeLabel.grid()
        
        self.master = master
        self.createContent()
  
    def createContent(self):
        today = date.today().strftime("%Y-%m-%d")
        sql_connection = pymysql.connect(host='127.0.0.1',
                                    user='Leon',
                                    password='password',
                                    db='default_schema')

        query = f"SELECT * FROM exchange_rates;"

        all_values = pd.read_sql_query(query, sql_connection)
        btc_value_usd = all_values['btc/usd'][all_values.size / 4 - 1]
        print(all_values)

        """-------------------------------------------Currency Calculator--------------------------------------------------"""
        self.convTab = ttk.Frame(self.home_frame, borderwidth=20)
        self.convTab.grid(columnspan=6)
        self.convTab.grid_configure(ipadx=10, ipady=10, padx=10, pady=10)

        self.convInfo = ttk.Label(self.convTab, text=f"Vrijednosti valuta na dan: {today}")
        self.convInfo.grid(row=0, column=2, columnspan=3)
        self.convInfo.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)

        self.convEntry = ttk.Entry(self.convTab, width=25, justify="right")
        self.convEntry.grid(row=1, column=0)
        self.convEntry.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convEntry.insert(0, "1")

        self.inputValue = float(self.convEntry.get()) 

        self.convValue = btc_value_usd * self.inputValue

        self.convMenu1 = ttk.Combobox(self.convTab, values=['BTC', 'HRK', 'USD'], justify="right")
        self.convMenu1.grid(row=1, column=2)
        self.convMenu1.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convMenu1.current(0)

        self.convMenu2 = ttk.Combobox(self.convTab, values=['USD', 'HRK', 'BTC'], justify="right")
        self.convMenu2.grid(row=1, column=5)
        self.convMenu2.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convMenu2.current(0)

        self.convLabel = ttk.Label(self.convTab, text=f" = {self.convValue}")
        self.convLabel.grid(row=1, column=4)
        self.convLabel.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)

        self.button_convert = ttk.Button(self.convTab, text="Pretvori", command=self.convert)
        self.button_convert.grid(row=2, column=2, columnspan=3)
        self.button_convert.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)

        self.home_frame.add(self.convTab, text = "Tečajni kalkulator")
        
        """---------------------------------------------Graphical representation-----------------------------------------"""
        self.graphTab = ttk.Frame(self.home_frame, borderwidth=20)
        self.graphTab.grid(columnspan=6)
        self.graphTab.grid_configure(ipadx=10, ipady=10, padx=10, pady=10)

        self.home_frame.add(self.graphTab, text = "Grafički prikaz tečaja")

        """---------------------------------------------Tabular representation-------------------------------------------"""
        self.tableTab = ttk.Frame(self.home_frame, borderwidth=20)
        self.tableTab.grid(columnspan=4)
        self.tableTab.grid_configure(ipadx=10, ipady=10, padx=10, pady=10)

        self.table = pandastable.Table(self.tableTab, dataframe=all_values, showtoolbar=True, showstatusbar=True)
        self.table.grid(row=0, column=0, columnspan=4)
        self.table.show()
        self.home_frame.add(self.tableTab, text = "Tablični prikaz tečaja")


    def convert(self):
        #Making a connection with the db and extracting values from a resulting pandas DataFrame
        today = date.today().strftime("%Y-%m-%d")
        sql_connection = pymysql.connect(host='127.0.0.1',
                                    user='Leon',
                                    password='password',
                                    db='default_schema')

        query = f"SELECT * FROM exchange_rates WHERE date = '{today}';"

        todays_values = pd.read_sql_query(query, sql_connection, index_col='date')

        btc_value_usd = todays_values['btc/usd'][0]
        usd_value_hrk = todays_values['usd/hrk'][0]
        btc_value_hrk = todays_values['btc/hrk'][0]
        
        #Conversion of values
        try:
            if self.convMenu1.get() == 'BTC':
                if self.convMenu2.get() == 'USD':
                    self.convValue = round(float(self.convEntry.get()) * btc_value_usd, 2)
                elif self.convMenu2.get() == 'HRK':
                    self.convValue = round(float(self.convEntry.get()) * btc_value_hrk, 2)
                else:
                    self.convValue = self.convEntry.get()
            elif self.convMenu1.get() == 'HRK':
                if self.convMenu2.get() == 'USD':
                    self.convValue = round(float(self.convEntry.get()) / usd_value_hrk, 2)
                elif self.convMenu2.get() == 'BTC':
                    self.convValue = round(float(self.convEntry.get()) / btc_value_hrk, 8)
                else:
                    self.convValue = self.convEntry.get()
            else:
                if self.convMenu2.get() == 'HRK':
                    self.convValue = round(float(self.convEntry.get()) * usd_value_hrk, 2)
                elif self.convMenu2.get() == 'BTC':
                    self.convValue = round(float(self.convEntry.get()) / btc_value_usd, 8)
                else:
                    self.convValue = self.convEntry.get()
            self.convLabel["text"] = f" = {self.convValue}"
        except ValueError or SyntaxError:
            messagebox.showerror("Greška", "Unesite ispravnu vrijednost.")

root = tk.Tk()

app = Conversion_App(root)

root.mainloop()