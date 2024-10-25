#!/bin/bash

# Variables
HOSTS_URL="https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
HOSTS_FILE="/tmp/hosts"
RANDOM_DOMAINS_FILE="/tmp/random_domains.txt"
PIHOLE_IP="192.168.0.1"  # Replace with your Pi-hole IP address

# Download the hosts file
echo "Downloading the hosts file..."
curl -o "$HOSTS_FILE" "$HOSTS_URL"

# Extract 1000 random domains
echo "Selecting 1000 random domains..."
awk '/^[0-9]/ {print $2}' "$HOSTS_FILE" | shuf -n 1000 > "$RANDOM_DOMAINS_FILE"

# Test domains with dig and extract the line below ;; ANSWER SECTION:
echo "Testing domains with dig and extracting the line below ;; ANSWER SECTION:"
while IFS= read -r domain; do
    echo "Testing $domain"
    dig @"$PIHOLE_IP" "$domain" | awk '/^;; ANSWER SECTION:/ {flag=1; next} flag && /^;;/ {flag=0} flag'
done < "$RANDOM_DOMAINS_FILE"

