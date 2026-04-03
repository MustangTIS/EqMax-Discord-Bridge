# Eq_Watchdog.py (v10.2.0 - Core Linked Edition)
import os
import time
import sys
import ctypes
import eq_guardian_core as core
import config_manager

CURRENT_VERSION = "10.2.0"

def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = f'mycompany.eqmax.watchdog.v{CURRENT_VERSION}'
        try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

def start_watchdog():
    set_taskbar_icon()
    print("="*52)
    print(f"    EqMax Watchdog System - [Standalone Mode]")
    print(f"    System Version: v{CURRENT_VERSION}")
    print("="*52)

    # 設定の読み込み
    config = config_manager.load_system_config()
    report_interval = config.get("report_interval_sec", 3600)
    ram_limit = config.get("ram_limit", 1024)

    print(f"\n [Step 1/3] Loading Configuration...")
    print(f"    ├─ Target   : {config['exe_path']}")
    print(f"    ├─ RAM Limit: {ram_limit} MB") 
    print(f"    └─ Interval : {report_interval} sec")

    print(f" [Step 2/3] Linking Guardian Core Engine...")
    print(f"    └─ Core Logic Ready. [ OK ]")

    print(f" [Step 3/3] System Standby.")
    print(f"\n" + "-"*52)
    print(f"  WATCHDOG STATUS: ACTIVE / MONITORING")
    print(f"  (Configured: {ram_limit}MB Limit / {report_interval}s Report)")
    print(f"  Press Ctrl+C to stop.")
    print("-"*52 + "\n")

    # --- 監視ループ ---
    health_counter = 0
    while True:
        try:
            # 死活監視・メモリチェックを実行
            core.maintain_eqmax_health(config["exe_path"], ram_limit=ram_limit)

            # 設定された間隔（秒）ごとに報告を出す
            if health_counter % report_interval == 0:
                import psutil
                current_ram = 0
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == "EqMax.exe":
                        try:
                            current_ram = proc.memory_full_info().private / (1024 * 1024)
                        except:
                            current_ram = proc.memory_info().rss / (1024 * 1024)
                        break

                ram_status = f"{current_ram:.1f} MB" if current_ram > 0 else "Not Running"
                print(f"[{time.strftime('%H:%M:%S')}] 🐾 Watchdog: システム稼働中 (RAM使用量: {ram_status} / Limit: {ram_limit} MB)")

            health_counter += 1
            time.sleep(1)

        # ★ここから下が抜けていたため、SyntaxErrorになっていました
        except KeyboardInterrupt:
            print("\n[Terminated] Watchdog 終了します。")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_watchdog()