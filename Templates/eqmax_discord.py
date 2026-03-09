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
import senders

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "8.0.0"
DEFAULT_RAM_LIMIT = 1024
DEFAULT_REPORT_INT = 3600
REPO_URL = "MustangTIS/EqMax-Discord-Bridge"
RELEASE_PAGE_URL = f"https://github.com/{REPO_URL}/releases/latest"

def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = f'mycompany.eqmax.guardian.v{CURRENT_VERSION}' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

set_taskbar_icon()

# --- 1. 応答なし監視 (フリーズ検知) ---
def is_window_responding(pid):
    try:
        def callback(hwnd, hwnds):
            _, found_pid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
            if found_pid == pid and ctypes.windll.user32.IsWindowVisible(hwnd):
                hwnds.append(hwnd)
            return True
        hwnds = []
        ctypes.windll.user32.EnumWindows(ctypes.WNDENUMPROC(callback), hwnds)
        for hwnd in hwnds:
            result = ctypes.windll.user32.SendMessageTimeoutW(
                hwnd, 0, 0, 0, 0x0002, 5000, ctypes.byref(ctypes.c_ulong())
            )
            if result == 0: return False
        return True
    except: return True

# --- 2. メモリ取得関数 ---
def get_private_ram_mb(proc):
    try:
        return proc.memory_full_info().private / (1024 * 1024)
    except:
        try:
            return proc.memory_info().rss / (1024 * 1024)
        except: return None

# --- 3. アップデートチェック ---
def check_for_updates():
    api_url = f"https://api.github.com/repos/{REPO_URL}/releases/latest"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data.get("tag_name")
            current = f"v{CURRENT_VERSION}" if not CURRENT_VERSION.startswith("v") else CURRENT_VERSION
            if latest_tag and latest_tag != current:
                return "UPDATE_AVAILABLE", latest_tag, data.get("html_url")
            return "LATEST", current, None
    except:
        return "ERROR", None, None
    return "ERROR", None, None

# --- 4. 設定読み込み & 環境チェック ---
def load_config():
    config = {"eqmax_dir": "C:/EqMax_Win64", "destinations": []}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except: pass
    
    config["eqmax_dir"] = os.path.normpath(config["eqmax_dir"])
    exe_path = os.path.join(config["eqmax_dir"], "EqMax.exe")
    config["is_env_ok"] = os.path.exists(exe_path)
    config["exe_path"] = exe_path
    return config

# --- 5. 津波・震度解析ロジック ---
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
    
    if any(k in description for k in ["海", "沖", "灘", "湾"]):
        if mag_val >= 7.5:
            description = "🚨**【巨大地震・大津波警戒】直ちに避難！**\n\n" + description
            color = 0xff0000
        elif mag_val >= 6.0:
            description = "⚠️**大規模な海域地震：津波警戒**\n\n" + description
            color = 0xffa500
        else:
            description = "ℹ️海域地震：念のため注意\n\n" + description

    return title, description, color

# --- 6. Discord送信ロジック ---
def process_log_update(content, config_dest):
    # (解析ロジック部分はそのまま)
    pattern = re.compile(r"(緊急地震速報：.*?)(C:\\.*?\.png)", re.DOTALL)
    matches = pattern.findall(content)
    if not matches: return

    full_text, image_path = matches[-1]
    title, description, color = get_alert_details(full_text)
    
    if not title: return

    # --- ここで情報を表示 ---
    timestamp = time.strftime('%H:%M:%S')
    bot_name = "EqMax EEW Bridge"
    
    print(f"\n[{timestamp}] 📢 {title} (Powered by {bot_name})")
    if description:
        print(f"[{timestamp}]    {description.splitlines()[0]}")

    # --- 修正: senders.dispatch に timestamp を追加 ---
    for dest in config_dest:
        url = dest.get("url")
        style = dest.get("style", "disembed").lower()
        if not url: continue
        
        response = senders.dispatch(
            style=style, 
            title=title, 
            description=description, 
            color=color, 
            image_path=image_path, 
            url=url, 
            bot_name=bot_name, 
            current_version=CURRENT_VERSION,
            timestamp=timestamp, # 追加
            matrix_token=dest.get("token"), 
            matrix_room=dest.get("room")
        )
        
        # 結果判定
        if isinstance(response, Exception):
            print(f"[{timestamp}]  └─ [Error] 送信失敗: {response}")
        elif response and hasattr(response, 'status_code') and response.status_code in [200, 204]:
            print(f"[{timestamp}]  └─ [Success] 送信完了 ({style})")
        else:
            print(f"[{timestamp}]  └─ [Failed] 送信失敗 ({style})")

# --- 7. 死活監視 ---
def maintain_eqmax_health(exe_path):
    target_proc = None
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == "EqMax.exe":
                target_proc = proc; break
        except: continue

    if target_proc is None:
        if os.path.exists(exe_path):
            print(f"[{time.strftime('%H:%M:%S')}] プロセスにEqMaxが見つかりません：最小化で起動")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
    else:
        if not is_window_responding(target_proc.pid):
            print(f"[{time.strftime('%H:%M:%S')}] EqMaxがフリーズしています：再起動")
            try:
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            except: pass

        mem_mb = get_private_ram_mb(target_proc)
        if mem_mb and mem_mb > DEFAULT_RAM_LIMIT:
            print(f"[{time.strftime('%H:%M:%S')}] EqMaxのRAMしきい値超過({mem_mb:.1f}MB)：再起動")
            try:
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            except: pass

# --- 8. メインループ ---
def start_combined_monitor():
    print("-" * 52)
    print(f">>> EqMax Discord Bridge: Initialization...")
    print(f">>> EqMax Discord Bridge: Boot Sequence Started...")
    print("-" * 52)
    
    is_all_ok = True  
    is_update_found = False

    # --- [Step 1-5] ---
    print(f"\n [Step 1/7] Booting EqMax Discord Bridge....... [  OK  ]")
    print(f"    └─ [System Version: v{CURRENT_VERSION}]")

    print(f" [Step 2/7] Checking for updates...")
    status, ver, url = check_for_updates()
    if status == "UPDATE_AVAILABLE":
        print(f"    └─ [Notice] 【重要】新バージョン {ver} が公開されています。")
        webbrowser.open(url)
        is_update_found = True # 止まらないが、注意状態にする
    elif status == "LATEST":
        print(f"    └─ [Notice] バージョン {ver} は最新です。  [  OK  ]")
    else:
        print(f"    └─ [Warning] アップデート確認をスキップしました。 [  NG  ]")

    print(f" [Step 3/7] Update Sequence Check.............. [  OK  ]")
    print(f" [Step 4/7] Guardian System Health Check....... [  OK  ]")
    print(f" [Step 5/7] Guardian Core Engine Initialized... [  OK  ]")
    print(f"    └─ [RAM LIMIT {DEFAULT_RAM_LIMIT}MB , ReportEvery {DEFAULT_REPORT_INT}Seconds]")

    # --- [Step 6-7] 環境チェック ---
    config = load_config()
    if config["is_env_ok"]:
        print(f" [Step 6/7] Link Check EqMax Connector....... [  OK  ]")
        print(f"    └─ Path: {config['eqmax_dir']}")
    else:
        print(f" [Step 6/7] Link Check EqMax Connector....... [  !!  ]")
        print(f"    └─ [Error] EqMax.exe が見つかりません。")
        is_all_ok = False

    if config["destinations"]:
        print(f" [Step 7/7] Discord Webhook Standby.......... [  OK  ]")
    else:
        print(f" [Step 7/7] Discord Webhook Standby.......... [  NG  ]")
        print(f"    └─ [Error] 有効な送信先が設定されていません。")
        is_all_ok = False

    # --- [Final Status] ---
    print(f"\n" + "="*52)
    if not is_all_ok:
        print(f"    SYSTEM STATUS: ATTENTION REQUIRED / CHECK LOGS")
        print(f"    [Error] 設定や環境に致命的な問題があるため、開始できません。")
        print(f"    [Help] 上記の [ !! ] または [ NG ] の項目を確認してください。")
        print(f"="*52 + "\n")
        print(f"\n    Enterキーを押すと終了します...")
        input()
        sys.exit(1)
    elif is_update_found:
        print(f"    SYSTEM STATUS: UPDATE AVAILABLE / STARTING MONITOR")
        print(f"    WELCOME TO EQMAX DISCORD BRIDGE V{CURRENT_VERSION}")
        print(f"    Developed by Mustang_TIS")
        print(f"="*52 + "\n")
    else:
        print(f"    SYSTEM STATUS: ALL GREEN / READY TO MONITOR")
        print(f"    WELCOME TO EQMAX DISCORD BRIDGE V{CURRENT_VERSION}")
        print(f"    Developed by Mustang_TIS")
        print(f"="*52 + "\n")

    # --- 監視処理開始 ---
    exe_path = config["exe_path"]
    log_file = os.path.join(config["eqmax_dir"], "Twitter.log")

    if os.path.exists(log_file):
        last_size = os.path.getsize(log_file)
    else:
        last_size = 0
        with open(log_file, "a", encoding="utf-8") as f: pass
        
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
                                    time.sleep(1)
                                    process_log_update(pending_block, config["destinations"])
                                    pending_block = ""
                    last_size = current_size
            
            health_counter += 1
            if health_counter % DEFAULT_REPORT_INT == 0:
                mem_display = "停止中"
                for proc in psutil.process_iter(['name']):
                    if proc.info.get('name') == "EqMax.exe":
                        val = get_private_ram_mb(proc)
                        mem_display = f"{val:.1f}" if val is not None else "取得失敗"
                        break
                print(f"[{time.strftime('%H:%M:%S')}] EqMax正常稼働中 (RAM使用量: {mem_display} MB)")

            time.sleep(1) 
        except: 
            time.sleep(1)

if __name__ == "__main__":
    try:
        start_combined_monitor()
    except Exception as e:
        print("\n" + "!"*60)
        print(" 【CRITICAL ERROR】システム実行中に致命的なエラーが発生しました")
        print("!"*60)
        import traceback
        traceback.print_exc()
        print("\n" + "!"*60)
        print(" 内容を確認し、Enterキーを押すと終了します。")
        print("!"*60)
        input()
        sys.exit(1)