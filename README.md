# RouterOS-AdList

![Build Status](https://github.com/noobsora/RouterOS-AdList/actions/workflows/generate_adlist.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Last Commit](https://img.shields.io/github/last-commit/noobsora/RouterOS-AdList.svg)
![Repo Size](https://img.shields.io/github/repo-size/noobsora/RouterOS-AdList.svg)
![Contributors](https://img.shields.io/github/contributors/noobsora/RouterOS-AdList.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![Format and Lint](https://github.com/noobsora/RouterOS-AdList/actions/workflows/format-and-lint.yml/badge.svg)

---

## 📢 Project Overview

This project is based on several well-known and trusted ad-blocking rule sources. It aggregates and deduplicates these sources to generate a `hosts`-formatted domain blocklist that is compatible with the MikroTik RouterOS DNS Adlist module.The ad domain blocklist is automatically updated every 4 hours, making it ideal for RouterOS users who require system-wide ad blocking without the need for additional plugins.

---

## ⚠️ Notes

The domain sources are selected with a focus on mainland China, and usage outside of this region is not recommended.

---

## ✨ Project Features

* 🔄 **Automatic Updates**: The blocklist is refreshed every 4 hours via GitHub Actions.
* 🧹 **Smart Filtering & Deduplication**: Automatically removes duplicates, invalid entries, regular expressions, wildcards, IP addresses, and non-domain formats.
* ⚙️ **High Compatibility**: Output is fully compatible with the RouterOS DNS Adlist module.
* 🌍 **Trusted Sources**: Aggregates from reputable public rule providers including AdGuard, Cats-Team, Loyalsoldier, and more.
* 🇨🇳 **China-Optimized**: All source lists are carefully selected for effectiveness within mainland China.

---

## ⚙️ Usage Instructions

### Method 1: Configure via Winbox GUI

1. Log in to your RouterOS device using **Winbox**
2. Navigate to `IP` > `DNS` > `Adlist`
3. Click the **“+”** button to add a new entry
4. Paste the following URL into the **URL** field (make sure it's on a single line):
```
https://raw.githubusercontent.com/noobsora/RouterOS-AdList/refs/heads/main/ros-adlist.txt
```
5. **Uncheck** the `SSL Verify` option
6. Click **Apply** to save and activate the rule

### Method 2: Configure via Command Line (RouterOS CLI)

```shell
/ip dns adlist add url="https://raw.githubusercontent.com/noobsora/RouterOS-AdList/refs/heads/main/ros-adlist.txt" ssl-verify=no
```

---

## 🔄 Automatic Update Mechanism

This project uses GitHub Actions to automatically fetch source rules every 4 hours, generate a new `ros-adlist.txt` file, and commit the latest version.

---

## 📚 Current Rule Sources (Partial List)
Cats-Team-AdRules

AdGuard-Dns-Filter

AdGuard-DNS-Popup-Hosts-filter

Perflyst-and-Dandelion-Sprout-s-Smart-TV-Blocklist

v2ray-rules-dat

1Hosts-Lite

OISD-Blocklist-Small

AWAvenue-Ads-Rule

217heidai-AdBlock-Hosts-Lite

Contributions of new source recommendations and Issue submissions are welcome!

---

## ⚠️ Disclaimer

This project is open-source and for educational use only, with no commercial intent.  

All domain sources are public community-maintained lists. This project simply aggregates and formats them.  

Using this list may block access to certain sites; evaluate before applying in production.  

The author is not liable for any damages caused by use of this project.
