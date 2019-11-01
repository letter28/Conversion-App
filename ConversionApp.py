# -*- coding: utf-8 -*-

import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import pandas as pd
import pandastable
from pandastable import config
import redis
import matplotlib
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
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
refresh_rate = 120000

figure = Figure(figsize=(16, 6), facecolor="#363636", tight_layout=True)
myplot = figure.add_subplot(1, 1, 1)


def get_data():
    try:
        redis_db_conn = redis.Redis(host='localhost',
                                    port=6379,
                                    db=4,
                                    password=None,
                                    decode_responses=True)

        all_keys = sorted(redis_db_conn.keys())
        data = pd.DataFrame(columns=['btc_usd', 'usd_hrk', 'btc_hrk'])
        for i in range(len(all_keys)):
            row_data = redis_db_conn.hgetall(all_keys[i])
            data = data.append(row_data, ignore_index=True)
            all_keys = pd.Series(all_keys)
        data = pd.concat([all_keys, data], axis=1).set_index(0, drop=True)
        data.index.names = ["POSIX Vrijeme"]
        timestamps = data.index
        data["Vrijeme"] = [datetime.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps]
        return data
    except Exception as e:
        messagebox.showerror(str(e))


global df
df = get_data()


def animate(most_recent):
    dates = np.array(df['Vrijeme']).astype("datetime64[s]").astype('O')
    prices = np.array(df[programName]).astype("float64")
    myplot.clear()
    myplot.plot(dates, prices, color="#18d9cc")
    figure.autofmt_xdate(bottom=0.1)
    myplot.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    myplot.set_title(current_rate, fontsize=18, color="#AAAAAA")
    myplot.set_ylabel(current_rate[-3:], fontsize=14, color="#AAAAAA")
    myplot.set_xlabel("Vrijeme", fontsize=14, color="#AAAAAA")


def change_refresh_rate(new):
    global refresh_rate
    refresh_rate = new * 1000


class ConversionApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.homeFrame = tk.Frame(self)
        self.wm_title("BTC Conversion App")
        # Menu
        menu_bar = tk.Menu(self.homeFrame)
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Jezik", command=self.refresh)
        settings_menu.add_command(label="Vrijeme osježavanja", command=lambda: change_refresh_rate(60))
        menu_bar.add_cascade(label="Postavke", menu=settings_menu)
        menu_bar.add_separator()

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
        tk.Frame.__init__(self, master, bg="#363636")
        self.most_recent = tk.StringVar()
        self.most_recent_values = df.iloc[-1, :]
        btc_value_usd = float(self.most_recent_values['btc_usd'])

        convInfo = tk.Label(self, textvariable=self.most_recent, font=BIG_FONT, bg="#363636", fg="#18d9cc")
        self.most_recent.set("Ažurirano: " + self.most_recent_values["Vrijeme"])
        convInfo.grid(row=0, column=2, columnspan=4, ipadx=10, ipady=5, padx=5, pady=5)

        self.convEntry = tk.Entry(self, width=22, justify="center", font=MED_FONT)
        self.convEntry.grid(row=2, column=1, ipadx=10, ipady=5, padx=5, pady=5)
        self.convEntry.insert(0, "1")

        self.inputValue = float(self.convEntry.get())
        self.convValue = btc_value_usd * self.inputValue

        self.convMenu1 = ttk.Combobox(self, values=['BTC', 'HRK', 'USD'], justify="center", font=MED_FONT, width=20)
        self.convMenu1.grid(row=2, column=3, ipadx=10, ipady=5, padx=5, pady=5)
        self.convMenu1.current(0)

        self.convLabel = tk.Entry(self, width=22, font=MED_FONT, takefocus=True, justify="center")
        self.convLabel.grid(row=2, column=5, ipadx=10, ipady=5, padx=5, pady=5)
        self.convLabel.insert(0, str(self.convValue))

        self.convMenu2 = ttk.Combobox(self, values=['USD', 'HRK', 'BTC'], justify="center", font=MED_FONT, width=20)
        self.convMenu2.grid(row=2, column=6, ipadx=10, ipady=5, padx=5, pady=5)
        self.convMenu2.current(0)

        button_convert = tk.Button(self, text="Pretvori", command=self.convert, bg="#363636", fg="#18d9cc",
                                   font=MED_FONT)
        button_convert.grid(row=3, column=3, columnspan=3, ipadx=10, ipady=5, padx=5, pady=5)

        button_graph = tk.Button(self, text="Grafički prikaz", bg="#363636", fg="#18d9cc", font=MED_FONT,
                                 command=lambda: controller.show_frame(GraphPage))
        button_graph.grid(row=5, column=7, ipadx=10, ipady=5, padx=5, pady=5)

        button_table = tk.Button(self, text="Tablični prikaz", bg="#363636", fg="#18d9cc", font=MED_FONT,
                                 command=lambda: controller.show_frame(TablePage))
        button_table.grid(row=5, column=0, ipadx=10, ipady=5, padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(7, weight=1)

        self.listenerC = self.after(refresh_rate, self.update_after)

    def update_after(self):
        df = get_data()
        self.most_recent_values = df.iloc[-1, :]
        self.most_recent.set("Ažurirano: " + self.most_recent_values["Vrijeme"])
        self.listenerC = self.after(refresh_rate, self.update_after)

    def convert(self):
        btc_value_usd = float(self.most_recent_values['btc_usd'])
        usd_value_hrk = float(self.most_recent_values['usd_hrk'])
        btc_value_hrk = float(self.most_recent_values['btc_hrk'])

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
        tk.Frame.__init__(self, master, borderwidth=20, bg="#363636")
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.navtoolbar = NavigationToolbar2Tk(self.canvas, self)
        self.navtoolbar.config(background="#363636")
        self.navtoolbar.message_label.config(fg="#AAAAAA", background="#363636")
        self.navtoolbar.update()
        self.plot_data()

        button_graph_convert = tk.Button(self, text="Konverter valuta", bg="#363636", fg="#18d9cc", font=MED_FONT,
                                         command=lambda: controller.show_frame(ConvertPage))
        button_graph_convert.pack(side="left", padx=10, pady=10, ipadx=10, ipady=5, anchor="sw")

        button_graph_table = tk.Button(self, text="Tablični prikaz", bg="#363636", fg="#18d9cc", font=MED_FONT,
                                       command=lambda: controller.show_frame(TablePage))
        button_graph_table.pack(side="right", padx=10, pady=10, ipadx=10, ipady=5, anchor="se")

        self.graph_selection = ttk.Combobox(self, values=['BTC/USD', 'USD/HRK', 'BTC/HRK'], justify="center",
                                            font=MED_FONT, width=20, state="readonly")
        self.graph_selection.current(0)
        self.graph_selection.pack(side="top", anchor="center", pady=10)

        button_update_selection = tk.Button(self, text="Prikaži", bg="#363636", fg="#18d9cc", font=MED_FONT,
                                            command=lambda: self.change_exchange_rate(self.graph_selection.get()))
        button_update_selection.pack(side="bottom", padx=10, pady=10, ipadx=10, ipady=5, anchor="s")

    def change_exchange_rate(self, toWhat):
        global current_rate
        global programName
        current_rate = toWhat
        programName = current_rate.lower().replace("/", "_")
        self.plot_data()

    def plot_data(self):
        dates = np.array(df['Vrijeme']).astype("datetime64[s]").astype('O')
        prices = np.array(df[programName]).astype("float64")
        myplot.clear()
        myplot.plot(dates, prices, color="#18d9cc")
        figure.autofmt_xdate(bottom=0.1)
        myplot.set_facecolor("#363636")
        myplot.spines['bottom'].set_color("#363636")
        myplot.spines['top'].set_color("#363636")
        myplot.spines['left'].set_color("#363636")
        myplot.spines['right'].set_color("#363636")
        myplot.tick_params(axis='both', colors="#999999")
        myplot.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
        myplot.set_title(current_rate, fontsize=18, color="#AAAAAA")
        myplot.set_ylabel(current_rate[-3:], fontsize=14, color="#AAAAAA")
        myplot.set_xlabel("Vrijeme", fontsize=14, color="#AAAAAA")
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(anchor="center", side="bottom", expand=True, padx=25)
        self.navtoolbar.pack(anchor="n", side="top", padx=30, pady=10)
        self.canvas.tkcanvas.pack(anchor="center", side="top", expand=True, padx=25)


class TablePage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, borderwidth=10, bg="#363636")

        self.table = pandastable.Table(self, dataframe=df, height=550, columns=4)
        self.table.grid()
        options = {'align': 'c',
                   'cellbackgr': '#303030',
                   'cellwidth': 200,
                   'colheadercolor': '#393939',
                   'entrybackgr': '#393939',
                   'floatprecision': 6,
                   'font': 'Consolas',
                   'fontsize': 12,
                   'grid_color': '#ABB1AD',
                   'linewidth': 1,
                   'rowheight': 22,
                   'rowselectedcolor': '#555555',
                   'textcolor': '#AAAAAA'
                   }
        config.apply_options(options, self.table)
        # self.table.autoResizeColumns()
        self.table.show()

        button_table_graph = tk.Button(self, text="Grafički prikaz", font=MED_FONT, bg="#363636", fg="#18d9cc",
                                       command=lambda: controller.show_frame(GraphPage))
        button_table_graph.grid(row=3, column=0, ipadx=10, ipady=5, padx=50, pady=20)

        button_table_convert = tk.Button(self, text="Konverter valuta", font=MED_FONT, bg="#363636", fg="#18d9cc",
                                         command=lambda: controller.show_frame(ConvertPage))
        button_table_convert.grid(row=3, column=3, ipadx=10, ipady=5, padx=50, pady=20)

        self.grid_rowconfigure(3, weight=1)

        self.listenerT = self.after(refresh_rate, self.update_after)

    def update_after(self):
        df = get_data()
        self.table.model.df = df
        self.table.redraw()
        self.listenerT = self.after(refresh_rate, self.update_after)


app = ConversionApp()

ani = animation.FuncAnimation(figure, animate, interval=refresh_rate)

app.mainloop()
