#!/usr/bin/env python3
"""
Shelly migrator -> bloco 192.168.50.X  (rede /16)

Contexto da rede:
  - Rede primaria: gateway 192.168.1.1, mascara 255.255.0.0 (/16)
  - DHCP entrega 192.168.1.2 -> 192.168.49.254
  - Bloco 192.168.50.0 -> 192.168.255.254 esta FORA do DHCP (livre p/ estaticos)

O script:
  1. Faz scan de Shellys na rede atual (default 192.168.1.0/24).
  2. Deteta Gen1 vs Gen2 para usar a API certa (nao parte os Gen1).
  3. Calcula que IPs estao livres no bloco 192.168.50.50-250.
  4. Mapeia cada Shelly a um IP livre e aplica IP estatico /16.
  Sempre com dry-run + confirmacao antes de mexer.

Como /16 mantem tudo no mesmo broadcast domain, os devices continuam
acessiveis a partir da .1 depois de migrarem para .50.X.
"""

import requests
import subprocess
import ipaddress
import time
import sys

# ---------------------------------------------------------------------------
# Configuracao fixa (ajustada a tua rede)
# ---------------------------------------------------------------------------
SCAN_NETWORK   = "192.168.1.0/24"      # onde os Shellys vivem agora
TARGET_BLOCK   = "192.168.50.0/24"     # bloco destino
TARGET_START   = 50                    # 192.168.50.50
TARGET_END     = 250                   # 192.168.50.250
GATEWAY        = "192.168.1.1"
NETMASK        = "255.255.0.0"         # /16
NAMESERVER     = "8.8.8.8"
HTTP_TIMEOUT   = 10


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------
def ensure_nmap():
    try:
        subprocess.run(["nmap", "--version"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("nmap nao esta instalado. Instala com: sudo apt install nmap")
        sys.exit(1)


def scan_for_hosts(network, ports="80"):
    """Devolve IPs com a porta indicada aberta."""
    ensure_nmap()
    print(f"Scanning {network} (porta {ports})...")
    result = subprocess.run(
        ["nmap", "-p", ports, "--open", str(network), "-oG", "-"],
        stdout=subprocess.PIPE, text=True)
    ips = []
    for line in result.stdout.splitlines():
        if "/open" in line:
            for part in line.split():
                if part.count('.') == 3:
                    ips.append(part)
    return ips


def get_device_info(ip):
    """
    Tenta identificar um Shelly e a sua geracao.
    Gen2/Plus/Pro respondem a Shelly.GetDeviceInfo (RPC).
    Gen1 responde ao endpoint HTTP /shelly.
    Devolve: 'gen2', 'gen1' ou None.
    """
    # Gen2+ : RPC
    try:
        r = requests.post(f"http://{ip}/rpc",
                          json={"id": 1, "method": "Shelly.GetDeviceInfo"},
                          timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            j = r.json()
            gen = j.get("result", {}).get("gen")
            if gen and gen >= 2:
                return "gen2"
    except requests.exceptions.RequestException:
        pass

    # Gen1 : /shelly devolve JSON com 'type' mas sem 'gen'
    try:
        r = requests.get(f"http://{ip}/shelly", timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            j = r.json()
            if "type" in j and "gen" not in j:
                return "gen1"
    except requests.exceptions.RequestException:
        pass

    return None


def get_used_ips(network):
    """Ping scan ao bloco destino para saber o que ja esta ocupado."""
    ensure_nmap()
    print(f"A verificar IPs ocupados em {network}...")
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
    used = get_used_ips(TARGET_BLOCK)
    used.add(GATEWAY)
    net = ipaddress.ip_network(TARGET_BLOCK, strict=False)
    pool = []
    for host in net.hosts():
        last = int(str(host).split('.')[-1])
        if TARGET_START <= last <= TARGET_END and str(host) not in used:
            pool.append(str(host))
    print(f"{len(pool)} IPs livres em 192.168.50.{TARGET_START}-{TARGET_END}")
    return pool


# ---------------------------------------------------------------------------
# Aplicar IP estatico
# ---------------------------------------------------------------------------
def set_static_gen2(ip, new_ip, dry_run=True):
    payload = {"id": 1, "method": "WiFi.SetConfig", "params": {"config": {"sta": {
        "ipv4mode": "static", "ip": new_ip, "netmask": NETMASK,
        "gw": GATEWAY, "nameserver": NAMESERVER, "enable": True}}}}
    if dry_run:
        print(f"  [DRY] gen2 {ip} -> {new_ip}: {payload}")
        return True
    r = requests.post(f"http://{ip}/rpc", json=payload, timeout=HTTP_TIMEOUT)
    ok = r.status_code == 200 and not r.json().get("error")
    if ok:
        requests.post(f"http://{ip}/rpc",
                      json={"id": 2, "method": "Shelly.Reboot"},
                      timeout=HTTP_TIMEOUT)
    else:
        print(f"  ERRO gen2 {ip}: {r.text}")
    return ok


def set_static_gen1(ip, new_ip, dry_run=True):
    # Gen1 usa HTTP GET em /settings/sta
    params = {
        "ipv4_method": "static",
        "ip": new_ip,
        "netmask": NETMASK,
        "gw": GATEWAY,
        "dns": NAMESERVER,
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"http://{ip}/settings/sta?{qs}"
    if dry_run:
        print(f"  [DRY] gen1 {ip} -> {new_ip}: GET {url}")
        return True
    r = requests.get(url, timeout=HTTP_TIMEOUT)
    ok = r.status_code == 200
    if ok:
        requests.get(f"http://{ip}/reboot", timeout=HTTP_TIMEOUT)
    else:
        print(f"  ERRO gen1 {ip}: status {r.status_code}")
    return ok


def apply_static(ip, gen, new_ip, dry_run=True):
    if gen == "gen2":
        return set_static_gen2(ip, new_ip, dry_run)
    elif gen == "gen1":
        return set_static_gen1(ip, new_ip, dry_run)
    return False


# ---------------------------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------------------------
def migrate():
    # 1. Descobrir Shellys
    candidates = scan_for_hosts(SCAN_NETWORK, ports="80")
    shellys = []
    for ip in candidates:
        gen = get_device_info(ip)
        if gen:
            shellys.append((ip, gen))
            print(f"  Shelly {gen}: {ip}")
    if not shellys:
        print("Nenhum Shelly encontrado.")
        return
    print(f"\nTotal: {len(shellys)} Shelly(s).")

    # 2. Pool de IPs livres
    pool = build_free_pool()
    if len(pool) < len(shellys):
        print(f"IPs livres insuficientes ({len(pool)}) para {len(shellys)} devices.")
        return

    # 3. Plano
    plan = [(ip, gen, pool[i]) for i, (ip, gen) in enumerate(shellys)]
    print("\n===== PLANO DE MIGRACAO =====")
    for old, gen, new in plan:
        print(f"  {old:<15} ({gen})  ->  {new}")
    print("Apos migrar, cada device fica em 192.168.50.X (continua acessivel via /16).")

    # 4. Confirmacao
    dry = input("\nDry-run? (y/n): ").strip().lower() == "y"
    if not dry and input("Escreve 'MIGRAR' para confirmar: ").strip() != "MIGRAR":
        print("Cancelado.")
        return

    # 5. Aplicar
    for old, gen, new in plan:
        ok = apply_static(old, gen, new, dry_run=dry)
        status = "OK" if ok else "FALHOU"
        print(f"  {old} -> {new}  [{status}]")
        time.sleep(2)

    print("\nFeito. Verifica os devices nos novos IPs (192.168.50.X).")
    if not dry:
        print("Se algum nao aparecer: botao reset fisico (~10s) repoe DHCP.")


def main():
    print("===== Shelly Migrator -> 192.168.50.X (/16) =====")
    print(f"Origem: {SCAN_NETWORK} | Destino: 192.168.50.{TARGET_START}-{TARGET_END}")
    print(f"Gateway: {GATEWAY} | Mascara: {NETMASK}\n")
    input("Enter para comecar o scan (Ctrl+C para sair)...")
    migrate()


if __name__ == "__main__":
    main()