from sqlalchemy.orm import sessionmaker
from models import engine, ConvertionHistory

import customtkinter as ctk


Session = sessionmaker(bind=engine)


class ConvertEaseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Convert Ease")
        self.geometry("400x200")




if __name__ == '__main__':
    app = ConvertEaseApp()
    app.mainloop()
