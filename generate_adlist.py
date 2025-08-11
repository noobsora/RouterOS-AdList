import requests
import re
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()

# 域名来源
SOURCES = {
    "Cats-Team": (
        "https://raw.githubusercontent.com/Cats-Team/AdRules/main/mosdns_adrules.txt"
    ),
    "AdGuardDnsFilter": (
        "https://raw.githubusercontent.com/AdguardTeam/"
        "HostlistsRegistry/refs/heads/main/filters/general/"
        "filter_1_DnsFilter/filter.txt"
    ),
    "AdGuard-DNS-Popup-Hosts-filter": (
        "https://raw.githubusercontent.com/AdguardTeam/"
        "HostlistsRegistry/refs/heads/main/filters/general/"
        "filter_59_DnsPopupsFilter/filter.txt"
    ),
    "AWAvenue-Ads-Rule": (
        "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/"
        "main/Filters/AWAvenue-Ads-Rule-RouterOS-Adlist.txt"
    ),
    "217heidai-AdblockHostsLite": (
        "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/"
        "adblockhostslite.txt"
    ),
    #    "Perflyst-and-Dandelion-Sprout-s-Smart-TV-Blocklist": (
    #        "https://raw.githubusercontent.com/AdguardTeam/"
    #        "HostlistsRegistry/refs/heads/main/filters/other/"
    #        "filter_7_SmartTVBlocklist/filter.txt"
    #    ),
    #    "v2ray-rules-dat": (
    #        "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/"
    #        "release/reject-list.txt"
    #    ),
    #    "1Hosts-Lite": ("https://badmojr.github.io/1Hosts/Lite/domains.txt"),
    #    "OISD-Blocklist-Small": ("https://small.oisd.nl/domainswild2"),
}

# 跳过规则（路径、通配符、正则）
SKIP_PATTERNS = [
    re.compile(r"^/.+/$"),   # 纯正则 /pattern/
    re.compile(r"[\[\]{}]"), # 正则符号
    re.compile(r"\*"),       # 通配符
    re.compile(r"/"),        # URL 路径（包含斜杠的直接跳过）
]

# 域名匹配（排除 IPv4）
DOMAIN_PATTERN = re.compile(
    r"\b(?!(?:\d+\.){3}\d+)([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})\b"
)


def extract_domains(text):
    """提取并过滤域名"""
    domains = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("@@"):
            continue

        # 去掉 Adblock 常见修饰符
        line = line.strip("^|")

        # 跳过匹配到的无效模式
        if any(p.search(line) for p in SKIP_PATTERNS):
            continue

        matches = DOMAIN_PATTERN.findall(line)
        for domain in matches:
            if (
                not any(p.search(domain) for p in SKIP_PATTERNS)
                and not domain.startswith("-")
                and not domain.startswith(".")
            ):
                domains.add(domain.lower())
    return domains


def get_hkt_time():
    """获取香港时间"""
    utc_time = datetime.utcnow()
    hkt_time = utc_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(
        ZoneInfo("Asia/Hong_Kong")
    )
    return hkt_time.strftime("%Y-%m-%d %H:%M GMT+8")


def create_session():
    """创建带重试的会话"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def main():
    all_domains = set()
    source_stats = {}
    session = create_session()

    for name, url in SOURCES.items():
        try:
            logger.info(f"⬇ 正在获取：{name}")
            res = session.get(url, timeout=30)
            res.raise_for_status()
            domains = extract_domains(res.text)
            source_stats[name] = len(domains)
            all_domains.update(domains)
        except requests.exceptions.RequestException as e:
            logger.error("❌ 获取失败 %s：%s", name, e)
            source_stats[name] = 0

    sorted_domains = sorted(all_domains, key=str.lower)

    with open("ros-adlist.txt", "w", encoding="utf-8") as f:
        f.write("# 更新时间：" + get_hkt_time() + "\n")
        f.write("# 数据来源：\n")
        for name, count in source_stats.items():
            f.write(f"# - {name}：{count} 条\n")
        f.write(f"# 合并去重后总数：{len(sorted_domains):,} 条\n\n")
        for domain in sorted_domains:
            f.write("0.0.0.0 " + domain + "\n")

    logger.info(
        "\n✅ 已生成 ros-adlist.txt，共 {:,} 个域名".format(len(sorted_domains))
    )


if __name__ == "__main__":
    main()