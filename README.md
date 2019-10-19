BTC Conversion App

This is a simple GUI application built using Python 3.7 and Tkinter library. It consists of 2 parts:

- a web scraper .py file: retrieves the exchange rates (BTC/USD, USD/HRK) once daily,
 calculates the corresponding BTC/HRK exchange rate and inserts the values into a MySQL database.

- app itself (BitCoin_to_Kuna_App.py): a Tkinter application with a simple GUI - a tab for Currency conversion,
 and a tab for inspecting the data, with values retreived from a MySQL database. Third tab with graphical
 representation of data will be added later.

Environment/Requirements:
- Windows 10 (64-bit)
- Python 3.7
- MySQL 8.0.17 (Server and Router needed for the app, Workbench optional)
- MySQL Connector/Python (3.7) 8.0.17
- Python libraries: 
	- pandas 	0.25.1
	- pandastable	0.12.1
	- PyMySQL	0.9.3
	- tkinter 	Python built-in

Web scraper currently supports the getting of exchange rates once daily, which will be changed to a couple times a day, 
 every few hours to get better data on the BTC/USD exchange rate. Also, MySQL DB will be replaced by a more efficient and 
 faster Redis DB (SQL to NoSQL). I will also add an installer for the entire app, so it can be run on any Win10 64bit system.		
