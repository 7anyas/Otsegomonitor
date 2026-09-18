# Otsegomonitor

a real-time system monitor with a dark industrial UI.
shows cpu, memory, disk, and network usage with threshold-based colour coding.


## Features

- real-time CPU usage (overall + per-core count)
- memory usage with total/used breakdown
- disk usage for root partition
- network I/O totals
- 60-second CPU history sparkline
- colour thresholds: green < 70%, amber 70-89%, red >= 90%
- uptime counter
- built-in screenshot button

## Requirements

- Python 3.10+
- Linux (tested on Linux Mint 21)

## Setup

```bash
# system dependencies
sudo apt install python3-tk imagemagick

# custom fonts
mkdir -p ~/.local/share/fonts
cp assets/fonts/*.otf assets/fonts/*.ttf ~/.local/share/fonts/
fc-cache -fv

# project
git clone https://github.com/7anyas/Otsegomonitor
cd Otsegomonitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
enjoy :)