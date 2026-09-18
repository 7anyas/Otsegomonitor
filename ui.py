import customtkinter as ctk
import psutil
import os
import platform
import time
from collections import deque
from PIL import Image, ImageDraw, ImageEnhance


# colour vars (start a war palette)
BG = "#010101"
SURFACE = "#0a0a0a"
ACCENT = "#1093a1"
TITLE = "#5eabba"
TEXT = "#5eabba"
TEXT_DIM = "#4a5a65"
BORDER = "#1a1a1a"
FONT_TITLE = "Glock Grotesque"
FONT_BODY = "Inter 18pt"

# threshold colours (adjusted for dark bg)
GREEN = "#46ad1c"
AMBER = "#c85c29"
RED = "#ad1c1c"


# picks a colour based on how high a percentage is
def threshold_colour(value: float, warn: float = 70, crit: float = 90) -> str:
    if value >= crit:
        return RED
    elif value >= warn:
        return AMBER
    return GREEN


def make_bg() -> Image.Image:
    w, h = 750, 660
    img = Image.new("RGB", (w, h), "#010101")
    draw = ImageDraw.Draw(img)

    # polka dots (subtle subtle)
    dot_radius = 10
    spacing = 100
    for y in range(0, h + spacing, spacing):
        for x in range(0, w + spacing, spacing):
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill="#0d0d0d"
            )

    # scanlines (thin dark horizontal lines every 4px like a crt monitor)
    for y in range(0, h, 4):
        draw.line([(0, y), (w, y)], fill="#050505", width=1)

    return img


class OtsegoMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Otsegomonitor")
        self.geometry("750x660")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.minsize(650, 500)

        # stores the last 60 cpu readings for the sparkline
        self.cpu_history = deque(maxlen=60)

        self._build_ui()
        self._update()

    def _build_ui(self):
        # background (polka dots + gradient same as my portfolio)
        bg_img = make_bg()
        bg_ctk = ctk.CTkImage(light_image=bg_img, dark_image=bg_img, size=(750, 550))
        bg_label = ctk.CTkLabel(self, image=bg_ctk, text="")
        bg_label.place(x=0, y=0)

        # the title (same as portfolio h1)
        title = ctk.CTkLabel(
            self, text="Otsegomonitor",
            font=ctk.CTkFont(family=FONT_TITLE, size=36, weight="bold"),
            text_color=ACCENT,
            fg_color="#010101"
        )
        title.pack(pady=(20, 5))

        # subtitle (accent same as portfolio header p)
        subtitle = ctk.CTkLabel(
            self, text=f"[ {platform.system()} {platform.release()} | {os.cpu_count()} cores ]",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=ACCENT,
            fg_color="#010101"
        )
        subtitle.pack(pady=(0, 20))

        self.status_header = ctk.CTkLabel(
            self, text="STATUS: NOMINAL",
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            text_color=GREEN,
            fg_color="#010101"
        )
        self.status_header.pack(pady=(0, 15))

        # uptime line
        self.uptime_label = ctk.CTkLabel(
            self, text="UP: --",
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            text_color=TEXT_DIM,
            fg_color="#010101"
        )
        self.uptime_label.pack(pady=(0, 5))

        # the 4 metric cards in a 2x2 grid
        grid = ctk.CTkFrame(self, fg_color="#010101")
        grid.pack(fill="x", padx=30, pady=10)
        grid.grid_columnconfigure((0, 1), weight=1)
        grid.grid_rowconfigure((0, 1), weight=1)

        self.cpu_card = self._make_card(grid, 0, 0, "CPU")
        self.ram_card = self._make_card(grid, 0, 1, "Memory")
        self.disk_card = self._make_card(grid, 1, 0, "Disk")
        self.net_card = self._make_card(grid, 1, 1, "Network")

        # the cpu sparkline
        hist_frame = ctk.CTkFrame(
            self, fg_color=SURFACE,
            border_width=1, border_color=BORDER,
            corner_radius=12
        )
        hist_frame.pack(fill="x", padx=30, pady=(10, 0))

        hist_label = ctk.CTkLabel(
            hist_frame, text="CPU HISTORY (60s)",
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            text_color=TEXT_DIM
        )
        hist_label.pack(anchor="w", padx=12, pady=(8, 4))

        self.hist_label = ctk.CTkLabel(
            hist_frame, text="",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=ACCENT,
            justify="left"
        )
        self.hist_label.pack(anchor="w", padx=12, pady=(0, 8))

        # status line at the bottom
        self.status_label = ctk.CTkLabel(
            self, text="Monitoring...",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=TEXT_DIM,
            fg_color="#010101"
        )
        self.status_label.pack(pady=(15, 10))

        # screenshot button
        from tkinter import filedialog
        ss_btn = ctk.CTkButton(
            self, text="SAVE SCREENSHOT",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
            fg_color=SURFACE, hover_color="#1a1a1a",
            text_color=ACCENT,
            width=140, height=30,
            border_width=1, border_color=BORDER,
            command=self._screenshot
        )
        ss_btn.pack(pady=(5, 10))

        # builds one of the 4 cards (highkey look like the round port cards)
    def _make_card(self, parent, row, col, title):
        card = ctk.CTkFrame(
            parent, fg_color=SURFACE,
            corner_radius=12,
            border_width=1, border_color=BORDER
        )
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        # corner brackets (give it a bit of an edge pun intended)
        for pos, char in [("nw", "┌"), ("ne", "┐"), ("sw", "└"), ("se", "┘")]:
            bracket = ctk.CTkLabel(
                card, text=char,
                font=ctk.CTkFont(family=FONT_BODY, size=14),
                text_color="#043147",
                fg_color="transparent"
            )
            if pos == "nw":
                bracket.place(x=4, y=2)
            elif pos == "ne":
                bracket.place(x=0, y=2, relx=1.0, anchor="ne")
            elif pos == "sw":
                bracket.place(x=4, y=0, rely=1.0, anchor="sw")
            elif pos == "se":
                bracket.place(x=0, y=0, relx=1.0, rely=1.0, anchor="se")

        header = ctk.CTkLabel(
            card, text=f"// {title}",
            font=ctk.CTkFont(family=FONT_BODY, size=12, weight="bold"),
            text_color=ACCENT
        )
        header.pack(anchor="w", padx=15, pady=(12, 4))

        value_label = ctk.CTkLabel(
            card, text="--",
            font=ctk.CTkFont(family=FONT_BODY, size=28, weight="bold"),
            text_color=TITLE
        )
        value_label.pack(anchor="w", padx=15)

        detail_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=TEXT_DIM
        )
        detail_label.pack(anchor="w", padx=15, pady=(0, 12))

        return {"value": value_label, "detail": detail_label, "card": card}

    # the main loop, runs every 1 second via self.after()
    def _update(self):
        # CPU
        cpu_pct = psutil.cpu_percent(interval=None)
        self.cpu_history.append(cpu_pct)

        colour = threshold_colour(cpu_pct)
        self.cpu_card["value"].configure(text=f"{cpu_pct:.0f}%", text_color=colour)
        per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        self.cpu_card["detail"].configure(text=f"avg across {len(per_cpu)} cores")

        # uptime
        uptime_sec = time.time() - psutil.boot_time()
        days = int(uptime_sec // 86400)
        hours = int((uptime_sec % 86400) // 3600)
        mins = int((uptime_sec % 3600) // 60)
        self.uptime_label.configure(text=f"UP: {days}d {hours}h {mins}m")

        # RAM
        ram = psutil.virtual_memory()
        ram_colour = threshold_colour(ram.percent)
        self.ram_card["value"].configure(text=f"{ram.percent:.0f}%", text_color=ram_colour)
        self.ram_card["detail"].configure(
            text=f"{ram.used / 1024**3:.1f} / {ram.total / 1024**3:.1f} GB"
        )

        # disk
        disk = psutil.disk_usage("/")
        disk_colour = threshold_colour(disk.percent)
        self.disk_card["value"].configure(text=f"{disk.percent:.0f}%", text_color=disk_colour)
        self.disk_card["detail"].configure(
            text=f"{disk.used / 1024**3:.1f} / {disk.total / 1024**3:.1f} GB"
        )

        # network
        net = psutil.net_io_counters()
        down = net.bytes_recv / 1024**2
        up = net.bytes_sent / 1024**2
        self.net_card["value"].configure(text=f"{down:.0f} MB", text_color=TEXT)
        self.net_card["detail"].configure(text=f"↓ {down:.1f} MB  ↑ {up:.1f} MB (total)")

        # the sparkline
        if self.cpu_history:
            bars = ""
            for v in self.cpu_history:
                level = int(v / 10)
                if level >= 9:
                    bars += "█"
                elif level >= 7:
                    bars += "▇"
                elif level >= 5:
                    bars += "▆"
                elif level >= 3:
                    bars += "▄"
                elif level >= 1:
                    bars += "▂"
                else:
                    bars += " "
            self.hist_label.configure(text=bars)

        # boring indicator
        worst = max(cpu_pct, ram.percent, disk.percent)
        if worst >= 90:
            self.status_header.configure(text="STATUS: CRITICAL", text_color=RED)
        elif worst >= 70:
            self.status_header.configure(text="STATUS: WARNING", text_color=AMBER)
        else:
            self.status_header.configure(text="STATUS: NOMINAL", text_color=GREEN)

        self.after(1000, self._update)

    def _screenshot(self):
        import subprocess
        from tkinter import filedialog
        self.update_idletasks()
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="otsegomonitor_screenshot.png"
        )
        if not path:
            return
        window_id = self.winfo_id()
        subprocess.run(["import", "-window", str(window_id), path], check=True)
        self.status_label.configure(text=f"saved to {path.split('/')[-1]}")