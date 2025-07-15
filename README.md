# RouterOS-AdList

![Build Status](https://github.com/noobsora/RouterOS-AdList/actions/workflows/generate_adlist.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Last Commit](https://img.shields.io/github/last-commit/noobsora/RouterOS-AdList.svg)
![Repo Size](https://img.shields.io/github/repo-size/noobsora/RouterOS-AdList.svg)
![Contributors](https://img.shields.io/github/contributors/noobsora/RouterOS-AdList.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![Format and Lint](https://github.com/noobsora/RouterOS-AdList/actions/workflows/format-and-lint.yml/badge.svg)

---

## 📢 项目简介

本项目基于多个主流广告过滤规则源，聚合并去重，生成符合 MikroTik RouterOS DNS Adlist 模块要求的 `hosts` 格式广告屏蔽列表。  
支持自动每4小时更新，适合需要系统级广告屏蔽的 RouterOS 用户，无需安装额外插件。

---

## ✨ 项目特点

- 🔄 **自动更新**：每4小时自动拉取最新规则并生成列表  
- 🧹 **智能去重与过滤**：剔除重复、无效规则，过滤正则、通配符、IP等非域名格式  
- ⚙️ **兼容性强**：输出格式100%支持 RouterOS DNS Adlist  
- 🌍 **多规则源支持**：包含 AdGuard、Cats-Team、Loyalsoldier 等多个高质量开源广告规则  

---

## ⚙️ 使用方法

### 方法一：Winbox 图形界面配置

1. 使用 Winbox 登录 RouterOS  
2. 依次点击 `IP` > `DNS` > `Adlist`  
3. 点击 `+` 新增规则  
4. 在 **URL** 栏粘贴以下地址（确保在同一行）：
```
https://raw.githubusercontent.com/noobsora/RouterOS-AdList/refs/heads/main/ros-adlist.txt
```
5. **取消勾选** `SSL Verify`  
6. 点击 `Apply` 保存生效  

### 方法二：命令行配置（RouterOS CLI）

```shell
/ip dns adlist add url="https://raw.githubusercontent.com/noobsora/RouterOS-AdList/refs/heads/main/ros-adlist.txt" ssl-verify=no
```

---

## 🔄 自动更新机制
本项目通过 GitHub Actions 自动拉取源规则，每 4 小时执行一次，自动生成并提交最新的 ros-adlist.txt 文件。

---

## 📚 当前规则源（部分）
Cats-Team: https://github.com/Cats-Team/AdRules

AdGuardDnsFilter

AdGuard-DNS-Popup-Hosts-filter

Perflyst-and-Dandelion-Sprout-s-Smart-TV-Blocklist

v2ray-rules-dat

1Hosts-Lite

OISD-Blocklist-Small

AWAvenue-Ads-Rule

欢迎提出新的源推荐和提交 Issue ！

---

## ⚠️ 免责声明 | Disclaimer
本项目为开源学习用途，不涉及任何商业盈利行为。  
This project is open-source and for educational use only, with no commercial intent.  

所有域名来源均来自公开社区项目或第三方规则集，作者仅作汇总清洗处理。  
All domain sources are public community-maintained lists. This project simply aggregates and formats them.  

使用本规则可能会对部分网站的访问造成影响，请用户自行评估与测试。  
Using this list may block access to certain sites; evaluate before applying in production.  

作者不对使用本项目可能造成的任何直接或间接损失承担责任。  
The author is not liable for any damages caused by use of this project.
