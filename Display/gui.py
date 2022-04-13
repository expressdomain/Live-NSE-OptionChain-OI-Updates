import tkcalendar as tkcal 
from datetime import datetime
from ttkwidgets.autocomplete import AutocompleteEntry
import tkinter as tk
from tkinter import ttk
import threading
import os

from utils.scrape import get_data

print(os. listdir())
with open(r"./Display/stocks.txt") as f:
    STOCKS = [x.strip() for x in f]

class Display(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.style = ttk.Style()

        self.FONT = ('Helvetice', 14)

        self.style.configure('Treeview', font = self.FONT, rowheight=30)
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

        self.__columns = ('#1', '#2', '#3', '#4', '#5')
        self.tree = ttk.Treeview(self, columns=self.__columns, show='headings', selectmode='none')
        self.tree.tag_configure('top5', background='orange')
        self.tree.column('#1', anchor=tk.CENTER)
        self.tree.column('#2', anchor=tk.CENTER)
        self.tree.column('#3', anchor=tk.CENTER)
        self.tree.column('#4', anchor=tk.CENTER)
        self.tree.column('#5', anchor=tk.CENTER)
        self.tree.heading('#1', text='Strike Prc.')
        self.tree.heading('#2', text='PE OI')
        self.tree.heading('#3', text='PE OI CNG %')
        self.tree.heading('#4', text='CE OI')
        self.tree.heading('#5', text='CE OI CNG %')
        
        self.tree.tag_configure(tagname="green", background="#4feb34")
        self.tree.tag_configure(tagname="red", background="#f03329")

        self.tree.pack(padx=10, pady=10)

        self.frame_controls = tk.Frame(self)
        self.frame_controls.pack(padx=5, pady=10)
        self.expiry_lab = tk.Label(self.frame_controls, text='Last Date: ', font=('Helvetica', 13))
        self.expiry = tkcal.DateEntry(self.frame_controls, selectmode='day')
        self.expiry_lab.grid(row=0, column=1, padx=20, pady=5)
        self.expiry.grid(row=1, column=1, padx=20, pady=5)

        
        
        self.script_label = ttk.Label(self.frame_controls, text="script", **self.font)
        self.script_var = tk.StringVar(self.frame_controls, value="NIFTY")
        self.script_entry = AutocompleteEntry(self.frame_controls, textvariable=self.script_var, width=10, completevalues=STOCKS,font=self.FONT)
        self.script_label.grid(row=0, column=0,pady=6, padx=30)
        self.script_entry.grid(row=1, column=0,pady=2, padx=30)  

        self.delay_label = ttk.Label(self.frame_controls, text="Delay (Mins)", **self.font)
        self.delay_var = tk.StringVar(value="0.5")
        self.delay_input = ttk.Entry(self.frame_controls, textvariable=self.delay_var, width=8)
        self.delay_label.grid(row=0, column=2,pady=6, padx=30)
        self.delay_input.grid(column=2, row=1, padx=2)

        self.update_btn = ttk.Button(self.frame_controls, text="Update Info", command=self.manual_update)
        self.update_btn.grid(column=3, row=0, rowspan=2, padx=2)

    def manual_update(self):
        if len(threading.enumerate()) < 2:
            self.load_data()
        else: print("thread busy")

    def load_data(self):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[REFRESH TIME] {now}")
        date = datetime.strftime(self.expiry.get_date(), '%d-%b-%Y')
        stock_name = self.script_var.get().strip()
        data = get_data(date, stock_name)
        if data is None:
            return
        data_main = sorted(data, key=lambda i: i['PE OI'], reverse=True)[:2] + sorted(data, key=lambda i: i['CE OI'], reverse=True)[:2]
        if len(data_main) > 0:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for i in range(len(data_main)):
                vals = data_main[i].values()
                self.tree.insert("", tk.END, iid=i, value=tuple(vals))
            
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