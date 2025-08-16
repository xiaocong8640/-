#!/usr/bin/env python3
"""
Naisi Wednesday 10:00 coupon grabber
无需改动，所有可变信息走环境变量
"""
import os
import time
import requests
from bs4 import BeautifulSoup

# ---------- 配置 ----------
LOGIN_URL   = "http://www.51ns.cn/nlogin"
COUPON_URL  = "http://www.51ns.cn/nlogin"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
# --------------------------

sess = requests.Session()
sess.headers.update({"User-Agent": UA})

def login():
    """登录并返回 True/False"""
    username = os.getenv("NAISI_USERNAME")
    password = os.getenv("NAISI_PASSWORD")
    if not username or not password:
        print("❌ 未配置 NAISI_USERNAME / NAISI_PASSWORD")
        return False

    # 先拿一次登录页，解析 token
    r = sess.get(LOGIN_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    token = soup.find("input", attrs={"name": "__token__"})
    token = token["value"] if token else ""

    payload = {
        "username": username,
        "password": password,
        "__token__": token,
    }
    r = sess.post(LOGIN_URL, data=payload)
    r.raise_for_status()
    if "退出" in r.text or username in r.text:
        print("✅ 登录成功")
        return True
    else:
        print("❌ 登录失败，请检查用户名密码")
        return False

def grab():
    """领券中心一键领取"""
    r = sess.get(COUPON_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    # 找到所有“立即领取”按钮
    grab_btn = soup.find_all("a", string="立即领取")
    if not grab_btn:
        print("⚠️  当前无可领取的券，或未到周三 10:00")
        return

    for btn in grab_btn:
        link = btn.get("href")
        if not link or "coupon_id" not in link:
            continue
        full = "http://www.51ns.cn" + link if link.startswith("/") else link
        sess.get(full)      # 触发领券
        print(f"🎁 已尝试领取：{full}")

if __name__ == "__main__":
    if login():
        time.sleep(2)  # 稍微等下，避免触发防刷
        grab()
