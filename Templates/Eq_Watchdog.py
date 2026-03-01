import os
import time
import psutil
import json
import ctypes
import sys

# --- タスクバーアイコン修正用の呪文 ---
def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = u'mycompany.eqmax.guardian.v4' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

set_taskbar_icon()

# --- 設定の読み込み (ここを少しだけ強化) ---
def load_config():
    config = {
        "eqmax_dir": "C:\\EqMax_Win64",
        "ram_limit_mb": 1024,          # デフォルト: 1GB
        "report_interval_sec": 3600    # デフォルト: 1時間
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception: pass
    return config

# --- 健康診断ロジック (ram_limit を受け取るように追加) ---
def maintain_eqmax_health(exe_path, check_full=False, ram_limit=1024):
    process_name = "EqMax.exe"
    target_proc = None

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                target_proc = proc
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied): continue

    if target_proc is None:
        print(f"[{time.strftime('%H:%M:%S')}] EqMax停止検知：再起動します。")
        os.startfile(exe_path)
        return

    if check_full:
        try:
            if not target_proc.is_running() or target_proc.status() == psutil.STATUS_ZOMBIE:
                print(f"[{time.strftime('%H:%M:%S')}] EqMaxハングアップ検知：強制再起動。")
                target_proc.kill()
                time.sleep(2)
                os.startfile(exe_path)
                return

            # JSONから読み込んだ ram_limit で判定
            mem_mb = target_proc.memory_info().rss / (1024 * 1024)
            if mem_mb > ram_limit:
                print(f"[{time.strftime('%H:%M:%S')}] メモリ超過({mem_mb:.1f}MB / Limit: {ram_limit}MB)：再起動。")
                target_proc.kill()
                time.sleep(2)
                os.startfile(exe_path)
        except Exception: pass

# --- メインループ ---
def start_watchdog():
    config = load_config()
    exe_path = os.path.normpath(os.path.join(config["eqmax_dir"], "EqMax.exe"))
    
    # JSONから設定を取得
    ram_limit = config.get("ram_limit_mb", 1024)
    report_int = config.get("report_interval_sec", 3600)
    
    if not os.path.exists(exe_path):
        print(f"エラー: {exe_path} が見つかりません。")
        return

    print(f"[{time.strftime('%H:%M:%S')}] EqMax Watchdog Started.")
    print(f"Monitoring: {exe_path} (Limit: {ram_limit}MB)")
    print("-" * 50)

    health_counter = 0
    process_name = "EqMax.exe"

    while True:
        try:
            # 生存確認ログ (JSONの設定値を使用)
            if health_counter % report_int == 0:
                mem_mb = "不明"
                for proc in psutil.process_iter(['name', 'memory_info']):
                    if proc.info.get('name') == process_name:
                        mem_mb = f"{proc.info['memory_info'].rss / (1024 * 1024):.1f}"
                        break
                print(f"[{time.strftime('%H:%M:%S')}] Watchdog Alive | EqMax RAM: {mem_mb} MB")
                if health_counter == 0: health_counter = 1

            # 死活監視 (ram_limit を渡す)
            if health_counter % 10 == 0:
                maintain_eqmax_health(exe_path, check_full=True, ram_limit=ram_limit)

            health_counter += 1
            if health_counter > 86400: health_counter = 1

        except KeyboardInterrupt:
            print("\nユーザーにより停止されました。")
            break
        except Exception as e:
            print(f"エラー: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    set_taskbar_icon()
    start_watchdog()