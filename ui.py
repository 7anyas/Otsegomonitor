import customtkinter as ctk

# colour vars (dark industrial theme)
BG = "#0d0d0d"
ACCENT = "#ff2200"
TEXT_DIM = "#777777"
MONO = "Courier"


class OtsegoMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OTSEGO")
        self.geometry("750x550")
        self.configure(fg_color=BG)
        self.minsize(650, 500)

        # just the title for now cus i'm gonna add everything else up later onn (big wip)
        title = ctk.CTkLabel(
            self, text="OTSEGO",
            font=ctk.CTkFont(family=MONO, size=26, weight="bold"),
            text_color=ACCENT
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self, text="[ placeholder ]",
            font=ctk.CTkFont(family=MONO, size=11),
            text_color=TEXT_DIM
        )
        subtitle.pack(pady=(0, 20))