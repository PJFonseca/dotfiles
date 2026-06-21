import requests
import subprocess
import json
import ipaddress
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

# ---------------------------------------------------------------------------
# Migration settings (rede /16: tudo no mesmo broadcast domain)
#   Primaria: gateway 192.168.1.1, mascara 255.255.0.0
#   DHCP: 192.168.1.2 -> 192.168.49.254
#   Bloco 192.168.50.50-250 esta FORA do DHCP -> livre p/ estaticos
# ---------------------------------------------------------------------------
MIGRATE_TARGET_BLOCK = "192.168.50.0/24"
MIGRATE_START        = 50            # 192.168.50.50
MIGRATE_END          = 250           # 192.168.50.250
MIGRATE_GATEWAY      = "192.168.1.1"
MIGRATE_NETMASK      = "255.255.0.0"  # /16
MIGRATE_NAMESERVER   = "8.8.8.8"


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

def detect_generation(device_ip):
    """Devolve 'gen2', 'gen1' ou None. Usado pela migracao para escolher a API."""
    # Gen2/Plus/Pro -> RPC
    try:
        r = requests.post(f"http://{device_ip}/rpc",
                          json={"id": 1, "method": "Shelly.GetDeviceInfo"}, timeout=10)
        if r.status_code == 200:
            gen = r.json().get("result", {}).get("gen")
            if gen and gen >= 2:
                return "gen2"
    except requests.exceptions.RequestException:
        pass
    # Gen1 -> /shelly
    try:
        r = requests.get(f"http://{device_ip}/shelly", timeout=10)
        if r.status_code == 200:
            j = r.json()
            if "type" in j and "gen" not in j:
                return "gen1"
    except requests.exceptions.RequestException:
        pass
    return None

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


# ---------------------------------------------------------------------------
# Migracao de IP estatico para o bloco 192.168.50.X
# ---------------------------------------------------------------------------
def get_used_ips(network):
    """Ping scan para saber que IPs ja estao ocupados no bloco destino."""
    ensure_nmap_installed()
    print(f"🔍 A verificar IPs ocupados em {network}...")
    result = subprocess.run(["nmap", "-sn", str(network), "-oG", "-"],
                            stdout=subprocess.PIPE, text=True)
    used = set()
    for line in result.stdout.splitlines():
        if "Up" in line:
            for part in line.split():
                if part.count('.') == 3:
                    used.add(part)
    return used

def build_free_pool():
    used = get_used_ips(MIGRATE_TARGET_BLOCK)
    used.add(MIGRATE_GATEWAY)
    net = ipaddress.ip_network(MIGRATE_TARGET_BLOCK, strict=False)
    pool = []
    for host in net.hosts():
        last = int(str(host).split('.')[-1])
        if MIGRATE_START <= last <= MIGRATE_END and str(host) not in used:
            pool.append(str(host))
    print(f"✅ {len(pool)} IPs livres em 192.168.50.{MIGRATE_START}-{MIGRATE_END}")
    return pool

def set_static_gen2(ip, new_ip, dry_run=True):
    payload = {"id": 1, "method": "WiFi.SetConfig", "params": {"config": {"sta": {
        "ipv4mode": "static", "ip": new_ip, "netmask": MIGRATE_NETMASK,
        "gw": MIGRATE_GATEWAY, "nameserver": MIGRATE_NAMESERVER, "enable": True}}}}
    if dry_run:
        print(f"  [DRY] gen2 {ip} -> {new_ip}")
        return True
    try:
        r = requests.post(f"http://{ip}/rpc", json=payload, timeout=10)
        if r.status_code == 200 and not r.json().get("error"):
            requests.post(f"http://{ip}/rpc",
                          json={"id": 2, "method": "Shelly.Reboot"}, timeout=10)
            return True
        print(f"  ❌ gen2 {ip}: {r.text}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ gen2 {ip}: {e}")
        return False

def set_static_gen1(ip, new_ip, dry_run=True):
    params = {"ipv4_method": "static", "ip": new_ip, "netmask": MIGRATE_NETMASK,
              "gw": MIGRATE_GATEWAY, "dns": MIGRATE_NAMESERVER}
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"http://{ip}/settings/sta?{qs}"
    if dry_run:
        print(f"  [DRY] gen1 {ip} -> {new_ip}: GET {url}")
        return True
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            requests.get(f"http://{ip}/reboot", timeout=10)
            return True
        print(f"  ❌ gen1 {ip}: status {r.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ gen1 {ip}: {e}")
        return False

def migrate_devices(discovered_ips):
    if not discovered_ips:
        print("Sem devices descobertos. Corre a opcao 1 primeiro.")
        return

    # Detetar geracao de cada um
    shellys = []
    print("\nA detetar geracoes...")
    for ip in discovered_ips:
        gen = detect_generation(ip)
        if gen:
            shellys.append((ip, gen))
            print(f"  {gen}: {ip}")
        else:
            print(f"  ⚠️ {ip}: geracao desconhecida, ignorado")
    if not shellys:
        print("Nenhum Shelly identificavel.")
        return

    # Pool de IPs livres
    pool = build_free_pool()
    if len(pool) < len(shellys):
        print(f"❌ IPs livres insuficientes ({len(pool)}) para {len(shellys)} devices.")
        return

    # Plano
    plan = [(ip, gen, pool[i]) for i, (ip, gen) in enumerate(shellys)]
    print("\n===== PLANO DE MIGRACAO =====")
    for old, gen, new in plan:
        print(f"  {old:<15} ({gen})  ->  {new}")
    print("Apos migrar, cada device fica em 192.168.50.X (continua acessivel via /16).")

    dry = input("\nDry-run mode? (y/n): ").strip().lower() == "y"
    if not dry and input("Escreve 'MIGRAR' para confirmar: ").strip() != "MIGRAR":
        print("Cancelado.")
        return

    for old, gen, new in plan:
        if gen == "gen2":
            ok = set_static_gen2(old, new, dry_run=dry)
        else:
            ok = set_static_gen1(old, new, dry_run=dry)
        print(f"  {old} -> {new}  [{'OK' if ok else 'FALHOU'}]")
        time.sleep(2)

    print("\n✅ Feito. Verifica os devices nos novos IPs (192.168.50.X).")
    if not dry:
        print("Se algum nao aparecer: reset fisico (~10s) repoe DHCP.")


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
        print("8. Migrate devices to 192.168.50.X (static IP)")
        print("9. Exit")
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
            migrate_devices(discovered_ips)
        elif choice == "9":
            print("Exiting.")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()