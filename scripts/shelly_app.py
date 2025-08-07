import requests
import subprocess
import json
import time
import sys

# MQTT Configuration details
mqtt_config = {
    "enable": True,
    "server": "192.168.1.4:1883",
    "user": "homeassistant",
    "pass": "mqtt_user",
    "topic": "shelly/device",
}

def ensure_nmap_installed():
    try:
        subprocess.run(["nmap", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("nmap is not installed. Please install nmap to use this script.")
        sys.exit(1)

def scan_network(network):
    ensure_nmap_installed()
    print(f"🔍 Scanning network {network}...")
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

def is_shelly_device(device_ip, retries=3):
    try:
        url = f"http://{device_ip}/rpc"
        data = { "id": 1, "method": "Mqtt.GetConfig" }
        for attempt in range(retries):
            try:
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200 and response.json().get("result"):
                    return True
            except requests.exceptions.RequestException:
                time.sleep(2)
        return False
    except:
        return False

def update_mqtt(device_ip, dry_run=True):
    try:
        url = f"http://{device_ip}/rpc"
        requests_to_send = [
            {
                "desc": "MQTT settings",
                "data": {
                    "id": 1,
                    "method": "Mqtt.SetConfig",
                    "params": { "config": mqtt_config }
                }
            },
            {
                "desc": "Disable WiFi AP",
                "data": {
                    "id": 2,
                    "method": "WiFi.SetConfig",
                    "params": { "config": { "ap": { "enable": False } } }
                }
            },
            {
                "desc": "Enable Bluetooth",
                "data": {
                    "id": 3,
                    "method": "Ble.SetConfig",
                    "params": { "config": { "enable": True } }
                }
            }
        ]

        for req in requests_to_send:
            print(f"{'[DRY RUN]' if dry_run else ''} Updating {req['desc']} on {device_ip}...")
            if not dry_run:
                response = requests.post(url, json=req["data"], timeout=10)
                if response.status_code == 200:
                    print(f"✅ Updated {req['desc']} on {device_ip}")
                else:
                    print(f"❌ Failed to update {req['desc']}. Status: {response.status_code}")
            else:
                print(f"Would send: {req['data']}")
                # Optionally validate dry-run works
                response = requests.post(url, json=req["data"], timeout=10)
                if response.status_code == 200:
                    print(f"✅ DRY-RUN worked for {req['desc']}")
                else:
                    print(f"❌ DRY-RUN failed for {req['desc']}. Status: {response.status_code}")

        if not dry_run:
            reboot_device(device_ip)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to {device_ip}: {e}")

def reboot_device(device_ip):
    try:
        url = f"http://{device_ip}/rpc"
        data = { "id": 1, "method": "Shelly.Reboot" }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"🔄 Rebooted {device_ip} successfully.")
        else:
            print(f"❌ Failed to reboot {device_ip}. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Reboot error: {e}")

def set_beta_updates(device_ip, enable_beta=True):
    try:
        url = f"http://{device_ip}/rpc"
        data = {
            "id": 1,
            "method": "Shelly.SetConfig",
            "params": {
                "config": {
                    "fw": {
                        "beta": enable_beta
                    }
                }
            }
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Beta updates {'enabled' if enable_beta else 'disabled'} for {device_ip}.")
        else:
            print(f"❌ Failed to update beta setting for {device_ip}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating beta flag on {device_ip}: {e}")

def force_firmware_update(device_ip):
    print(f"\n🔧 Ensuring {device_ip} is ready for beta update...")

    # Step 1: Set beta = true
    try:
        response = requests.post(
            f"http://{device_ip}/rpc",
            json={
                "id": 1,
                "method": "Shelly.SetConfig",
                "params": {
                    "config": {
                        "fw": {
                            "beta": True
                        }
                    }
                }
            },
            timeout=1
        )
        if response.status_code == 200:
            print(f"✅ Beta config enabled on {device_ip}")
        else:
            print(f"❌ Failed to set beta config on {device_ip}")
            return
    except Exception as e:
        print(f"❌ Error setting beta config: {e}")
        return

    # Step 2: Reboot
    try:
        response = requests.post(
            f"http://{device_ip}/rpc",
            json={"id": 2, "method": "Shelly.Reboot"},
            timeout=1
        )
        if response.status_code == 200:
            print(f"🔄 Rebooting {device_ip}...")
            time.sleep(1)
        else:
            print(f"⚠️ Reboot failed, but continuing.")
    except Exception as e:
        print(f"⚠️ Reboot error: {e}")

    # Step 3: Call Shelly.Update with beta=True
    try:
        print(f"🚀 Triggering beta firmware update on {device_ip}...")
        response = requests.post(
            f"http://{device_ip}/rpc",
            json={"id": 3, "method": "Shelly.Update", "params": {"beta": True}},
            timeout=1
        )
        if response.status_code == 200:
            print(f"✅ Update triggered on {device_ip} (response: {response.json()})")
        else:
            print(f"❌ Failed to trigger update. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error triggering update: {e}")


# Menu loop
def main():
    network_range = input("Enter network range (default: 192.168.1.0/24): ").strip() or "192.168.1.0/24"
    discovered_ips = []

    while True:
        print("\n======= Shelly Device Manager =======")
        print("1. Scan network for Shelly devices")
        print("2. Show discovered devices")
        print("3. Update MQTT config (all)")
        print("4. Update MQTT config (single IP)")
        print("5. Reboot a device")
        print("6. Toggle beta firmware updates for a device")
        print("7. Force firmware update on all devices")
        print("8. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            discovered_ips = [ip for ip in scan_network(network_range) if is_shelly_device(ip)]
            print(f"\n✅ Found {len(discovered_ips)} Shelly device(s):")
            for ip in discovered_ips:
                print(f" - {ip}")
        elif choice == "2":
            if not discovered_ips:
                print("No devices discovered yet. Run option 1 first.")
            else:
                print("\nDiscovered devices:")
                for ip in discovered_ips:
                    print(f" - {ip}")
        elif choice == "3":
            if not discovered_ips:
                print("No devices to update. Please scan first.")
            else:
                dry = input("Dry-run mode? (y/n): ").strip().lower() == "y"
                for ip in discovered_ips:
                    update_mqtt(ip, dry_run=dry)
        elif choice == "4":
            ip = input("Enter device IP: ").strip()
            if is_shelly_device(ip):
                dry = input("Dry-run mode? (y/n): ").strip().lower() == "y"
                update_mqtt(ip, dry_run=dry)
            else:
                print("❌ Not a valid Shelly device.")
        elif choice == "5":
            ip = input("Enter device IP to reboot: ").strip()
            reboot_device(ip)
        elif choice == "6":
            if not discovered_ips:
                print("No devices discovered. Run option 1 first.")
                continue
            beta = input("Enable beta firmware updates? (y/n): ").strip().lower() == "y"
            for ip in discovered_ips:
                set_beta_updates(ip, enable_beta=beta)
        elif choice == "7":
            if not discovered_ips:
                print("No devices discovered. Run option 1 first.")
                continue
            use_beta = input("Force beta firmware update? (y/n): ").strip().lower() == "y"
            for ip in discovered_ips:
                force_firmware_update(ip)
        elif choice == "8":
            print("Exiting.")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
