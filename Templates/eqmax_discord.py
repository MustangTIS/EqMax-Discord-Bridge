# eqmax_discord.py
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
import datetime # 日付ベースのパス生成用
import senders
import fixed_report_parser # 自作モジュール
import eew_parser

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "10.0.0"
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

# --- 6. 速報処理（メイン側） ---
def process_log_update(content, config_dest, current_version):
    print(f"\n--- 速報検知 (Log) ---\n{content.strip()}\n---------------------")

    # 外部モジュールで解析
    title, description, color, image_path = eew_parser.parse_log_content(content)

    if not title: return

    timestamp = time.strftime('%H:%M:%S')
    bot_name = "EqMax EEW Bridge"
    shared_image_url = None

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
            current_version=current_version,
            timestamp=timestamp,
            matrix_token=dest.get("token"), 
            matrix_room=dest.get("room"),
            shared_image_url=shared_image_url 
        )
        
        # --- 画像URLの抽出ロジック ---
        if style in ["disembed", "dissimple"] and response and hasattr(response, 'status_code') and response.status_code in [200, 204]:
            try:
                data = response.json()
                if "attachments" in data and len(data["attachments"]) > 0:
                    shared_image_url = data["attachments"][0].get("url")
                elif "embeds" in data and len(data["embeds"]) > 0 and "image" in data["embeds"][0]:
                    shared_image_url = data["embeds"][0]["image"].get("url")
            except:
                pass
        
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
            print(f"\n[{time.strftime('%H:%M:%S')}] プロセスにEqMaxが見つかりません：最小化で起動")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
    else:
        if not is_window_responding(target_proc.pid):
            print(f"\n[{time.strftime('%H:%M:%S')}] EqMaxがフリーズしています：再起動")
            try:
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            except: pass

        mem_mb = get_private_ram_mb(target_proc)
        if mem_mb and mem_mb > DEFAULT_RAM_LIMIT:
            print(f"\n[{time.strftime('%H:%M:%S')}] EqMaxのRAMしきい値超過({mem_mb:.1f}MB)：再起動")
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

    print(f"\n [Step 1/7] Booting EqMax Discord Bridge....... [  OK  ]")
    print(f"    └─ [System Version: v{CURRENT_VERSION}]")

    print(f" [Step 2/7] Checking for updates...")
    status, ver, url = check_for_updates()
    if status == "UPDATE_AVAILABLE":
        print(f"    └─ [Notice] 【重要】新バージョン {ver} が公開されています。")
        webbrowser.open(url)
        is_update_found = True
    elif status == "LATEST":
        print(f"    └─ [Notice] バージョン {ver} は最新です。  [  OK  ]")
    else:
        print(f"    └─ [Warning] アップデート確認をスキップしました。 [  NG  ]")

    print(f" [Step 3/7] Update Sequence Check.............. [  OK  ]")
    print(f" [Step 4/7] Guardian System Health Check....... [  OK  ]")
    print(f" [Step 5/7] Guardian Core Engine Initialized... [  OK  ]")
    print(f"    └─ [RAM LIMIT {DEFAULT_RAM_LIMIT}MB , ReportEvery {DEFAULT_REPORT_INT}Seconds]")

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

    print(f"\n" + "="*52)
    if not is_all_ok:
        print(f"    SYSTEM STATUS: ATTENTION REQUIRED / CHECK LOGS")
        print(f"    [Error] 設定や環境に致命的な問題があるため、開始できません。")
        input("\n    Enterキーを押すと終了します...")
        sys.exit(1)
    
    print(f"    SYSTEM STATUS: ALL GREEN / READY TO MONITOR")
    print(f"    WELCOME TO EQMAX DISCORD BRIDGE V{CURRENT_VERSION}")
    print(f"    Developed by Mustang_TIS")
    print(f"="*52 + "\n")

    exe_path = config["exe_path"]
    log_file = os.path.join(config["eqmax_dir"], "Twitter.log")

    if os.path.exists(log_file):
        last_size = os.path.getsize(log_file)
    else:
        last_size = 0
        with open(log_file, "a", encoding="utf-8") as f: pass

    pending_block = ""
    health_counter = 0
    last_checked_json = None 
    INT_ORDER = {"1": 1, "2": 2, "3": 3, "4": 4, "5弱": 5, "5強": 6, "6弱": 7, "6強": 8, "7": 9}

    print(f"監視開始: {log_file}")
    print(f"初期サイズ: {last_size} bytes")

    while True:
        try:
            # --- ここを追加：ループのたびに設定を再読み込みする ---
            config = load_config() 

            # --- 1. 死活監視・メモリ管理 ---
            if health_counter % 10 == 0:
                maintain_eqmax_health(exe_path)

            # --- 2. 確定報(JSON) 監視ロジック ---
            # ここで最新の config から値を取得するようになる
            min_trigger = config.get("min_trigger_int", "3")
            min_display = config.get("min_display_int", "1")
            now = datetime.datetime.now()
            json_base_dir = os.path.join(config["eqmax_dir"], "Json", now.strftime("%Y"), now.strftime("%m"))
            
            if os.path.exists(json_base_dir):
                # ファイル名に特定のコードを指定せず、すべてのJSONファイルを対象にする
                json_files = sorted([f for f in os.listdir(json_base_dir) if f.endswith(".json")])
                if json_files:
                    latest_json = json_files[-1]
                    if latest_json != last_checked_json:
                        if last_checked_json is not None:
                            json_path = os.path.join(json_base_dir, latest_json)
                            try:
                                with open(json_path, "r", encoding="utf-8-sig") as f:
                                    data = json.load(f)
                                    title = data.get("Control", {}).get("Title", "")
                                max_int = data.get("Body", {}).get("Intensity", {}).get("Observation", {}).get("MaxInt", "0")

                                current_int_val = INT_ORDER.get(str(max_int), 0)
                                trigger_int_val = INT_ORDER.get(str(min_trigger), 0)

                                if "津波" in title or current_int_val >= trigger_int_val:
                                    formatted_text = fixed_report_parser.parse_fixed_report(data, min_display)
                                    if len(formatted_text) > 1900:
                                        formatted_text = formatted_text[:1900] + "\n\n...（省略）"
                                    
                                    timestamp = time.strftime('%H:%M:%S')
                                    print(f"\n--- 確定報検知 (JSON) ---\n{formatted_text}\n-----------------------")

                                    for dest in config["destinations"]:
                                        # タイトルを判定：津波の文字があれば津波、なければ震度
                                        display_title = "【津波情報】" if "津波" in title else f"【地震情報】最大震度 {max_int}"

                                        senders.dispatch(
                                            style=dest.get("style", "disembed").lower(),
                                            title=display_title,  # ← 変数に差し替え
                                            description=formatted_text,
                                            color=0x00FFFF if "津波" in title else 0xFFD700, # 津波なら水色、地震なら金/黄色
                                            image_path=None,
                                            url=dest.get("url"),
                                            bot_name="EqMax Report Bridge",
                                            current_version=CURRENT_VERSION,
                                            timestamp=timestamp,
                                            matrix_token=dest.get("token"), 
                                            matrix_room=dest.get("room")
                                        )
                                    print(f"[{timestamp}] 📝 確定報を送信しました: {latest_json}")
                                else:
                                    print(f"[{time.strftime('%H:%M:%S')}] 確定報通知スキップ: 最大震度 {max_int}")
                            except Exception as e:
                                print(f"[{time.strftime('%H:%M:%S')}] [Error] JSON解析失敗: {e}")
                        last_checked_json = latest_json

            # --- 3. 速報(Twitter.log) 監視ロジック ---
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size < last_size: last_size = 0 # ローテーション対応

                if current_size > last_size:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_size)
                        new_data = f.read()
                        if new_data:
                            for line in new_data.splitlines():
                                raw_line = line.strip()
                                if not raw_line: continue

                                # ブロック開始判定
                                if "緊急地震速報：" in raw_line or "[Twitter] Post Success:" in raw_line:
                                    pending_block = raw_line + "\n"
                                # ブロック蓄積中
                                elif pending_block:
                                    if raw_line == ":": continue
                                    pending_block += raw_line + "\n"
                                    # 送信トリガー (画像パス判定)
                                    low_line = raw_line.lower()
                                    if ".png" in low_line and "capture" in low_line:
                                        time.sleep(0.5)
                                        process_log_update(pending_block, config["destinations"], CURRENT_VERSION)
                                        pending_block = ""
                    last_size = current_size
                else:
                    if health_counter % 10 == 0:
                        print(".", end="", flush=True)
            else:
                if health_counter % 60 == 0:
                    print(f"\n[ERROR] ファイルが見つかりません: {log_file}")

            # --- 4. 定期ステータスレポート ---
            if health_counter % DEFAULT_REPORT_INT == 0:
                mem_display = "停止中"
                for proc in psutil.process_iter(['name']):
                    if proc.info.get('name') == "EqMax.exe":
                        val = get_private_ram_mb(proc)
                        mem_display = f"{val:.1f}" if val is not None else "取得失敗"
                        break
                print(f"\n[{time.strftime('%H:%M:%S')}] EqMax正常稼働中 (RAM使用量: {mem_display} MB)")

            health_counter += 1
            time.sleep(1) 

        except Exception as e:
            print(f"\n[Loop Error] {e}")
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
        input("\nEnterキーを押して終了...")