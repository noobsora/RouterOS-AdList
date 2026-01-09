import requests
import re
import logging
import os
import shutil
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO, format=LOG_FORMAT, handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

OUTPUT_FILE = "ros-adlist.txt"

SOURCES = {
    "Cats-Team": "https://raw.githubusercontent.com/Cats-Team/AdRules/main/mosdns_adrules.txt",
    "AdGuardDnsFilter": "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_1_DnsFilter/filter.txt",
    "AdGuard-DNS-Popup-Hosts": "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/refs/heads/main/filters/general/filter_59_DnsPopupsFilter/filter.txt",
    "AWAvenue-Ads-Rule": "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/Filters/AWAvenue-Ads-Rule-RouterOS-Adlist.txt",
    "217heidai-AdblockHostsLite": "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockhostslite.txt",
}

# 合并跳过规则以提高效率
# 1. 包含 * 的 (通配符)
# 2. 包含正则符号 [] {} 的
# 3. 看起来像路径的 (包含 /)
INVALID_CHARS_PATTERN = re.compile(r"[*\[\]{}/]")

# 纯IP匹配 (用于排除纯IP行)
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# 域名匹配正则 (更严格的 TLD 校验，排除 IP)
# 不以 - 或 . 开头，由点分隔的部分，最后一部分必须是2个以上字母
DOMAIN_PATTERN = re.compile(
    r"(?i)\b((?=[a-z0-9-]{1,63}\.)(xn--[a-z0-9]+|[a-z0-9]+(-[a-z0-9]+)*)\.)+[a-z]{2,63}\b"
)


def get_hkt_time():
    """获取香港时间"""
    return (
        datetime.now(timezone.utc)
        .astimezone(ZoneInfo("Asia/Hong_Kong"))
        .strftime("%Y-%m-%d %H:%M GMT+8")
    )


def create_session():
    """创建高可用会话"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def clean_line(line):
    """
    清洗行数据：
    1. 去除注释 (# 和 !)
    2. 去除 Adblock 修饰符 (||, ^, @@)
    3. 去除行首 IP (如 127.0.0.1 google.com)
    """
    # 1. 去除行内注释 (Adblock 常用 ! 或 #)
    if "#" in line:
        line = line.split("#")[0]
    if "!" in line:
        line = line.split("!")[0]

    line = line.strip()

    # 2. 忽略白名单和空行
    if not line or line.startswith("@@"):
        return None

    # 3. 清理 Adblock 语法
    # 移除 || (开始) 和 ^ (结束) 以及 | (行首行尾)
    line = line.replace("||", "").replace("^", "").strip("|")

    # 4. 处理 Hosts 格式 (去除前面的 IP)
    # 分割空格，取最后一个部分通常是域名
    parts = line.split()
    if len(parts) >= 2:
        # 如果第一部分是 IP (简单判断)，取后面部分
        if parts[0] in ["0.0.0.0", "127.0.0.1", "::1"]:
            line = parts[-1]

    return line.strip()


def extract_domains(text):
    """提取并过滤域名"""
    domains = set()

    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue

        # 如果清洗后的行还包含 /，说明是具体路径规则 (如 example.com/ad.js)
        # DNS 封锁无法处理路径，必须丢弃，否则会误杀整个域名
        if INVALID_CHARS_PATTERN.search(line):
            continue

        # 提取域名
        matches = DOMAIN_PATTERN.finditer(line)
        for match in matches:
            domain = match.group().lower()

            # 二次校验：排除 IP 地址和无效字符
            if not IP_PATTERN.match(domain) and not INVALID_CHARS_PATTERN.search(
                domain
            ):
                domains.add(domain)

    return domains


def main():
    all_domains = set()
    source_stats = {}
    session = create_session()

    logger.info("🚀 开始更新域名列表...")

    for name, url in SOURCES.items():
        try:
            logger.info(f"⬇ 正在获取：{name}")
            res = session.get(url, timeout=30)
            res.raise_for_status()

            current_domains = extract_domains(res.text)
            count = len(current_domains)
            source_stats[name] = count
            logger.info(f"  └─ 提取到 {count} 条有效域名")

            all_domains.update(current_domains)

        except Exception as e:
            logger.error(f"❌ 获取 {name} 失败: {e}")
            source_stats[name] = 0

    if not all_domains:
        logger.error("❌ 未提取到任何域名，终止写入。")
        return

    sorted_domains = sorted(all_domains)
    total_count = len(sorted_domains)

    # 写入临时文件
    temp_file = OUTPUT_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(f"# 更新时间：{get_hkt_time()}\n")
            f.write("# 数据来源：\n")
            for name, count in source_stats.items():
                f.write(f"# - {name}：{count} 条\n")
            f.write(f"# 合并去重后总数：{total_count:,} 条\n\n")

            f.writelines(f"0.0.0.0 {domain}\n" for domain in sorted_domains)

        # 移动临时文件覆盖原文件
        shutil.move(temp_file, OUTPUT_FILE)
        logger.info(f"\n✅ 成功生成 {OUTPUT_FILE}，共 {total_count:,} 个域名")

    except IOError as e:
        logger.error(f"❌ 文件写入失败: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户手动中止")
