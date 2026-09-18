import customtkinter as ctk
from ui import OtsegoMonitor

def main():
    ctk.set_appearance_mode("dark")
    app = OtsegoMonitor()
    app.mainloop()

if __name__ == "__main__":
    main()