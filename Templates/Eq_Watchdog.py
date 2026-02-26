import os
import time
import psutil
import json
import ctypes
import sys

# --- タスクバーアイコン修正用の呪文 ---
def set_taskbar_icon():
    if sys.platform == "win32":
        # 独自のAppIDを設定することで、cmd.exeとは別のアプリとして認識させる
        myappid = u'mycompany.eqmax.guardian.v4' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

set_taskbar_icon()
# --- 設定の読み込み ---
def load_config():
    config = {"eqmax_dir": "C:\\EqMax_Win64"}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception: pass
    return config

def maintain_eqmax_health(exe_path, check_full=False):
    process_name = "EqMax.exe"
    target_proc = None

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                target_proc = proc
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 1. プロセス不在時の自動起動
    if target_proc is None:
        print(f"[{time.strftime('%H:%M:%S')}] EqMax停止検知：再起動します。")
        os.startfile(exe_path)
        return

    # 2. 精密検査 (フリーズ・メモリチェック)
    if check_full:
        try:
            # 応答チェック
            if not target_proc.is_running() or target_proc.status() == psutil.STATUS_ZOMBIE:
                print(f"[{time.strftime('%H:%M:%S')}] EqMaxハングアップ検知：強制再起動。")
                target_proc.kill()
                time.sleep(2)
                os.startfile(exe_path)
                return

            # メモリリーク対策 (1GB超過でリセット)
            mem_mb = target_proc.memory_info().rss / (1024 * 1024)
            if mem_mb > 1024:
                print(f"[{time.strftime('%H:%M:%S')}] メモリ超過({mem_mb:.1f}MB)：リフレッシュ起動。")
                target_proc.kill()
                time.sleep(2)
                os.startfile(exe_path)
        except Exception: pass

if __name__ == "__main__":
    config = load_config()
    eqmax_exe = os.path.join(config["eqmax_dir"], "EqMax.exe")
    print(f"EqMax Watchdog 稼働中... (監視対象: {eqmax_exe})")
    
    counter = 0
    while True:
        counter += 1
        # 10秒に1回精密検査、それ以外は存在確認のみ
        maintain_eqmax_health(eqmax_exe, check_full=(counter >= 10))
        if counter >= 10: counter = 0
        time.sleep(1)