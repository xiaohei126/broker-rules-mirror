#!/usr/bin/env python3
"""
从 forecho/broker-rules 拉取 Surge 格式的合并规则文件，
拆分成两份 Clash rule-provider 能直接用的 yaml：
  rule/domain.yaml  -> behavior: domain
  rule/ip.yaml      -> behavior: ipcidr

用法：python scripts/split.py
"""
import os
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/forecho/broker-rules/master/rule/Surge/Broker.list"

OUT_DOMAIN = "rule/domain.yaml"
OUT_IP = "rule/ip.yaml"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def split(text: str):
    domain_entries, ip_entries = [], []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split(",")]
        rule_type = parts[0].upper()

        if rule_type == "DOMAIN-SUFFIX" and len(parts) >= 2:
            domain_entries.append(f"+.{parts[1]}")
        elif rule_type == "DOMAIN" and len(parts) >= 2:
            domain_entries.append(parts[1])
        elif rule_type == "DOMAIN-KEYWORD" and len(parts) >= 2:
            domain_entries.append(f"*{parts[1]}*")
        elif rule_type in ("IP-CIDR", "IP-CIDR6") and len(parts) >= 2:
            ip_entries.append(parts[1])

    return sorted(set(domain_entries)), sorted(set(ip_entries))


def write_yaml(path: str, entries: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - '{e}'\n")


def main():
    text = fetch(SOURCE_URL)
    domain_entries, ip_entries = split(text)

    write_yaml(OUT_DOMAIN, domain_entries)
    write_yaml(OUT_IP, ip_entries)

    print(f"domain: {len(domain_entries)} 条 -> {OUT_DOMAIN}")
    print(f"ip:     {len(ip_entries)} 条 -> {OUT_IP}")


if __name__ == "__main__":
    main()
