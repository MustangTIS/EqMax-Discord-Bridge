#eq_guardian_core.py
import ctypes
import psutil
import subprocess
import time
import os
import sys

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

# --- 3. 死活監視 ---
def maintain_eqmax_health(exe_path, ram_limit=1024):
    target_proc = None
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == "EqMax.exe":
                target_proc = proc
                break
        except: continue

    # A. プロセスがいない場合
    if target_proc is None:
        if os.path.exists(exe_path):
            print(f"\n[{time.strftime('%H:%M:%S')}] プロセスにEqMaxが見つかりません：最小化で起動")
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 6 
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), startupinfo=si)
        return # 起動したので終了

    # B. プロセスがいる場合（ここから下は else の中に入れるか、上記のように return する）
    if not is_window_responding(target_proc.pid):
        print(f"\n[{time.strftime('%H:%M:%S')}] EqMaxがフリーズしています：再起動")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            return
        except: pass

    mem_mb = get_private_ram_mb(target_proc)
    if mem_mb and mem_mb > ram_limit:
        print(f"\n[{time.strftime('%H:%M:%S')}] EqMaxのRAMしきい値超過({mem_mb:.1f}MB / 制限:{ram_limit}MB)：再起動")
        try:
            target_proc.kill(); time.sleep(3); os.startfile(exe_path)
        except: pass