#!/usr/bin/env python3
"""把原始（多行）curl 命令折成单行写入 .env 的 WXREAD_CURL_BASH。

docker-compose 的 env_file 不支持多行值，而浏览器 "Copy as cURL (bash)"
复制出来的是带反斜杠换行的多行命令，直接贴进 .env 只会读到第一行。
config.py 用正则解析，不关心换行，所以折成单行是安全的。

cookie 可能以两种形式出现，与 config.py 的 convert() 保持一致：
  -H 'cookie: a=1; b=2'
  -b 'a=1; b=2'

用法：  python3 set-cookie.py curl.txt
"""
import os
import re
import sys
import pathlib

if len(sys.argv) != 2:
    sys.exit("用法: python3 set-cookie.py <含原始 curl 的文件>")

src = pathlib.Path(sys.argv[1])
env = pathlib.Path(__file__).resolve().parent / ".env"

if not src.is_file():
    sys.exit(f"错误：找不到 {src}")
if not env.is_file():
    sys.exit(f"错误：找不到 {env}")

raw = src.read_text()
# 去掉反斜杠续行，再把所有空白压成单个空格
one = " ".join(re.sub(r"\\\s*\n\s*", " ", raw).split())

if "weread.qq.com/web/book/read" not in one:
    sys.exit("错误：这不像 read 接口的 curl。确认右键复制的是名为 'read' 的那条请求。")

headers = dict(re.findall(r"-H '([^:]+): ([^']+)'", one))

# 与 config.py 同样的两种取法
cookie = next((v for k, v in headers.items() if k.lower() == "cookie"), "")
source = "-H 'cookie:'"
if not cookie:
    m = re.search(r"(?<![\w-])-b '([^']+)'", one)
    if m:
        cookie = m.group(1)
        source = "-b"

if not cookie:
    sys.exit("错误：curl 里既没有 cookie 头也没有 -b 参数。")

names = [c.split("=", 1)[0].strip() for c in cookie.split("; ") if "=" in c]
wr = [n for n in names if n.startswith("wr_")]
if not wr:
    sys.exit(f"错误：cookie 里没有 wr_* 字段（只看到 {', '.join(names[:6])}），可能未登录。")

lines = [l for l in env.read_text().splitlines()
         if not l.startswith("WXREAD_CURL_BASH=")]
lines.append("WXREAD_CURL_BASH=" + one)
env.write_text("\n".join(lines) + "\n")
os.chmod(env, 0o600)

print("✅ 已写入 .env")
print(f"   cookie 来源: {source}")
print(f"   headers: {len(headers)} 个")
print(f"   cookies: {len(names)} 个，其中 wr_* {len(wr)} 个 -> {', '.join(wr)}")
print(f"   单行长度: {len(one)} 字符")
