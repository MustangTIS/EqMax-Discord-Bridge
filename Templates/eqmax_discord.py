import os
import time
import requests
import json
import re
import psutil  # 死活監視に必要
import ctypes
import sys

# --- タスクバーアイコン修正用の呪文 ---
def set_taskbar_icon():
    if sys.platform == "win32":
        # 独自のAppIDを設定することで、cmd.exeとは別のアプリとして認識させる
        myappid = u'mycompany.eqmax.guardian.v4' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

set_taskbar_icon()

# --- 1. 設定の読み込み (v3ベース) ---
def load_config():
    config = {
        "destinations": [],
        "eqmax_dir": "C:\\EqMax_Win64"
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception as e: print(f"設定失敗: {e}")
    return config

config = load_config()
EQ_DIR = os.path.normpath(config["eqmax_dir"])
LOG_FILE = os.path.join(EQ_DIR, "Twitter.log")
EQ_EXE = os.path.join(EQ_DIR, "EqMax.exe")

# --- 2. 死活監視ロジック (Eq_Watchdogより統合) ---
def maintain_eqmax_health(exe_path, check_full=False):
    process_name = "EqMax.exe"
    target_proc = None
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                target_proc = proc
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied): continue

    if target_proc is None:
        if os.path.exists(exe_path):
            print(f"[{time.strftime('%H:%M:%S')}] EqMax停止検知：再起動します。")
            os.startfile(exe_path)
        return

    if check_full:
        try:
            if not target_proc.is_running() or target_proc.status() == psutil.STATUS_ZOMBIE:
                print(f"[{time.strftime('%H:%M:%S')}] EqMaxフリーズ検知：強制再起動。")
                target_proc.kill()
                time.sleep(1)
                os.startfile(exe_path)
                return
            mem_mb = target_proc.memory_info().rss / (1024 * 1024)
            if mem_mb > 1024:
                print(f"[{time.strftime('%H:%M:%S')}] メモリ超過({mem_mb:.1f}MB)：リセット。")
                target_proc.kill()
                time.sleep(1)
                os.startfile(exe_path)
        except Exception: pass

# --- 3. 解析・通知ロジック (v3の完全なロジックを維持) ---
def get_alert_details(text_block):
    if "緊急地震速報：" not in text_block: return None, None, None
    lines = text_block.strip().split('\n')
    shindo, mag_str, mag_val = "不明", "不明", 0.0
    clean_lines, found_essential = [], False 
    
    for line in lines:
        line = line.strip()
        if any(x in line for x in ["PostTweet", "TTwitter", "=", "remaining"]): continue
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

    # 震度別カラー (v3のフルリスト)
    color = 0x808080
    if "7" in shindo: color = 0xFF0000
    elif "6強" in shindo: color = 0xFF4500
    elif "6弱" in shindo: color = 0xFF8C00
    elif "5強" in shindo: color = 0xFFA500
    elif "5弱" in shindo: color = 0xFFFF00
    elif "4" in shindo: color = 0x00FF00
    elif "3" in shindo: color = 0x00FFFF
    elif "2" in shindo: color = 0x1E90FF
    elif "1" in shindo: color = 0xFFFFFF
    
    # 津波判定 (v3の警告文)
    tsunami_keywords = ["海域", "近海", "沖", "灘", "湾"]
    if any(k in description for k in tsunami_keywords):
        if mag_val >= 7.5:
            description = "🚨**【巨大地震・大津波警戒】直ちに避難！**\n\n" + description
            color = 0xff0000
        elif mag_val >= 6.0:
            description = "⚠️**大規模な海域地震：津波警戒**\n\n" + description
            color = 0xffa500
        else:
            description = "ℹ️海域地震：念のため注意\n\n" + description

    return title, description, color

def process_log_update(content):
    # v3方式の画像パス抽出
    pattern = re.compile(r"(緊急地震速報：.*?)(C:\\.*?\.png)", re.DOTALL)
    matches = pattern.findall(content)
    if not matches: return

    full_text, image_path = matches[-1]
    image_path = image_path.strip()
    
    title, description, color = get_alert_details(full_text)
    if not title: return

    for dest in config.get("destinations", []):
        url = dest.get("url")
        style = dest.get("style", "embed")
        if not url: continue

        if style == "simple":
            # 改行を消して1行にする (あなたの要望)
            single_line = f"📢 **{title}** / {description}".replace("\n", " ").strip()
            payload = {"content": single_line}
        else:
            payload = {
                "embeds": [{
                    "title": title, "description": description, "color": color,
                    "image": {"url": "attachment://image.png"},
                    "footer": {"text": "EqMax-Discord Bridge v4.6"}
                }]
            }

        try:
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    requests.post(url, data={"payload_json": json.dumps(payload)}, files={"file": ("image.png", f, "image/png")})
            else:
                requests.post(url, json=payload)
        except Exception: pass

# --- 4. メインループ (v3の安定トリガーを採用) ---
def watch_log():
    if not config.get("destinations"):
        print("エラー: 送信先が設定されていません。")
        return

    print(f"=== EqMax-Discord-Bridge v4.6 Running ===")
    last_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
    pending_block = ""
    health_counter = 0

    while True:
        try:
            # 死活監視の実行
            health_counter += 1
            maintain_eqmax_health(EQ_EXE, check_full=(health_counter >= 10))
            if health_counter >= 10: health_counter = 0

            if not os.path.exists(LOG_FILE):
                time.sleep(1); continue

            current_size = os.path.getsize(LOG_FILE)
            if current_size < last_size: last_size = 0
            
            if current_size > last_size:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                
                for line in new_lines:
                    line = line.strip()
                    if not line or "PostTweet" in line: continue
                    
                    if "緊急地震速報：" in line:
                        pending_block = line + "\n"
                    elif pending_block:
                        pending_block += line + "\n"
                        # 【v3のコア】画像パスが来るまで絶対に送らない
                        if ".png" in line and "C:\\" in line:
                            time.sleep(1) # 書き出し完了待ち
                            process_log_update(pending_block)
                            pending_block = ""
                last_size = current_size
        except Exception as e: print(f"ループエラー: {e}")
        time.sleep(1)

if __name__ == "__main__":
    watch_log()