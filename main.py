from datetime import datetime

import customtkinter as ctk
from customtkinter import END

from tkinter import messagebox

from sqlalchemy.orm import sessionmaker
from models import engine, ConvertionHistory
from exeptions import NegativeValueError, EmptyFieldError

import requests


Session = sessionmaker(bind=engine)
API_KEY = "cur_live_GUJDzvVikvIXbtcgPJcvbjIDdULbWFfYvgmHM6Dh"


class ConvertEaseApp(ctk.CTk):  # Inherits from the CTk class
    def __init__(self):
        super().__init__()

        self.title("ConvertEase")
        self.geometry("450x520")  # Adjusted size for better spacing

        self.theme_color = "dark"
        ctk.set_appearance_mode(self.theme_color)

        # Title Label
        self.label_for_conversion = ctk.CTkLabel(self, text="Convert Currencies", font=("Helvetica", 24, "bold"))
        self.label_for_conversion.pack(pady=(20, 10))

        # Entry for Amount
        self.entry_for_amount = ctk.CTkEntry(self, placeholder_text="Amount", justify="center", width=200)
        self.entry_for_amount.pack(pady=10)

        # From Currency Label and Entry
        self.from_currency_label = ctk.CTkLabel(self, text="From Currency:", font=("Helvetica", 12))
        self.from_currency_label.pack(pady=5)

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
        self.swap_currency_button.pack(pady=15)

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
        self.convert_button.pack(pady=20)

        # Result Label
        self.result_label = ctk.CTkLabel(self, text="No convertion yet", font=("Helvetica", 14), text_color="green")
        self.result_label.pack(pady=15)

        self.see_history_button = ctk.CTkButton(self,
                                                text="See Convertion History",
                                                command=self.open_history_window
                                                )
        self.see_history_button.pack(pady=5)

    def convert_currency(self):
        try:
            amount = float(self.entry_for_amount.get())

            if amount < 0:
                raise NegativeValueError

            from_currency = self.entry_for_currency_to_convert.get().upper()
            to_currency = self.entry_for_currency_wanted.get().upper()

            if from_currency.split() == "" or to_currency.split() == "":
                raise EmptyFieldError
        except ValueError:
            messagebox.showerror("Error", "The amount must be of float type!")
            return
        except NegativeValueError:
            messagebox.showerror("Error", "The amount must be a positive number")
            return
        except EmptyFieldError:
            messagebox.showerror("Error", "Please fill both currency fields!")
            return

        URL = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies={to_currency}&base_currency={from_currency}"

        response = requests.get(URL)
        data = response.json()

        if "errors" in data.keys():
            messagebox.showerror("Error", "Please select a valid currency")
            return

        result = round(data["data"][to_currency]["value"], 2) * amount
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

    @staticmethod
    def open_history_window():
        def show_conversations():
            with Session() as session:
                conversions_history = session.query(ConvertionHistory).all()

                return conversions_history
        
        
        def add_to_frame():
            conversions_history = show_conversations()
            
            for conversion in conversions_history:
                row_info = (f"{conversion.date_of_creation.strftime('%Y-%m-%d %H:%M:%S')} - "
                       f"{conversion.amount} {conversion.from_currency} -> "
                       f"{conversion.to_currency} = {conversion.result}")

                label_record = ctk.CTkLabel(
                    history_window,
                    text=row_info,
                    font=("Helvetica", 12),
                    justify="center",
                    wraplength=300,
                    anchor="w"
                )
                label_record.pack(pady=5)


        history_window = ctk.CTkToplevel()
        history_window.title(f"History of transactions")
        history_window.geometry("440x330")

        history_window = ctk.CTkScrollableFrame(history_window,
                                                        width=320,
                                                        orientation="vertical")
        history_window.pack(pady=15)

        add_to_frame()


if __name__ == '__main__':
    app = ConvertEaseApp()
    app.mainloop()
