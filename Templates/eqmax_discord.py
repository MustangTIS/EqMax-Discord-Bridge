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
import eq_guardian_core as core  # これを追加
import config_manager
from log_monitor import LogMonitor

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "11.0.0"
DEFAULT_RAM_LIMIT = 1024
DEFAULT_REPORT_INT = 3600
REPO_URL = "MustangTIS/EqMax-Discord-Bridge"
RELEASE_PAGE_URL = f"https://github.com/{REPO_URL}/releases/latest"

# 確定報JSONの表記ゆれ（5-, 5+等）に対応した重み付け辞書
INT_ORDER = {
    "1": 1, "2": 2, "3": 3, "4": 4, 
    "5弱": 5, "5-": 5, 
    "5強": 6, "5+": 6, 
    "6弱": 7, "6-": 7, 
    "6強": 8, "6+": 8, 
    "7": 9
}

def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = f'mycompany.eqmax.guardian.v{CURRENT_VERSION}' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

set_taskbar_icon()

# --- 1. アップデートチェック ---
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

# --- 2. 設定読み込み & 環境チェック ---
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

# --- 3. 速報処理（メイン側） ---
def process_log_update(content, config_dest, current_version):
    print(f"\n--- 速報検知 (Log) ---\n{content.strip()}\n---------------------")

    title, description, color, image_path = eew_parser.parse_log_content(content)
    if not title: return

    timestamp = time.strftime('%H:%M:%S')
    bot_name = "EqMax EEW Bridge"
    shared_image_url = None

    # 各送信先へループ
    for dest in config_dest:
        url = dest.get("url")
        style = dest.get("style", "disembed").lower()
        # Blueskyの場合はURLがなくても進行させる（ハンドルとパスワードがあれば良いため）
        if not url and style not in ["bluesky"]: continue

        # senders.dispatch に Bluesky 用の引数を追加
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
            shared_image_url=shared_image_url,
            bsky_handle=dest.get("bsky_handle"),      # ★追加
            bsky_pass=dest.get("bsky_password")      # ★追加
        )

        # --- 画像URLの抽出ロジック（Discord送信成功時にURLを保存） ---
        if style in ["disembed", "dissimple"] and response and hasattr(response, 'status_code') and response.status_code in [200, 204]:
            try:
                if not shared_image_url:
                    data = response.json()
                    if "attachments" in data and len(data["attachments"]) > 0:
                        shared_image_url = data["attachments"][0].get("url")
                    elif "embeds" in data and len(data["embeds"]) > 0 and "image" in data["embeds"][0]:
                        shared_image_url = data["embeds"][0]["image"].get("url")
            except:
                pass

        # 結果判定の表示
        if isinstance(response, Exception):
            print(f"[{timestamp}]  └─ [Error] 送信失敗: {response}")
        elif response and hasattr(response, 'status_code') and response.status_code in [200, 201, 204]: # Blueskyの201も成功に含める
            print(f"[{timestamp}]  └─ [Success] 送信完了 ({style})")
        else:
            print(f"[{timestamp}]  └─ [Failed] 送信失敗 ({style})")

# --- 4. 確定情報の処理 ---
def check_and_process_json(config, last_checked_json):
    now = datetime.datetime.now()
    json_base_dir = os.path.join(config["eqmax_dir"], "Json", now.strftime("%Y"), now.strftime("%m"))

    if not os.path.exists(json_base_dir):
        return last_checked_json

    json_files = sorted([f for f in os.listdir(json_base_dir) if f.endswith(".json")])
    if not json_files:
        return last_checked_json

    latest_json = json_files[-1]
    if latest_json == last_checked_json:
        return last_checked_json

    # 初回起動時は通知せず、2回目（新しいファイルが生成された時）から処理
    if last_checked_json is not None:
        json_path = os.path.join(json_base_dir, latest_json)
        try:
            with open(json_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                title = data.get("Control", {}).get("Title", "")
                h_title = data.get("Head", {}).get("Title", "")
                max_int = data.get("Body", {}).get("Intensity", {}).get("Observation", {}).get("MaxInt", "0")
                current_int_val = INT_ORDER.get(str(max_int), 0)
                trigger_int_val = INT_ORDER.get(str(config.get("min_trigger_int", "3")), 0)
                is_special = any(x in title or x in h_title for x in ["津波", "遠地地震"])

                if is_special or current_int_val >= trigger_int_val:
                    formatted_text = fixed_report_parser.parse_fixed_report(data, config.get("min_display_int", "1"))
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"\n--- 確定報検知 (JSON) ---\n{formatted_text[:500]}...\n-----------------------")

                    for dest in config["destinations"]:
                        style = dest.get("style", "disembed").lower()
                        limit = 4000 if style == "disembed" else 1900
                        # Blueskyの文字数制限(300)に配慮したカットはsenders.py側で行うため、ここではそのまま渡す
                        current_formatted_text = formatted_text[:limit] + "\n\n...（省略）" if len(formatted_text) > limit else formatted_text

                        senders.dispatch(
                            style=style, 
                            title="【津波情報】" if "津波" in title else f"【地震情報】最大震度 {max_int}",
                            description=current_formatted_text, 
                            color=0x00FFFF if "津波" in title else 0xFFD700,
                            image_path=None,
                            url=dest.get("url"), 
                            bot_name="EqMax Report Bridge",
                            current_version=CURRENT_VERSION, 
                            timestamp=timestamp,
                            matrix_token=dest.get("token"), 
                            matrix_room=dest.get("room"),
                            bsky_handle=dest.get("bsky_handle"),    # ★追加
                            bsky_pass=dest.get("bsky_password")     # ★追加
                        )

                    print(f"[{timestamp}] 📝 確定報を送信しました: {latest_json}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] 確定報通知スキップ: {title} (最大震度 {max_int})")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] [Error] JSON解析失敗: {e}")
    return latest_json

# --- 5. 定期レポート処理 ---
def output_periodic_report(health_counter, report_interval):
    if health_counter % report_interval != 0:
        return

    mem_display = "停止中"
    for proc in psutil.process_iter(['name']):
        if proc.info.get('name') == "EqMax.exe":
            val = core.get_private_ram_mb(proc)
            mem_display = f"{val:.1f}" if val is not None else "取得失敗"
            break
    print(f"\n[{time.strftime('%H:%M:%S')}] EqMax正常稼働中 (RAM使用量: {mem_display} MB)")
    
# --- 6. メインループ ---
def start_combined_monitor():
    print("-" * 52)
    print(f">>> EqMax Discord Bridge: Initialization...")
    print(f">>> EqMax Discord Bridge: Boot Sequence Started...")
    print("-" * 52)

    is_all_ok = True  
    is_update_found = False
    config = config_manager.load_system_config()
    
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
    
    ram_val = config.get("ram_limit", DEFAULT_RAM_LIMIT)
    rep_val = config.get("report_interval_sec", DEFAULT_REPORT_INT)

    print(f" [Step 5/7] Guardian Core Engine Initialized... [  OK  ]")
    print(f"    └─ [RAM LIMIT {ram_val}MB , ReportEvery {rep_val}Seconds]")

    # Step 6/7: config_managerが判定した is_env_ok を使う
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

    # --- 監視の準備 (整理後) ---
    # 設定を最新状態で読み込み
    log_path = os.path.join(config["eqmax_dir"], "Twitter.log")

    if not os.path.exists(log_path):
        with open(log_path, "a", encoding="utf-8") as f: pass

    monitor = LogMonitor(log_path)
    last_checked_json = None
    health_counter = 0

    print(f"監視開始: {log_path}")
    print(f"初期サイズ: {monitor.last_size} bytes")

    health_counter = 0
    while True:
        try:
            # 1. 監視（コア機能：死活監視 & JSON監視）
            core.maintain_eqmax_health(config["exe_path"], config.get("ram_limit", 1024))
            last_checked_json = check_and_process_json(config, last_checked_json)
            
            # 2. ログ監視（EEW）
            new_blocks = monitor.check_new_logs()
            if new_blocks:
                for block in new_blocks:
                    process_log_update(block, config["destinations"], CURRENT_VERSION)
            elif health_counter % 10 == 0:
                print(".", end="", flush=True)

            # 3. 定期ステータスレポート
            # configからインターバルを取得するか、デフォルト値を使用
            report_int = config.get("report_interval_sec", DEFAULT_REPORT_INT)
            output_periodic_report(health_counter, report_int)

            health_counter += 1
            time.sleep(1)

        except Exception as e:
            print(f"\n[Loop Error] {e}")
            time.sleep(1)
        
# 行頭の余計なスペースを消して左端に合わせる
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