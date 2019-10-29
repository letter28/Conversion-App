# -*- coding: utf-8 -*-

import time
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import pandas as pd
import pandastable
import redis
import matplotlib
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
matplotlib.use("TkAgg")
matplotlib.style.use('bmh')
register_matplotlib_converters()

BIG_FONT = ("Consolas", 20)
MED_FONT = ("Consolas", 14)
current_rate = "BTC-USD"
programName = "btc_usd"

figure = Figure(figsize=(13, 6), facecolor="#787878", tight_layout=True)
myplot = figure.add_subplot(111)

def get_data():
    try:
        redis_db_conn = redis.Redis(host='localhost',
                                    port=6379,
                                    db=4,
                                    password=None,
                                    decode_responses=True)

        all_keys = sorted(redis_db_conn.keys())
        df = pd.DataFrame(columns=['btc_usd', 'usd_hrk', 'btc_hrk'])
        for i in range(len(all_keys)):
            row_data = redis_db_conn.hgetall(all_keys[i])
            df = df.append(row_data, ignore_index=True)
            all_keys = pd.Series(all_keys)
        df = pd.concat([all_keys, df], axis=1).set_index(0, drop=True)
        df.index.names = ["POSIX Vrijeme"]
        timestamps = df.index
        df["Vrijeme"] = [datetime.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps]
        return df
    except Exception as e:
        messagebox.showerror(str(e))

df = get_data()

def animate(most_recent):
    global df
    df = get_data()
    dates = np.array(df['Vrijeme']).astype("datetime64[s]").astype('O')
    prices = np.array(df[programName]).astype("float64")
    myplot.clear()
    myplot.plot(dates, prices)
    figure.autofmt_xdate(bottom=0.1)
    myplot.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    myplot.set_title(current_rate, fontsize=18)
    myplot.set_ylabel(current_rate[-3:], fontsize=14)
    myplot.set_xlabel("Vrijeme", fontsize=14)

class ConversionApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.homeFrame = tk.Frame(self)
        self.wm_title("BTC Conversion App")
        #Menu
        menu_bar = tk.Menu(self.homeFrame)
        refresh_menu = tk.Menu(menu_bar, tearoff=0)
        refresh_menu.add_command(label="Refresh", command=self.refresh)
        menu_bar.add_cascade(label="Refresh", menu=refresh_menu)

        self.config(menu=menu_bar)
        self.homeFrame.pack(side="top", fill="both", expand=True)
        self.homeFrame.grid_rowconfigure(0)
        self.homeFrame.grid_columnconfigure(0)

        self.frames = {}
        pages = (ConvertPage, GraphPage, TablePage)
        for f in pages:
            frame = f(self.homeFrame, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(ConvertPage)

    def refresh(self):
        pass

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class ConvertPage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.most_recent = tk.StringVar()
        most_recent_values = df.iloc[-1, :]
        btc_value_usd = float(most_recent_values['btc_usd'])

        convInfo = tk.Label(self, textvariable=self.most_recent, font=BIG_FONT)
        self.most_recent.set("Ažurirano: " + most_recent_values["Vrijeme"])
        convInfo.grid(row=1, column=2, columnspan=4)
        convInfo.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)

        self.convEntry = tk.Entry(self, width=22, justify="right", font=MED_FONT)
        self.convEntry.grid(row=2, column=1)
        self.convEntry.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convEntry.insert(0, "1")

        inputValue = float(self.convEntry.get()) 
        self.convValue = btc_value_usd * inputValue

        self.convMenu1 = ttk.Combobox(self, values=['BTC', 'HRK', 'USD'], justify="center", font=MED_FONT, width=20)
        self.convMenu1.grid(row=2, column=3)
        self.convMenu1.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convMenu1.current(0)

        self.convMenu2 = ttk.Combobox(self, values=['USD', 'HRK', 'BTC'], justify="center", font=MED_FONT, width=20)
        self.convMenu2.grid(row=2, column=6)
        self.convMenu2.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convMenu2.current(0)

        self.convLabel = tk.Entry(self, width=10, font=MED_FONT, takefocus=True, justify="center")
        self.convLabel.grid(row=2, column=5)
        self.convLabel.grid_configure(ipadx=10, ipady=10, padx=5, pady=5)
        self.convLabel.insert(0, str(self.convValue))

        button_convert = ttk.Button(self, text="Pretvori", command= self.convert)
        button_convert.grid(row=3, column=3, columnspan=3, sticky="ew")
        button_convert.grid_configure(ipadx=20, ipady=10, padx=5, pady=5)

        button_graph = ttk.Button(self, text="Grafički prikaz", command=lambda: controller.show_frame(GraphPage))
        button_graph.grid(row=4, column=1)
        button_graph.grid_configure(ipadx=10, ipady=5, padx=5, pady=5)

        button_table = ttk.Button(self, text="Tablični prikaz", command=lambda: controller.show_frame(TablePage))
        button_table.grid(row=4, column=6)
        button_table.grid_configure(ipadx=10, ipady=5, padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(7, weight=1)

    def convert(self):
        most_recent_values = df.iloc[-1, :]
        self.most_recent.set("Ažurirano: " + most_recent_values["Vrijeme"])
        btc_value_usd = float(most_recent_values['btc_usd'])
        usd_value_hrk = float(most_recent_values['usd_hrk'])
        btc_value_hrk = float(most_recent_values['btc_hrk'])

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
            self.convLabel.delete(0, tk.END)
            self.convLabel.insert(0, str(self.convValue))
        except ValueError or SyntaxError:
            messagebox.showerror("Greška", "Unesite ispravnu vrijednost.")
        except KeyError as e:
            messagebox.showerror("Error", str(e))

class GraphPage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, borderwidth=10)
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.navtoolbar = NavigationToolbar2Tk(self.canvas, self)
        self.plot_data(erate=programName)

        button_graph_convert = ttk.Button(self, text="Konverter valuta", command=lambda: controller.show_frame(ConvertPage))
        button_graph_convert.pack(side="left", padx=10, pady=10, ipadx=10, ipady=5, anchor="sw")

        button_graph_table = ttk.Button(self, text="Tablični prikaz", command=lambda: controller.show_frame(TablePage))
        button_graph_table.pack(side="right", padx=10, pady=10, ipadx=10, ipady=5, anchor="se")

        self.graph_selection = ttk.Combobox(self, values=['BTC/USD', 'USD/HRK', 'BTC/HRK'], justify="center", font=MED_FONT, width=20, state="readonly")
        self.graph_selection.current(0)
        self.graph_selection.pack(side="top", anchor="center", pady=10)

        button_update_selection = ttk.Button(self, text="Prikaži", command=lambda: self.change_exchange_rate(self.graph_selection.get()))
        button_update_selection.pack(side="bottom", padx=10, pady=10, ipadx=10, ipady=5, anchor="s")

    def change_exchange_rate(self, toWhat):
        global current_rate
        global programName
        current_rate = toWhat
        programName = current_rate.lower().replace("/", "_")
        self.plot_data(programName)

    def plot_data(self, erate):
        erate = programName
        dates = np.array(df['Vrijeme']).astype("datetime64[s]").astype('O')
        prices = np.array(df[erate]).astype("float64")
        myplot.clear()
        myplot.plot(dates, prices)
        figure.autofmt_xdate(bottom=0.1)
        myplot.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
        myplot.set_title(current_rate, fontsize=18)
        myplot.set_ylabel(current_rate[-3:], fontsize=14)
        myplot.set_xlabel("Vrijeme", fontsize=14)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(anchor="center", side="bottom", expand=True, padx=25)
        self.navtoolbar.pack(anchor="n", side="top", padx=30, pady=10)
        self.canvas._tkcanvas.pack(anchor="center", side="top", expand=True, padx=25)

class TablePage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, borderwidth=10)

        table = pandastable.Table(self, dataframe=df, height=550)
        table.grid(row=0, column=1, sticky="n")
        table.show()

        button_table_convert = ttk.Button(self, text="Konverter valuta", command=lambda: controller.show_frame(ConvertPage))
        button_table_convert.grid(row=2, column=0, ipadx=10, ipady=5, padx=50, pady=20, sticky="sw")

        button_table_graph = ttk.Button(self, text="Grafički prikaz", command=lambda: controller.show_frame(GraphPage))
        button_table_graph.grid(row=2, column=2, ipadx=10, ipady=5, padx=50, pady=20, sticky="se")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        """
        self.plot_menu = tk.Menu(self.menu_bar, tearoff=1)
        self.plot_menu.add_command(label="BTC-USD", command=lambda: self.changeRate("BTC-USD", 'btc_usd'))
        self.plot_menu.add_command(label="USD-HRK", command=lambda: self.changeRate("USD-HRK", 'usd_hrk'))
        self.plot_menu.add_command(label="BTC-USD", command=lambda: self.changeRate("BTC-HRK", 'btc_hrk'))
        self.menu_bar.add_cascade(label="Plot", menu=self.plot_menu)
        """

app = ConversionApp()

ani = animation.FuncAnimation(figure, animate, interval=60000)

app.resizable(1, 1)

app.mainloop()
