#!/usr/bin/env python3
"""
从 forecho/broker-rules 拉取 Surge 格式的合并规则文件，
同时拆分产出两套格式：

Clash（behavior 拆开）：
  rule/domain.yaml  -> behavior: domain
  rule/ip.yaml      -> behavior: ipcidr

Surge（RULE-SET 纯文本，同样按域名/IP 拆开）：
  rule/domain.list
  rule/ip.list

用法：python scripts/split.py
"""
import os
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/forecho/broker-rules/master/rule/Surge/Broker.list"

OUT_CLASH_DOMAIN = "rule/domain.yaml"
OUT_CLASH_IP = "rule/ip.yaml"
OUT_SURGE_DOMAIN = "rule/domain.list"
OUT_SURGE_IP = "rule/ip.list"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(text: str):
    """一次解析，同时产出 Clash 用的列表和 Surge 用的行。"""
    clash_domain, clash_ip = [], []
    surge_domain, surge_ip = [], []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split(",")]
        rule_type = parts[0].upper()

        if rule_type == "DOMAIN-SUFFIX" and len(parts) >= 2:
            clash_domain.append(f"+.{parts[1]}")
            surge_domain.append(f"DOMAIN-SUFFIX,{parts[1]}")
        elif rule_type == "DOMAIN" and len(parts) >= 2:
            clash_domain.append(parts[1])
            surge_domain.append(f"DOMAIN,{parts[1]}")
        elif rule_type == "DOMAIN-KEYWORD" and len(parts) >= 2:
            # Clash domain behavior 没有关键词语义，用通配近似表达
            clash_domain.append(f"*{parts[1]}*")
            surge_domain.append(f"DOMAIN-KEYWORD,{parts[1]}")
        elif rule_type in ("IP-CIDR", "IP-CIDR6") and len(parts) >= 2:
            clash_ip.append(parts[1])
            surge_ip.append(f"{rule_type},{parts[1]},no-resolve")
        # 其余规则类型按需自行扩展分支

    dedup = lambda lst: sorted(set(lst))
    return dedup(clash_domain), dedup(clash_ip), dedup(surge_domain), dedup(surge_ip)


def write_yaml(path: str, entries: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - '{e}'\n")


def write_list(path: str, lines: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    text = fetch(SOURCE_URL)
    clash_domain, clash_ip, surge_domain, surge_ip = parse(text)

    write_yaml(OUT_CLASH_DOMAIN, clash_domain)
    write_yaml(OUT_CLASH_IP, clash_ip)
    write_list(OUT_SURGE_DOMAIN, surge_domain)
    write_list(OUT_SURGE_IP, surge_ip)

    print(f"[Clash] domain: {len(clash_domain)} 条 -> {OUT_CLASH_DOMAIN}")
    print(f"[Clash] ip:     {len(clash_ip)} 条 -> {OUT_CLASH_IP}")
    print(f"[Surge] domain: {len(surge_domain)} 条 -> {OUT_SURGE_DOMAIN}")
    print(f"[Surge] ip:     {len(surge_ip)} 条 -> {OUT_SURGE_IP}")


if __name__ == "__main__":
    main()
