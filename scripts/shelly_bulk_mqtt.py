import requests
import subprocess
import concurrent.futures
import json
import argparse
from datetime import datetime

# ----------------------
# ? Configurable Settings
# ----------------------
NETWORK = "192.168.1.0/24"
MQTT_SERVER = "192.168.1.3"
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASS = "mqtt_user"
LOG_FILE = "shelly_update_log.txt"


# ----------------------
# ? Scan network for IPs with port 80 open
# ----------------------
def scan_network(network):
    print("? Scanning network...")
    result = subprocess.run(["nmap", "-p", "80", "--open", str(network), "-oG", "-"],
                            stdout=subprocess.PIPE, text=True)
    ips = []
    for line in result.stdout.splitlines():
        if "/open" in line:
            parts = line.split()
            for part in parts:
                if part.count('.') == 3:
                    ips.append(part)
    return ips


# ----------------------
# ? Check model and configure MQTT accordingly
# ----------------------
def configure_device(ip, dry_run=False):
    try:
        r = requests.get(f"http://{ip}/shelly", timeout=2)
        if r.status_code == 200:
            data = r.json()
            model = data.get("type", "")
            if model.startswith("shelly"):
                print(f"? Gen1 Shelly at {ip} ({model})")

                if dry_run:
                    print(f"   [Dry Run] Would set MQTT and reboot {ip}")
                else:
                    payload = {
                        "mqtt_enable": True,
                        "mqtt_server": MQTT_SERVER,
                        "mqtt_user": MQTT_USER,
                        "mqtt_pass": MQTT_PASS,
                        "mqtt_port": MQTT_PORT
                    }
                    requests.post(f"http://{ip}/settings", data=payload, timeout=3)
                    requests.get(f"http://{ip}/reboot", timeout=2)
                    log_success(ip, model)

                return

        # If not Gen1, try Gen2 (Plus/Pro) via /rpc
        r = requests.post(f"http://{ip}/rpc/Sys.GetInfo", timeout=2, json={})
        if r.status_code == 200:
            info = r.json()
            model = info.get("model", "Unknown")
            print(f"? Gen2 Shelly at {ip} ({model})")

            if dry_run:
                print(f"   [Dry Run] Would set MQTT and reboot {ip}")
            else:
                mqtt_config = {
                    "id": 1,
                    "method": "MQTT.SetConfig",
                    "params": {
                        "enable": True,
                        "server": f"{MQTT_SERVER}:{MQTT_PORT}",
                        "user": MQTT_USER,
                        "pass": MQTT_PASS
                    }
                }
                requests.post(f"http://{ip}/rpc", json=mqtt_config, timeout=3)

                # Reboot
                requests.post(f"http://{ip}/rpc", json={"id":1, "method":"Sys.Reboot"}, timeout=2)
                log_success(ip, model)

        else:
            print(f"? {ip} is not a Shelly or unresponsive")
    except Exception as e:
        print(f"? Error with {ip}: {e}")


# ----------------------
# ? Logging
# ----------------------
def log_success(ip, model):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {ip} - {model} - MQTT configured\n")


# ----------------------
# ? Main Entry
# ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan and configure MQTT on Shelly devices")
    parser.add_argument("--dry-run", action="store_true", help="Only detect devices, don't configure anything")
    args = parser.parse_args()

    found_ips = scan_network(NETWORK)
    print(f"Found {len(found_ips)} devices to check.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for ip in found_ips:
            executor.submit(configure_device, ip, args.dry_run)

    print("? All done.")
