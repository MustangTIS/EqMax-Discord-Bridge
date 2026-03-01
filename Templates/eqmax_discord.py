import os
import time
import requests
import json
import re
import psutil
import ctypes
import sys
import webbrowser
import subprocess

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "5.5.0" # ← 新バージョンを出す時はここを書き換える
DEFAULT_RAM_LIMIT = 1024
DEFAULT_REPORT_INT = 3600
# MustangTISさんのリポジトリに合わせて修正
RELEASE_PAGE_URL = "https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/latest"

def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = u'mycompany.eqmax.guardian.v5' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

set_taskbar_icon()

# --- 1. アップデートチェック (タグ「vX.X.X」判定型) ---
def check_for_updates():
    print(f"[{time.strftime('%H:%M:%S')}] [Update] Checking for updates...")
    try:
        # User-Agentを指定しないとGitHubに拒否される場合があるため追加
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(RELEASE_PAGE_URL, headers=headers, timeout=5)
        
        if response.status_code == 200:
            target_tag = f"v{CURRENT_VERSION}"
            # 最新リリースのHTML内に自分のバージョンタグが含まれているか
            if target_tag not in response.text:
                print(f"[{time.strftime('%H:%M:%S')}] [Update] 【重要】新バージョンが公開されています。")
                print(f"[{time.strftime('%H:%M:%S')}] [Update] ブラウザで最新版を確認してください。")
                webbrowser.open(RELEASE_PAGE_URL)
                time.sleep(2)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] [Update] バージョン {target_tag} は最新です。")
    except:
        print(f"[{time.strftime('%H:%M:%S')}] [Update] チェックをスキップしました (Network Offline)")

# --- 2. 設定読み込み ---
def load_config():
    config = {"eqmax_dir": "C:/PGF/EqMax_Win64", "destinations": []}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except: pass
    config["eqmax_dir"] = os.path.normpath(config["eqmax_dir"])
    return config

# --- 3. 津波・震度解析ロジック ---
def get_alert_details(text_block):
    if "緊急地震速報：" not in text_block: return None, None, None
    lines = text_block.strip().split('\n')
    shindo, mag_str, mag_val = "不明", "不明", 0.0
    clean_lines, found_essential = [], False 
    
    for line in lines:
        line = line.strip()
        if any(x in line for x in ["PostTweet", "TTwitter", "=", "remaining", "Image Filename:"]): continue
        if not line or "尚、これは" in line: break
        if "震源地：" in line: found_essential = True
        if "推定最大震度：" in line: shindo = line.split("：")[1].strip()
        if "マグニチュード：" in line:
            mag_str = line.split("：")[1].strip()
            m_match = re.search(r"(\d+\.\d+|\d+)", mag_str)
            if m_match: mag_val = float(m_match.group(1)); found_essential = True
        clean_lines.append(line)

    if not found_essential: return None, None, None

    description = "\n".join(clean_lines)
    title = f"[EqMax] EEW Alert📢 【最大震度 {shindo} / {mag_str}】"

    color = 0x808080
    colors = {"7": 0xFF0000, "6強": 0xFF4500, "6弱": 0xFF8C00, "5強": 0xFFA500, "5弱": 0xFFFF00, 
              "4": 0x00FF00, "3": 0x00FFFF, "2": 0x1E90FF, "1": 0xFFFFFF}
    for k, v in colors.items():
        if k in shindo: color = v; break
    
    if any(k in description for k in ["海域", "近海", "沖", "灘", "湾"]):
        if mag_val >= 7.5:
            description = "🚨**【巨大地震・大津波警戒】直ちに避難！**\n\n" + description
            color = 0xff0000
        elif mag_val >= 6.0:
            description = "⚠️**大規模な海域地震：津波警戒**\n\n" + description
            color = 0xffa500
        else:
            description = "ℹ️海域地震：念のため注意\n\n" + description

    return title, description, color

# --- 4. Discord送信ロジック ---
def process_log_update(content, config_dest):
    pattern = re.compile(r"(緊急地震速報：.*?)(C:\\.*?\.png)", re.DOTALL)
    matches = pattern.findall(content)
    if not matches: return

    full_text, image_path = matches[-1]
    title, description, color = get_alert_details(full_text)
    if not title: return

    print(f"\n[{time.strftime('%H:%M:%S')}] 📢 EEW検知: {title}")

    for dest in config_dest:
        url = dest.get("url")
        style = str(dest.get("style", "embed")).lower()
        if not url: continue

        if style == "simple":
            single_line = f"📢 **{title}** / {description}".replace("\n", " / ").strip()
            payload = {"content": single_line}
        else:
            payload = {
                "embeds": [{
                    "title": title, "description": description, "color": color,
                    "image": {"url": "attachment://image.png"},
                    "footer": {"text": f"EqMax Guardian v{CURRENT_VERSION}"}
                }]
            }

        try:
            path_to_img = image_path.strip()
            if os.path.exists(path_to_img):
                with open(path_to_img, "rb") as f:
                    response = requests.post(url, data={"payload_json": json.dumps(payload)}, 
                                             files={"file": ("image.png", f, "image/png")}, timeout=10)
            else:
                response = requests.post(url, json=payload, timeout=5)
            
            status = "Success" if response.status_code in [200, 204] else f"Failed({response.status_code})"
            print(f"[{time.strftime('%H:%M:%S')}]  └─ [{status}] Discord送信完了 ({style})")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}]  └─ [Error] 送信エラー: {e}")

# --- 5. 死活監視 ---
def maintain_eqmax_health(exe_path):
    target_proc = None
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == "EqMax.exe":
                target_proc = proc; break
        except: continue

    if target_proc is None:
        if os.path.exists(exe_path):
            print(f"[{time.strftime('%H:%M:%S')}] EqMax不在：最小化で起動。")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
    else:
        try:
            mem_mb = target_proc.memory_info().rss / (1024 * 1024)
            if mem_mb > DEFAULT_RAM_LIMIT:
                print(f"[{time.strftime('%H:%M:%S')}] RAM超過({mem_mb:.1f}MB)：再起動。")
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
        except: pass

# --- 6. メインループ ---
def start_combined_monitor():
    check_for_updates() # 起動時にチェック
    config = load_config()
    exe_path = os.path.join(config["eqmax_dir"], "EqMax.exe")
    log_file = os.path.join(config["eqmax_dir"], "Twitter.log")
    
    print(f"="*50 + f"\n EqMax Guardian v{CURRENT_VERSION}\n" + f"="*50)

    last_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    pending_block = ""
    health_counter = 0

    while True:
        try:
            if health_counter % 10 == 0:
                maintain_eqmax_health(exe_path)
            
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size > last_size:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_size)
                        for line in f:
                            raw_line = line.strip()
                            if "緊急地震速報：" in raw_line:
                                pending_block = raw_line + "\n"
                            elif pending_block:
                                pending_block += raw_line + "\n"
                                if ".png" in raw_line and "C:\\" in raw_line:
                                    time.sleep(1); process_log_update(pending_block, config["destinations"]); pending_block = ""
                    last_size = current_size
            
            health_counter += 1
            if health_counter % DEFAULT_REPORT_INT == 0:
                current_ram = 0.0
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'] == "EqMax.exe":
                            current_ram = proc.memory_info().rss / (1024 * 1024)
                            break
                    except: continue
                status_msg = f"正常稼働中 (EqMax RAM: {current_ram:.1f} MB)" if current_ram > 0 else "正常稼働中 (EqMax停止中)"
                print(f"[{time.strftime('%H:%M:%S')}] {status_msg}")
            
            time.sleep(1)
        except: time.sleep(1)

if __name__ == "__main__":
    start_combined_monitor()