import customtkinter as ctk
from tkinter import messagebox

from sqlalchemy.orm import sessionmaker
from models import engine, ConvertionHistory

import requests


Session = sessionmaker(bind=engine)
API_KEY = "cur_live_GUJDzvVikvIXbtcgPJcvbjIDdULbWFfYvgmHM6Dh"


class ConvertEaseApp(ctk.CTk):  # Inherits from the CTk class
    def __init__(self):
        super().__init__()

        self.title("ConvertEase")
        self.geometry("450x500")  # Adjusted size for better spacing

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
        self.result_label = ctk.CTkLabel(self, text="", font=("Helvetica", 14), text_color="green")
        self.result_label.pack(pady=15)

    def convert_currency(self):
        amount = int(self.entry_for_amount.get())
        from_currency = self.entry_for_currency_to_convert.get().upper()
        to_currency = self.entry_for_currency_wanted.get().upper()

        URL = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies={to_currency}&base_currency={from_currency}"

        response = requests.get(URL)
        data = response.json()

        if "errors" in data.keys():
            messagebox.showerror("Error", data["errors"]["currencies"][0])
            return

        result = round(data["data"][to_currency]["value"], 2) * amount
        self.result_label.configure(text=f"Converted {amount} {from_currency} to {to_currency} = {result}")


if __name__ == '__main__':
    app = ConvertEaseApp()
    app.mainloop()
