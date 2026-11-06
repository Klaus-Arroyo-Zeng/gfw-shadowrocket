
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

SOURCE_URL = (
    "https://raw.githubusercontent.com/MetaCubeX/"
    "meta-rules-dat/refs/heads/meta/geo/geosite/gfw.list"
)

OUTPUT_FILE = Path("Shadowrocket/GFW.list")

def convert(line):
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line.startswith("+."):
        return "DOMAIN-SUFFIX," + line[2:]

    if line.startswith("full:"):
        return "DOMAIN," + line[5:]

    if line.startswith("keyword:"):
        return "DOMAIN-KEYWORD," + line[8:]

    if line.startswith("regexp:"):
        return "DOMAIN-REGEX," + line[7:]

    if line.startswith("domain:"):
        return "DOMAIN-SUFFIX," + line[7:]

    return "DOMAIN," + line


def main():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "GitHub-Actions"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read().decode("utf-8")

    rules = []
    seen = set()

    for line in content.splitlines():
        rule = convert(line)

        if rule and rule not in seen:
            seen.add(rule)
            rules.append(rule)

    # 分类统计
    suffix_count = sum(r.startswith("DOMAIN-SUFFIX,") for r in rules)
    domain_count = sum(r.startswith("DOMAIN,") for r in rules)
    keyword_count = sum(r.startswith("DOMAIN-KEYWORD,") for r in rules)
    regex_count = sum(r.startswith("DOMAIN-REGEX,") for r in rules)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    header = [
        "# NAME: GFW",
        "# SOURCE: MetaCubeX/meta-rules-dat",
        f"# UPDATED: {updated}",
        f"# DOMAIN: {domain_count}",
        f"# DOMAIN-SUFFIX: {suffix_count}",
        f"# DOMAIN-KEYWORD: {keyword_count}",
        f"# DOMAIN-REGEX: {regex_count}",
        f"# TOTAL: {len(rules)}",
        ""
    ]

    OUTPUT_FILE.write_text(
        "\n".join(header + rules) + "\n",
        encoding="utf-8"
    )

    print(f"Converted {len(rules)} rules")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
