#!/usr/bin/env python3
import urllib.request
import time
import os
import os.path
import argparse
from flask import Flask

ROUTERS = ["ocelot", "lion"]
ROUTER_IPS = {
    "ocelot": "192.168.1.1",
    "lion": "192.168.1.2",
}

app = Flask(__name__)

# Colors
RED="\u001b[91m"
GREEN="\u001b[92m"
YELLOW="\u001b[93m"
RESET="\u001b[0m"
BLUE="\u001b[94m"

names = {}

# Load well known names
with open("/mnt/names") as names_file:
    for name in names_file:
        parts = name.split("-")
        names[parts[0]] = {
            "name": parts[1].strip(),
        }

def load(show_leases=False):
    leases = {}
    clients = []
    uptimes = []
    for router in ROUTERS:
        # Load into from the routers
        try:
            request = urllib.request.Request("http://{}/cgi-bin/who".format(ROUTER_IPS[router]))
            response = urllib.request.urlopen(request)
            infos = response.read().decode().split("\n")

            for info in infos:
                info = info.split()
                if len(info) == 0:
                    continue

                # Organize declatations
                if info[0] == "lease":
                    leases[info[1]] = {
                        "ip": info[2],
                        "hostname": info[3],
                    }
                elif info[0] == "uptime":
                    uptimes.append({
                        "name": router,
                        "uptime": " ".join(info[1:]),
                    })
                elif info[0] == "device":
                    clients.append({
                        "mac": info[1],
                        "signal": info[2],
                        "ssid": info[3],
                        "router": router,
                    })
        except Exception:
            pass

    for client in clients:
        # Add dhcp leases to client info
        if client["mac"] in leases:
            client.update(leases[client["mac"]])
            del leases[client["mac"]]
    
    if show_leases:
        for mac, lease in leases.items():
            lease.update({ "mac": mac })
            clients.append(lease)

    for client in clients:
        if "hostname" in client and client["hostname"] == "*":
            del client["hostname"]

        # Look up their better name
        if client["mac"] in names:
            client.update(names[client["mac"]])

    return {
        "clients": clients,
        "uptimes": uptimes,
        "online": os.system("ping -W 1 -c 1 8.8.8.8") == 0,
    }

@app.route("/")
def main():
    return load(show_leases=True)

@app.route("/reboot")
def reboot():
    if os.path.exists("/home/ryan/no-reboot"):
        return "Reboot denied: The routers are being worked on"
    for router in ROUTERS:
        os.system("ssh -o StrictHostKeyChecking=no root@{} reboot".format(ROUTER_IPS[router]))
    return "Reboot started"

app.run()
