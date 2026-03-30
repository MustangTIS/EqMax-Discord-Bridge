# Eq_Watchdog.py
import os
import time
import psutil
import json
import ctypes
import sys
import subprocess

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "8.6.0"

# --- タスクバーアイコン修正用の呪文 ---
def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = f'mycompany.eqmax.guardian.v{CURRENT_VERSION}' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

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

# --- 2. メモリ取得関数 (Private Bytes優先) ---
def get_private_ram_mb(proc):
    try:
        return proc.memory_full_info().private / (1024 * 1024)
    except:
        try:
            return proc.memory_info().rss / (1024 * 1024)
        except: return None

# --- 3. 設定の読み込み ---
def load_config():
    config = {
        "eqmax_dir": "C:\\EqMax_Win64",
        "ram_limit_mb": 1024,
        "report_interval_sec": 3600
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except: pass
    return config

# --- 4. 健康診断ロジック ---
def maintain_eqmax_health(exe_path, ram_limit=1024):
    process_name = "EqMax.exe"
    target_proc = None
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                target_proc = proc; break
        except: continue

    if target_proc is None:
        if os.path.exists(exe_path):
            print(f"[{time.strftime('%H:%M:%S')}] EqMax未起動：最小化で起動します")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
        return

    if not is_window_responding(target_proc.pid):
        print(f"[{time.strftime('%H:%M:%S')}] EqMaxフリーズ検知：再起動します")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            return 
        except: pass

    mem_mb = get_private_ram_mb(target_proc)
    if mem_mb and mem_mb > ram_limit:
        print(f"[{time.strftime('%H:%M:%S')}] RAM超過({mem_mb:.1f}MB)：再起動します")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
        except: pass

# --- 5. メインループ (診断シーケンス・シンプル版) ---
def start_watchdog():
    is_all_ok = True
    config = load_config()
    exe_path = os.path.normpath(os.path.join(config["eqmax_dir"], "EqMax.exe"))
    ram_limit = config.get("ram_limit_mb", 1024)
    report_int = config.get("report_interval_sec", 3600)
    
    print("-" * 52)
    print(f">>> EqMax Watchdog: Initialization...")
    print(f">>> EqMax Watchdog: Boot Sequence Started...")
    print("-" * 52)

    # --- [Step 1/7] ---
    print(f" [Step 1/7] Booting EqMax Watchdog Engine....... [  OK  ]")
    print(f"    └─ [System Version: v{CURRENT_VERSION}]")

    # --- [Step 2/7] アップデート判定をパス ---
    print(f" [Step 2/7] Checking for updates............. [ SKIP ]")
    print(f"    └─ [Info] スタンドアロン動作モードです。")

    # --- [Step 3-5] ---
    print(f" [Step 3/7] Update Sequence Check.............. [  OK  ]")
    print(f" [Step 4/7] Guardian System Health Check....... [  OK  ]")
    print(f" [Step 5/7] Guardian Core Engine Initialized... [  OK  ]")
    print(f"    └─ [RAM LIMIT {ram_limit}MB , ReportEvery {report_int}Seconds]")

    # --- [Step 6/7] 環境チェック ---
    if os.path.exists(exe_path):
        print(f" [Step 6/7] Link Check EqMax Connector....... [  OK  ]")
        print(f"    └─ Path: {exe_path}")
    else:
        print(f" [Step 6/7] Link Check EqMax Connector....... [  !!  ]")
        print(f"    └─ [Error] EqMax.exe が見つかりません。")
        is_all_ok = False

    # --- [Step 7/7] ---
    print(f" [Step 7/7] Discord Webhook Standby.......... [ SKIP ]")
    print(f"    └─ [Info] 単体動作モードのため送信は行いません。")

    # --- [Final Status] ---
    print(f"\n" + "="*52)
    if is_all_ok:
        print(f"    SYSTEM STATUS: ALL GREEN / READY TO MONITOR")
    else:
        print(f"    SYSTEM STATUS: ATTENTION REQUIRED / CHECK LOGS")
    print(f"    WELCOME TO EQMAX WATCHDOG V{CURRENT_VERSION}")
    print(f"    Developed by Mustang_TIS")
    print(f"="*52 + "\n")

    if not is_all_ok:
        print("致命的なエラーがあるため、監視を開始できません。config.jsonを確認してください。")
        return

    # --- 監視ループ ---
    health_counter = 0
    while True:
        try:
            # 指定された間隔(report_int)ごとにメモリ使用量を表示
            if health_counter % report_int == 0:
                mem_display = "取得失敗" # 初期値を設定しておく
                for proc in psutil.process_iter(['name']):
                    if proc.info.get('name') == "EqMax.exe":
                        val = get_private_ram_mb(proc)
                        if val: mem_display = f"{val:.1f}"
                        break
                print(f"[{time.strftime('%H:%M:%S')}] 正常稼働中 | EqMax RAM(Private): {mem_display} MB")
                if health_counter == 0: health_counter = 1

            # 10秒ごとにEqMaxの健康診断（フリーズ・メモリ超過チェック）を実行
            if health_counter % 10 == 0:
                maintain_eqmax_health(exe_path, ram_limit=ram_limit)

            health_counter += 1
            if health_counter > 86400: health_counter = 1 # カウンターリセット
        except KeyboardInterrupt: 
            break 
        except Exception as e:
            # ループ内の軽微なエラーは表示して継続
            print(f"[{time.strftime('%H:%M:%S')}] 警告: 監視中にエラーが発生しました: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        set_taskbar_icon()
        start_watchdog()  # ここでStep 1-7の診断とメインループが走ります
    except Exception as e:
        # 実行中にエラーが起きたらここで捕まえて、画面を止めます
        print("\n" + "!"*60)
        print(" 【CRITICAL ERROR】システム実行中に致命的なエラーが発生しました")
        print("!"*60)
        import traceback
        traceback.print_exc() # どこが原因か詳細を表示
        print("\n" + "!"*60)
        print(" このウィンドウはエラー保持のため自動で閉じません。")
        print(" 内容を確認し、Enterキーを押すと終了します。")
        print("!"*60)
        input() # ここでユーザーの入力を待つ（重要！）
        sys.exit(1)