import tkcalendar as tkcal 
from datetime import datetime
from ttkwidgets.autocomplete import AutocompleteEntry
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
import threading

from utils.scrape import get_data

with open(r"./Display/stocks.txt") as f:
    STOCKS = [x.strip() for x in f]

class Display(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.style = ttk.Style()

        self.FONT = ('Helvetice', 14)

        self.style.configure('Treeview', font = self.FONT, rowheight=30)
        self.style.configure('Treeview.Heading', font = self.FONT)
        self.style.configure('my.Radiobutton', font = self.FONT)

        self.font = {
            'font': self.FONT
        }

        self.cur_stock_var = tk.StringVar(self)
        self.cur_stock_lab = tk.Label(self, textvariable = self.cur_stock_var, font= self.FONT)
        self.cur_stock_lab.pack(pady=10)
        
        self.last_updated_var = tk.StringVar(self)
        self.last_updated_lab = tk.Label(self, textvariable = self.last_updated_var, font= self.FONT)
        self.last_updated_lab.pack(pady=5)

        self.__columns = ('#1', '#2', '#3')
        self.tree = ttk.Treeview(self, columns=self.__columns, show='headings', selectmode='browse')
        self.tree.column('#1', anchor=tk.CENTER)
        self.tree.column('#2', anchor=tk.CENTER)
        self.tree.column('#3', anchor=tk.CENTER)
        self.tree.heading('#1', text='Strike Prc.')
        self.tree.heading('#2', text='PE OI')
        self.tree.heading('#3', text='CE OI')
        
        self.tree.tag_configure(tagname="green", background="#4feb34")
        self.tree.tag_configure(tagname="red", background="#f03329")

        self.tree.pack(padx=10, pady=10)

        self.frame_controls = tk.Frame(self)
        self.frame_controls.pack(padx=5, pady=10)
        self.expiry_lab = tk.Label(self.frame_controls, text='Last Date', font=self.FONT)
        self.expiry = tkcal.DateEntry(self.frame_controls, selectmode='day')
        self.expiry_lab.grid(row=0, column=1, padx=20, pady=5)
        self.expiry.grid(row=1, column=1, padx=20, pady=5)

        
        
        self.script_label = ttk.Label(self.frame_controls, text="Script", **self.font)
        self.script_var = tk.StringVar(self.frame_controls, value="NIFTY")
        self.script_entry = AutocompleteEntry(self.frame_controls, textvariable=self.script_var, width=10, completevalues=STOCKS,font=self.FONT)
        self.script_label.grid(row=0, column=0,pady=6, padx=30)
        self.script_entry.grid(row=1, column=0,pady=2, padx=30)  

        self.delay_label = ttk.Label(self.frame_controls, text="Delay (Mins)", **self.font)
        self.delay_var = tk.StringVar(value="60")
        self.delay_input = ttk.Entry(self.frame_controls, textvariable=self.delay_var, width=8)
        self.delay_label.grid(row=0, column=2,pady=6, padx=30)
        self.delay_input.grid(column=2, row=1, padx=2)

        self.update_btn = ttk.Button(self.frame_controls, text="Update Info", command=self.manual_update)
        self.update_btn.grid(column=3, row=0, rowspan=2, padx=2)
         # prepare data
        self.data = {
            'CE' : 0,
            'PE' : 0
        }
        options = self.data.keys()
        total_OI = self.data.values()

        # create a figure
        self.figure = Figure(figsize=(3, 2), dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self.parent)

        # create the toolbar
        NavigationToolbar2Tk(self.figure_canvas, self.parent)

        # create axes
        self.axes = self.figure.add_subplot()

        # create the barchart
        self.axes.bar(options, total_OI)
        self.axes.set_title('Total OI')
        self.axes.set_ylabel('OI')

        self.figure_canvas.get_tk_widget().pack(padx=10,side=tk.RIGHT, fill=tk.BOTH, expand=1)

        self.OI_diff_percent_var = tk.StringVar(self)
        self.OI_diff_percent_lab = tk.Label(self, textvariable = self.OI_diff_percent_var, font= ('Helvetice', 15, 'bold'))
        self.OI_diff_percent_lab.pack(pady=5)

    def manual_update(self):
        if len(threading.enumerate()) < 2:
            self.load_data()
        else: print("thread busy")

    def load_data(self):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[REFRESH TIME] {now}")
        date = datetime.strftime(self.expiry.get_date(), '%d-%b-%Y')
        stock_name = self.script_var.get().strip()
        raw_data = get_data(date, stock_name)
        data = raw_data[0]
        if data is None:
            return
        data_main = sorted(data, key=lambda i: i['PE OI'], reverse=True)[:2] + sorted(data, key=lambda i: i['CE OI'], reverse=True)[:2]
        if len(data_main) > 0:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for i in range(len(data_main)):
                vals = data_main[i].values()
                self.tree.insert("", tk.END, iid=i, value=tuple(vals))
            self.data = raw_data[1]
            options = self.data.keys()
            total_OI = self.data.values()
            diff_per = round(((self.data["CE"] - self.data["PE"]) / self.data["CE"]) * 100, 2)
            self.OI_diff_percent_var.set(f"OI Difference: {diff_per}%")
            if diff_per > 0:
                self.OI_diff_percent_lab.config(fg="green")
            else:
                self.OI_diff_percent_lab.config(fg="red")
            self.axes.clear()
            self.axes.bar(options, total_OI, color=["green", "red"])
            self.axes.set_title(stock_name)
            self.axes.set_ylabel('OI')
            
            self.figure.canvas.draw()

            self.figure.canvas.flush_events()
            self.parent.update()
            self.cur_stock_var.set("Current Stock: " + stock_name)
            now = datetime.now().strftime("%H:%M:%S")
            self.last_updated_var.set("Last Updated: " + now)
    
    def refresh(self):
        self.t1 = threading.Thread(target=self.load_data, daemon=True)
        self.t1.start()
        delay = int(float(self.delay_var.get()) * 60 * 1000)
        self.parent.after(delay, self.refresh)

'''root = tk.Tk()
a = Display(root)
a.pack(side="top", fill="both", expand=True)
a.refresh()

root.mainloop()'''
