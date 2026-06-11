#!/bin/bash

# Try to enable IP forwarding (may fail in container, host-level forwarding used instead)
echo 1 > /proc/sys/net/ipv4/ip_forward 2>/dev/null || true

# Detect interfaces dynamically
LAB01_IF=$(ip route | grep '10.10.1.' | awk '{print $3}' | head -1)
LAB02_IF=$(ip route | grep '10.10.2.' | awk '{print $3}' | head -1)

if [ -n "$LAB01_IF" ] && [ -n "$LAB02_IF" ]; then
    iptables -t nat -A POSTROUTING -o $LAB02_IF -j MASQUERADE 2>/dev/null || true
    iptables -A FORWARD -i $LAB01_IF -o $LAB02_IF -j ACCEPT 2>/dev/null || true
    iptables -A FORWARD -i $LAB02_IF -o $LAB01_IF -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true
    echo "[+] Gateway routing configured: $LAB01_IF <-> $LAB02_IF"
else
    echo "[!] Could not detect interfaces, enabling basic forwarding"
    iptables -t nat -A POSTROUTING -j MASQUERADE 2>/dev/null || true
    iptables -A FORWARD -j ACCEPT 2>/dev/null || true
fi

exec /usr/sbin/sshd -D
