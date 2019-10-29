BTC Conversion App

This is a simple GUI application built using Python 3.7 and Tkinter library. It consists of 2 parts:

- a web scraper (job.py): retrieves the exchange rates (BTC/USD, USD/HRK) periodically (currently every 60 seconds),
 calculates the corresponding BTC/HRK exchange rate and inserts the values into a Redis database. Needs to be run 
 before starting the app.

- app itself (ConversionApp.py): a Tkinter application with a simple GUI, currently supporting three views:
  - currency converter
  - graphs
  - table

Environment/Requirements:
- Windows 10 (64-bit)
- Python 3.7
- Redis 3.2
- Python libraries:
	- matplotlib	3.1.0
	- pandas 	0.25.1
	- pandastable	0.12.1
	- tkinter 	Python built-in

Batch file Conversion_app_run_job.bat can be run by Windows Task Scheduler, ideally every day on startup. 
Without the web scraper running in the background, the app does not work properly.
I will also add an installer for the entire app, so it can be run on any Win10 64bit system.

Changes:
- switched the backend db to Redis
- changed the app design from Notebook tabs to Card layout
- changed the frequency of updates to once every 60 seconds
- added graphical view
- added auto-update function for the graph
- added option of changing the exchange rate to be plotted
- some styling, font(Consolas)
