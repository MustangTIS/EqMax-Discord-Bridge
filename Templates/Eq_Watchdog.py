import os
import time
import psutil
import json
import ctypes
import sys
import subprocess

# --- タスクバーアイコン修正用の呪文 ---
def set_taskbar_icon():
    if sys.platform == "win32":
        myappid = u'mycompany.eqmax.guardian.5.5.3' 
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

# --- 1. 応答なし監視 (フリーズ検知) の心臓部 ---
def is_window_responding(pid):
    """指定したPIDのメインウィンドウがフリーズしていないかWindows APIで確認"""
    try:
        def callback(hwnd, hwnds):
            _, found_pid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
            if found_pid == pid and ctypes.windll.user32.IsWindowVisible(hwnd):
                hwnds.append(hwnd)
            return True
        hwnds = []
        ctypes.windll.user32.EnumWindows(ctypes.WNDENUMPROC(callback), hwnds)
        
        for hwnd in hwnds:
            # 5秒(5000ms)反応がなければ 0 が返る
            result = ctypes.windll.user32.SendMessageTimeoutW(
                hwnd, 0, 0, 0, 0x0002, 5000, ctypes.byref(ctypes.c_ulong())
            )
            if result == 0: return False
        return True
    except: return True

# --- 2. メモリ取得関数 (Private値を優先) ---
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

# --- 4. 健康診断ロジック (応答チェック搭載版) ---
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
            print(f"[{time.strftime('%H:%M:%S')}] EqMaxが起動していません：最小化で起動します。")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
        return

    # [A] 応答チェック (フリーズ検知)
    if not is_window_responding(target_proc.pid):
        print(f"[{time.strftime('%H:%M:%S')}] EqMaxのフリーズ(応答なし)を検知：再起動します。")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            return 
        except: pass

    # [B] メモリ超過チェック
    mem_mb = get_private_ram_mb(target_proc)
    if mem_mb and mem_mb > ram_limit:
        print(f"[{time.strftime('%H:%M:%S')}] RAM容量超過({mem_mb:.1f}MB / Limit: {ram_limit}MB)：再起動。")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
        except: pass

# --- 5. メインループ ---
def start_watchdog():
    config = load_config()
    exe_path = os.path.normpath(os.path.join(config["eqmax_dir"], "EqMax.exe"))
    ram_limit = config.get("ram_limit_mb", 1024)
    report_int = config.get("report_interval_sec", 3600)
    
    if not os.path.exists(exe_path):
        print(f"エラー: {exe_path} が見つかりません。")
        return

    print(f"[{time.strftime('%H:%M:%S')}] EqMax Watchdog (Guardian Mode) 5.5.3 Started.")
    print(f"Monitoring: {exe_path} (Limit: {ram_limit}MB)")
    print("-" * 50)

    health_counter = 0
    while True:
        try:
            if health_counter % report_int == 0:
                mem_display = "プロセス一覧にEqMaxを見つけられません"
                for proc in psutil.process_iter(['name']):
                    if proc.info.get('name') == "EqMax.exe":
                        val = get_private_ram_mb(proc)
                        if val: mem_display = f"{val:.1f}"
                        break
                print(f"[{time.strftime('%H:%M:%S')}] 正常稼働中 | EqMax RAM(Private): {mem_display} MB")
                if health_counter == 0: health_counter = 1

            if health_counter % 10 == 0:
                maintain_eqmax_health(exe_path, ram_limit=ram_limit)

            health_counter += 1
            if health_counter > 86400: health_counter = 1
        except KeyboardInterrupt: break
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    set_taskbar_icon()
    start_watchdog()