import requests
import argparse
import subprocess
import json
import time

# MQTT Configuration details
mqtt_config = {
    "enable": True,  # Enable MQTT
    "server": "192.168.1.4:1883",  # Your MQTT broker IP and port
    "user": "homeassistant",  # MQTT username
    "pass": "mqtt_user",  # MQTT password
    "topic": "shelly/device",  # MQTT topic format
}

# Function to check if a device is a Shelly device by checking MQTT configuration
def is_shelly_device(device_ip, retries=3):
    try:
        url = f"http://{device_ip}/rpc"
        data = {
            "id": 1,
            "method": "Mqtt.GetConfig"
        }
        for attempt in range(retries):
            try:
                response = requests.post(url, json=data, timeout=10)  # Increased timeout
                if response.status_code == 200 and response.json().get("result"):
                    print(f"Device at {device_ip} is a Shelly device.")
                    return True
                else:
                    print(f"Device at {device_ip} is not a Shelly device.")
                    return False
            except requests.exceptions.RequestException:
                print(f"Attempt {attempt+1} failed to connect to {device_ip}, retrying...")
                time.sleep(2)  # Wait 2 seconds before retrying
        print(f"Failed to connect to {device_ip} after {retries} attempts.")
        return False

    except requests.exceptions.RequestException:
        print(f"Error while connecting to {device_ip}")
        return False

# Function to update MQTT configuration on a Shelly device
def update_mqtt(device_ip, dry_run):
    try:
        # Construct the URL to access the Shelly device's MQTT configuration
        url = f"http://{device_ip}/rpc"
        data = {
            "id": 1,
            "method": "Mqtt.SetConfig",
            "params": {
                "config": {
                    "enable": mqtt_config["enable"],
                    "server": mqtt_config["server"],
                    "user": mqtt_config["user"],
                    "pass": mqtt_config["pass"],
                    "topic": mqtt_config["topic"]
                }
            }
        }

        if dry_run:
            print(f"Dry run: Would update MQTT settings for {device_ip}")
            # Actually apply the change in dry-run mode, but only for this IP
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"Dry-run: Successfully updated MQTT settings for {device_ip}")
                # Reboot the device after updating the config
                reboot_device(device_ip)  # Perform reboot in dry-run mode
            else:
                print(f"Failed to update MQTT settings for {device_ip}. Status code: {response.status_code}")
            return  # Return to avoid updating other devices in dry-run mode

        # In normal mode, update and reboot as usual
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            print(f"Successfully updated MQTT settings for {device_ip}")

            # Reboot the device after updating the config
            reboot_device(device_ip)
        else:
            print(f"Failed to update MQTT settings for {device_ip}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error while connecting to {device_ip}: {e}")

# Function to reboot a Shelly device
def reboot_device(device_ip):
    try:
        # Construct the URL for the Reboot API
        url = f"http://{device_ip}/rpc"
        data = {
            "id": 1,
            "method": "Shelly.Reboot"
        }

        # Reboot the device
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            print(f"Device {device_ip} successfully rebooted.")
        else:
            print(f"Failed to reboot device {device_ip}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error while connecting to {device_ip}: {e}")

# ----------------------
# ? Scan network for IPs with port 80 open
# ----------------------
def scan_network(network):
    ensure_nmap_installed()

    print(f"? Scanning network {network}...")
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

# Function to ensure nmap is installed
def ensure_nmap_installed():
    try:
        subprocess.run(["nmap", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("nmap is not installed. Please install nmap to use this script.")
        exit(1)

# Parse arguments
parser = argparse.ArgumentParser(description="Bulk update Shelly devices' MQTT settings")
parser.add_argument('--dry-run', action='store_true', help="Actually update the MQTT settings for the specified IP, but only for that IP.")
parser.add_argument('--ip', type=str, help="Specify an individual IP to update (if not supplied, all IPs will be updated).")
parser.add_argument('--network', type=str, help="Specify the network range (e.g., 192.168.1.0/24).", default="192.168.1.0/24")

args = parser.parse_args()

# If --ip flag is provided, only update that device
if args.ip:
    if is_shelly_device(args.ip):  # Only proceed if it's a Shelly device
        print(f"Checking current config for {args.ip}...")
        update_mqtt(args.ip, args.dry_run)
    else:
        print(f"Skipping {args.ip}, not a Shelly device.")
else:
    # Scan the network for open ports (80)
    ips = scan_network(args.network)
    for device_ip in ips:
        if is_shelly_device(device_ip):  # Only proceed if it's a Shelly device
            print(f"Checking current config for {device_ip}...")
            update_mqtt(device_ip, args.dry_run)
