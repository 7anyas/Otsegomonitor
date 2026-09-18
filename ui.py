import customtkinter as ctk
import psutil
import os
import platform

# colour vars (dark industrial theme)
BG = "#0d0d0d"
SURFACE = "#1a1a1a"
ACCENT = "#ff2200"
TEXT = "#e0e0e0"
TEXT_DIM = "#777777"
BORDER = "#333333"
MONO = "Courier"


class OtsegoMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OTSEGO")
        self.geometry("750x550")
        self.configure(fg_color=BG)
        self.minsize(650, 500)

        self._build_ui()
        self._update()  # start the refresh loop

    def _build_ui(self):
        # the title at the top
        title = ctk.CTkLabel(
            self, text="OTSEGO",
            font=ctk.CTkFont(family=MONO, size=26, weight="bold"),
            text_color=ACCENT
        )
        title.pack(pady=(20, 5))

        # subtitle showing os + core count
        subtitle = ctk.CTkLabel(
            self, text=f"[ {platform.system()} {platform.release()} | {os.cpu_count()} cores ]",
            font=ctk.CTkFont(family=MONO, size=11),
            text_color=TEXT_DIM
        )
        subtitle.pack(pady=(0, 20))

        # the 4 metric cards in a 2x2 grid
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=10)
        grid.grid_columnconfigure((0, 1), weight=1)
        grid.grid_rowconfigure((0, 1), weight=1)

        # each card is a dict so i can grab the labels later to update them
        self.cpu_card = self._make_card(grid, 0, 0, "CPU")
        self.ram_card = self._make_card(grid, 0, 1, "MEMORY")
        self.disk_card = self._make_card(grid, 1, 0, "DISK")
        self.net_card = self._make_card(grid, 1, 1, "NETWORK")

        # status line at the bottom
        self.status_label = ctk.CTkLabel(
            self, text="Monitoring...",
            font=ctk.CTkFont(family=MONO, size=11),
            text_color=TEXT_DIM
        )
        self.status_label.pack(pady=(15, 10))

    # builds one of the 4 cards (title + big number + detail line)
    def _make_card(self, parent, row, col, title):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        # the card header (e.g. "■ CPU")
        header = ctk.CTkLabel(
            card, text=f"■ {title}",
            font=ctk.CTkFont(family=MONO, size=12, weight="bold"),
            text_color=TEXT_DIM
        )
        header.pack(anchor="w", padx=15, pady=(12, 4))

        # the big percentage number (e.g. "42%")
        value_label = ctk.CTkLabel(
            card, text="--",
            font=ctk.CTkFont(family=MONO, size=28, weight="bold"),
            text_color=TEXT
        )
        value_label.pack(anchor="w", padx=15)

        # the smaller detail line under the number (e.g. "8.2 / 16.0 GB")
        detail_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(family=MONO, size=11),
            text_color=TEXT_DIM
        )
        detail_label.pack(anchor="w", padx=15, pady=(0, 12))

        # return refs so _update() can change the text later
        return {"value": value_label, "detail": detail_label, "card": card}

    # the main loop, runs every 1 second via self.after()
    def _update(self):
        # CPU
        cpu_pct = psutil.cpu_percent(interval=None)
        self.cpu_card["value"].configure(text=f"{cpu_pct:.0f}%")
        per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        self.cpu_card["detail"].configure(text=f"avg across {len(per_cpu)} cores")

        # RAM
        ram = psutil.virtual_memory()
        self.ram_card["value"].configure(text=f"{ram.percent:.0f}%")
        self.ram_card["detail"].configure(
            text=f"{ram.used / 1024**3:.1f} / {ram.total / 1024**3:.1f} GB"
        )

        # disk (root partition)
        disk = psutil.disk_usage("/")
        self.disk_card["value"].configure(text=f"{disk.percent:.0f}%")
        self.disk_card["detail"].configure(
            text=f"{disk.used / 1024**3:.1f} / {disk.total / 1024**3:.1f} GB"
        )

        # network (total bytes since boot)
        net = psutil.net_io_counters()
        down = net.bytes_recv / 1024**2
        up = net.bytes_sent / 1024**2
        self.net_card["value"].configure(text=f"{down:.0f} MB")
        self.net_card["detail"].configure(text=f"↓ {down:.1f} MB  ↑ {up:.1f} MB (total)")

        # schedule the next update in 1000ms
        self.after(1000, self._update)