from datetime import datetime

import customtkinter as ctk
from customtkinter import END

from tkinter import messagebox

from docutils.nodes import entry
from sqlalchemy.orm import sessionmaker
from models import engine, ConvertionHistory
from exeptions import NegativeValueError, EmptyFieldError

import requests
import csv


Session = sessionmaker(bind=engine)
API_KEY = "cur_live_GUJDzvVikvIXbtcgPJcvbjIDdULbWFfYvgmHM6Dh"


def get_sorted_conversions(ascending=True):
    with Session() as session:
        order = ConvertionHistory.date_of_creation.asc() if ascending else ConvertionHistory.date_of_creation.desc()
        conversions_history = session.query(ConvertionHistory).order_by(order).all()

        return conversions_history

def get_all_records_as_a_dict(ascending):
    conversions_history = get_sorted_conversions(ascending)

    conversion_dict = [
    {
        "from currency": c.from_currency,
        "to currency": c.to_currency,
        "amount": c.amount,
        "result": c.result,
        "date of creation": c.date_of_creation.strftime("%Y-%m-%d %H:%M:%S")
    }
    for c in conversions_history
    ]

    return conversion_dict


class ConvertEaseApp(ctk.CTk):  # Inherits from the CTk class
    def __init__(self):
        super().__init__()

        self.title("ConvertEase")
        self.geometry("450x600")  # Adjusted size for better spacing

        self.theme_color = "dark"
        ctk.set_appearance_mode(self.theme_color)

        self.bind("<Escape>", self.close_window)

        # Title Label
        self.label_for_conversion = ctk.CTkLabel(self, text="Convert Currencies", font=("Helvetica", 24, "bold"))
        self.label_for_conversion.pack(pady=(15, 30))

        # Entry for Amount
        self.entry_for_amount = ctk.CTkEntry(self, placeholder_text="Amount", justify="center", width=200)
        self.entry_for_amount.pack(pady=(20,10))

        # From Currency Label and Entry
        self.from_currency_label = ctk.CTkLabel(self, text="From Currency:", font=("Helvetica", 12))
        self.from_currency_label.pack(pady=(15,5))

        self.entry_for_currency_to_convert = ctk.CTkEntry(
            self,
            placeholder_text="e.g. USD",
            justify="center",
            width=70
        )
        self.entry_for_currency_to_convert.pack(pady=10)

        self.swap_currency_button = ctk.CTkButton(self,
                                                  text="🔄",
                                                  width=40,
                                                  command=self.swap_currency_places)
        self.swap_currency_button.pack(pady=20)

        # To Currency Label and Entry
        self.to_currency_label = ctk.CTkLabel(self, text="To Currency:", font=("Helvetica", 12))
        self.to_currency_label.pack(pady=5)


        self.entry_for_currency_wanted = ctk.CTkEntry(
            self,
            placeholder_text="e.g. EUR",
            justify="center",
            width=70
        )
        self.entry_for_currency_wanted.pack(pady=10)

        # Convert Button
        self.convert_button = ctk.CTkButton(self, text="Convert", command=self.convert_currency, width=200)
        self.convert_button.pack(pady=(25, 15))

        # Result Label
        self.result_label = ctk.CTkLabel(self,
            text="No conversion yet",
            font=("Helvetica", 16, "bold"),
            text_color="white",
            fg_color="green",
            corner_radius=5,
            padx=10,
            pady=5
        )
        self.result_label.pack(pady=15)

        self.see_history_button = ctk.CTkButton(self,
                                                text="See Convertion History",
                                                command=self.open_history_window
                                                )
        self.see_history_button.pack(pady=20)

    def convert_currency(self):
        self.result_label.configure(text="Loading...")
        self.update_idletasks()

        amount = self.entry_for_amount.get()
        from_currency = self.entry_for_currency_to_convert.get().upper()
        to_currency = self.entry_for_currency_wanted.get().upper()

        try:
            if amount.strip() == "":
                raise EmptyFieldError

            amount = float(amount)

            if amount < 0:
                raise NegativeValueError

            if from_currency.strip() == "" or to_currency.strip() == "":
                raise EmptyFieldError
        except ValueError:
            messagebox.showerror("Error", "The amount must be of float type!")
            return
        except NegativeValueError:
            messagebox.showerror("Error", "The amount must be a positive number")
            return
        except EmptyFieldError:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        URL = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies={to_currency}&base_currency={from_currency}"

        response = requests.get(URL)
        data = response.json()

        if "errors" in data.keys():
            messagebox.showerror("Error", "Please select a valid currency")
            return

        result = round(data["data"][to_currency]["value"] * amount, 2)
        self.result_label.configure(text=f"Converted {amount} {from_currency} to {to_currency} = {result}")

        with Session() as session:
            convertion_history_record = ConvertionHistory(
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                result=result,
                date_of_creation=datetime.now()
            )

            session.add(convertion_history_record)
            session.commit()

            messagebox.showinfo("Success", "Conversion recorded successfully!")

    def swap_currency_places(self):
        from_currency_value = self.entry_for_currency_to_convert.get()
        to_currency_value = self.entry_for_currency_wanted.get()

        self.entry_for_currency_to_convert.delete(0, END)
        self.entry_for_currency_wanted.delete(0, END)

        self.entry_for_currency_to_convert.insert(0, to_currency_value)
        self.entry_for_currency_wanted.insert(0, from_currency_value)

    def open_history_window(self):
        sort_records = False  # Start with default sorting order

        def add_to_frame():
            conversions_history = get_sorted_conversions(ascending=sort_records)

            for conversion in conversions_history:
                row_info = (f"{conversion.date_of_creation.strftime('%Y-%m-%d %H:%M:%S')} - "
                            f"{conversion.amount} {conversion.from_currency} -> "
                            f"{conversion.to_currency} = {conversion.result}")

                label_record = ctk.CTkLabel(
                    history_frame,
                    text=row_info,
                    font=("Helvetica", 12),
                    justify="center",
                    wraplength=300,
                    anchor="w"
                )
                label_record.pack(pady=5)

        def clear_history_frame():
            for widget in history_frame.winfo_children():
                widget.destroy()

        def refresh_field():
            clear_history_frame()
            add_to_frame()

        def change_sort_value():
            nonlocal sort_records
            sort_records = not sort_records  # Toggle sorting flag

            # Update button text based on sorting order
            button_sorting.configure(text="Sort by latest" if sort_records else "Sort by earliest")

            refresh_field()  # Refresh the display

        def get_csv_file_of_history():
            history_dict = get_all_records_as_a_dict(sort_records)
            with open("convertion_history.csv", "w", newline="") as csvfile:
                fieldnames = ["date of creation", "from currency", "to currency", "amount", "result"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|")
                writer.writeheader()
                writer.writerows(history_dict)

        history_window = ctk.CTkToplevel()
        history_window.title("History of transactions")
        history_window.geometry("440x400")

        history_window.bind("<Escape>", self.close_window)

        history_label = ctk.CTkLabel(history_window, text="Convertion History:", font=("Helvetica", 20))
        history_label.pack(pady=6)

        button_sorting = ctk.CTkButton(
            history_window,
            text="Sort by earliest",  # Default state
            command=change_sort_value
        )
        button_sorting.pack(pady=15)

        history_frame = ctk.CTkScrollableFrame(history_window, width=320, orientation="vertical")
        history_frame.pack(pady=15)

        add_to_frame()  # Populate frame with initial data

        get_csv_file_button = ctk.CTkButton(history_window, text="Get History as CSV", command=get_csv_file_of_history,
                                            width=200)
        get_csv_file_button.pack(pady=10)

    def close_window(self, event=None):
        answer = messagebox.askyesno("Are you sure?", "Are you sure you want to quit. the application?")

        if answer:
            self.destroy()


if __name__ == '__main__':
    app = ConvertEaseApp()
    app.mainloop()
