# Broker Rules Mirror

这是一个自动同步和优化券商/金融服务分流规则的项目。

本项目基于 [forecho/broker-rules](https://github.com/forecho/broker-rules) 进行二次开发与镜像优化。其核心改进在于**将域名（Domain）和 IP 地址（IP-CIDR）规则进行了解耦与分离**，旨在提高规则加载效率，方便不同代理客户端（如 Clash、Surge等）进行更灵活的精细化按需配置。

## 🌟 核心特性

- **域名与 IP 分离**：拒绝臃肿，将 `DOMAIN` 相关规则与 `IP-CIDR` 规则独立成不同的文件。
- **提升解析性能**：客户端无需在大文件中频繁混合匹配域名与 IP，减少代理软件的内存占用与解析耗时。
- **自动同步更新**：上游规则变动后自动跟进，确保金融/券商节点走最快的分流路线。

## Surge

```
RULE-SET,https://raw.githubusercontent.com/xiaohei126/broker-rules-mirror/main/rule/ip.list,节点
RULE-SET,https://raw.githubusercontent.com/xiaohei126/broker-rules-mirror/main/rule/domain.list,节点
```

## Clash

```
  broker_domain:
    type: http
    behavior: classical
    format: text
    interval: 43200
    url: https://raw.githubusercontent.com/xiaohei126/broker-rules-mirror/main/rule/domain.list
    path: ./broker_ruleset/broker_domain.list

  broker_ip:
    type: http
    behavior: classical
    format: text
    interval: 43200
    url: https://raw.githubusercontent.com/xiaohei126/broker-rules-mirror/main/rule/ip.list
    path: ./broker_ruleset/broker_ip.list
    
    - RULE-SET,broker_domain,节点
    - RULE-SET,broker_ip,节点
```

