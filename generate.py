#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 AI 供应链股票行情并生成 index.html。
在 GitHub Actions 上每天定时运行（盘前/盘后各一次）。
数据来源：Yahoo Finance（通过 yfinance）。
"""
import json
import datetime
from zoneinfo import ZoneInfo
import yfinance as yf

# 观察列表：t=代码, n=名称, note=备注
TICKERS = {
    "storage": [
        {"t": "MU",   "n": "Micron 美光",            "note": "DRAM/NAND/HBM"},
        {"t": "WDC",  "n": "Western Digital 西部数据", "note": "HDD"},
        {"t": "STX",  "n": "Seagate 希捷",            "note": "HDD 双寡头"},
        {"t": "SNDK", "n": "SanDisk 闪迪",            "note": "NAND，产能售罄"},
    ],
    "cooling": [
        {"t": "VRT",   "n": "Vertiv 维谛",          "note": "液冷+供配电纯标的"},
        {"t": "MOD",   "n": "Modine",              "note": "小盘纯标的，弹性大"},
        {"t": "ETN",   "n": "Eaton 伊顿",           "note": "综合电气"},
        {"t": "NVT",   "n": "nVent",               "note": "散热配套供应商"},
        {"t": "SBGSY", "n": "Schneider 施耐德 ADR",  "note": "综合电气+软件"},
    ],
    "power": [
        {"t": "CEG", "n": "Constellation 星座能源", "note": "核电，AI数据中心供电"},
        {"t": "VST", "n": "Vistra",               "note": "独立发电商"},
        {"t": "GEV", "n": "GE Vernova",           "note": "电力设备/燃机/电网"},
        {"t": "TLN", "n": "Talen Energy",         "note": "核电运营商"},
        {"t": "NRG", "n": "NRG Energy",           "note": "综合电力/零售"},
    ],
}


def fetch(symbol):
    """返回 (最新价, 当日涨跌幅%, 数据日期) ；失败返回 (None, None, None)"""
    try:
        hist = yf.Ticker(symbol).history(period="7d", auto_adjust=False)
        if hist is None or len(hist) == 0:
            return None, None, None
        closes = hist["Close"].dropna()
        if len(closes) == 0:
            return None, None, None
        last = float(closes.iloc[-1])
        prev = float(closes.iloc[-2]) if len(closes) >= 2 else None
        chg = round((last / prev - 1) * 100, 2) if prev else None
        as_of = closes.index[-1].strftime("%Y-%m-%d")
        return round(last, 2), chg, as_of
    except Exception as e:
        print(f"[warn] {symbol}: {e}")
        return None, None, None


def build():
    as_of = None
    data = {}
    for sector, rows in TICKERS.items():
        out = []
        for r in rows:
            p, c, d = fetch(r["t"])
            if d and (as_of is None or d > as_of):
                as_of = d
            out.append({"t": r["t"], "n": r["n"], "note": r["note"], "p": p, "c": c})
        data[sector] = out

    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.datetime.now(tz)
    # 用北京时间判断这次大致是盘前(<12点)还是盘后
    label = "盘前" if now.hour < 12 else "盘后"
    updated = now.strftime("%Y-%m-%d %H:%M") + f" 北京时间 ({label})"
    as_of = as_of or now.strftime("%Y-%m-%d")

    payload = {
        "asOf": as_of,
        "updatedAt": updated,
        "storage": data["storage"],
        "cooling": data["cooling"],
        "power": data["power"],
    }

    html = TEMPLATE.replace("/*DATA*/null", json.dumps(payload, ensure_ascii=False))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 已生成，数据截至", as_of)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 供应链股票追踪</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js"></script>
<style>
:root{color-scheme:light}*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#f7f8fa;color:#1a1d21;line-height:1.5}
.wrap{max-width:860px;margin:0 auto;padding:24px 18px 48px}
h1{font-size:22px;margin:0 0 4px}.meta{color:#6b7280;font-size:13px;margin-bottom:18px}
.section-title{font-size:16px;font-weight:600;margin:26px 0 10px;display:flex;align-items:center;gap:8px}
.dot{width:9px;height:9px;border-radius:50%}.dot.storage{background:#2563eb}.dot.cooling{background:#ea580c}.dot.power{background:#16a34a}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
th,td{padding:11px 12px;text-align:right;font-size:14px;border-bottom:1px solid #eef0f3}
th{background:#f1f3f6;color:#6b7280;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
th:first-child,td:first-child{text-align:left}tr:last-child td{border-bottom:none}
.tkr{font-weight:700}.nm{color:#6b7280;font-size:12px}
.price{font-variant-numeric:tabular-nums;font-weight:600}.chg{font-variant-numeric:tabular-nums;font-weight:600}
.up{color:#16a34a}.down{color:#dc2626}.flat{color:#6b7280}.note{color:#9ca3af;font-size:12px}
.chart-box{background:#fff;border-radius:10px;padding:16px;margin-top:22px;box-shadow:0 1px 3px rgba(0,0,0,.06);height:300px}
.disclaimer{margin-top:26px;padding:13px 15px;background:#fff7ed;border:1px solid #fed7aa;border-radius:9px;color:#9a3412;font-size:12.5px}
.src{margin-top:14px;font-size:11.5px;color:#9ca3af}
</style>
</head>
<body>
<div class="wrap">
  <h1>AI 供应链股票追踪</h1>
  <div class="meta" id="updated"></div>
  <div class="section-title"><span class="dot storage"></span>存储（内存 / 硬盘）</div>
  <table><thead><tr><th>代码</th><th>最新价 (USD)</th><th>当日涨跌</th><th>备注</th></tr></thead><tbody id="storage-rows"></tbody></table>
  <div class="section-title"><span class="dot cooling"></span>散热</div>
  <table><thead><tr><th>代码</th><th>最新价 (USD)</th><th>当日涨跌</th><th>备注</th></tr></thead><tbody id="cooling-rows"></tbody></table>
  <div class="section-title"><span class="dot power"></span>电力（发电 / 电网）</div>
  <table><thead><tr><th>代码</th><th>最新价 (USD)</th><th>当日涨跌</th><th>备注</th></tr></thead><tbody id="power-rows"></tbody></table>
  <div class="chart-box"><canvas id="chgChart"></canvas></div>
  <div class="disclaimer">⚠️ 仅供参考，不构成投资建议。数据来自 Yahoo Finance，每个交易日自动刷新两次（盘前/盘后），可能有延迟，请以券商实时行情为准。</div>
  <div class="src" id="asof"></div>
</div>
<script>
const DATA = /*DATA*/null;
function fmtPrice(p){ if(p===null||p===undefined) return "—"; return p.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}); }
function chgCell(c){ if(c===null||c===undefined) return '<span class="flat">—</span>'; const cls=c>0?"up":(c<0?"down":"flat"); const sign=c>0?"+":""; return '<span class="chg '+cls+'">'+sign+c.toFixed(2)+'%</span>'; }
function row(d){ return '<tr><td><span class="tkr">'+d.t+'</span><br><span class="nm">'+d.n+'</span></td><td class="price">'+fmtPrice(d.p)+'</td><td>'+chgCell(d.c)+'</td><td class="note">'+d.note+'</td></tr>'; }
document.getElementById("storage-rows").innerHTML = DATA.storage.map(row).join("");
document.getElementById("cooling-rows").innerHTML = DATA.cooling.map(row).join("");
document.getElementById("power-rows").innerHTML = DATA.power.map(row).join("");
document.getElementById("updated").textContent = "数据截至 " + DATA.asOf + " · 每交易日自动刷新两次：盘前/盘后";
document.getElementById("asof").textContent = "来源：Yahoo Finance · 更新于 " + DATA.updatedAt;
const all = DATA.storage.concat(DATA.cooling, DATA.power).filter(d=>d.c!==null);
new Chart(document.getElementById("chgChart"), {
  type:"bar",
  data:{ labels: all.map(d=>d.t), datasets:[{ label:"当日涨跌 %", data: all.map(d=>d.c), backgroundColor: all.map(d=>d.c>=0?"#16a34a":"#dc2626"), borderRadius:4 }] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{display:false}, title:{display:true, text:"当日涨跌幅对比 (%)"} }, scales:{ y:{ ticks:{ callback:v=>v+"%" } } } }
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
