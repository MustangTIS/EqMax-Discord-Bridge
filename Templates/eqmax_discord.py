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

# --- [0. バージョン・固定設定] ---
CURRENT_VERSION = "5.5.3"
DEFAULT_RAM_LIMIT = 1024
DEFAULT_REPORT_INT = 3600
REPO_URL = "MustangTIS/EqMax-Discord-Bridge"
RELEASE_PAGE_URL = f"https://github.com/{REPO_URL}/releases/latest"

def set_taskbar_icon():
    if sys.platform == "win32":
        # f-stringでバージョンを自動反映
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

# --- 2. メモリ取得関数 (PowerShell版と一致するPrivate Bytes取得) ---
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
    print(f"[{time.strftime('%H:%M:%S')}] [Update] Checking for updates...")
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data.get("tag_name")
            current = f"v{CURRENT_VERSION}" if not CURRENT_VERSION.startswith("v") else CURRENT_VERSION
            if latest_tag and latest_tag != current:
                print(f"[{time.strftime('%H:%M:%S')}] [Update] 【重要】新バージョン {latest_tag} が公開されています。")
                webbrowser.open(data.get("html_url", RELEASE_PAGE_URL))
                time.sleep(2)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] [Update] バージョン {current} は最新です。")
    except: pass

# --- 4. 設定読み込み ---
def load_config():
    config = {"eqmax_dir": "C:/EqMax_Win64", "destinations": []}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except: pass
    config["eqmax_dir"] = os.path.normpath(config["eqmax_dir"])
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

# --- 6. Discord送信ロジック (v5.5.0風のログ出力へ改善) ---
def process_log_update(content, config_dest):
    pattern = re.compile(r"(緊急地震速報：.*?)(C:\\.*?\.png)", re.DOTALL)
    matches = pattern.findall(content)
    if not matches: return

    full_text, image_path = matches[-1]
    title, description, color = get_alert_details(full_text)
    if not title: return

    # 画像のイメージに合わせて1行で検知を出力
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] 📢 EEW検知: {title}")

    for dest in config_dest:
        url = dest.get("url")
        style = str(dest.get("style", "embed")).lower()
        if not url: continue
        
        if style == "simple":
            payload = {"content": f"📢 **{title}** / {description}".replace("\n", " / ").strip()}
        else:
            payload = {"embeds": [{"title": title, "description": description, "color": color,
                                   "image": {"url": "attachment://image.png"},
                                   "footer": {"text": f"EqMax Guardian v{CURRENT_VERSION}"}}]}
        try:
            path_to_img = image_path.strip()
            if os.path.exists(path_to_img):
                with open(path_to_img, "rb") as f:
                    response = requests.post(url, data={"payload_json": json.dumps(payload)}, 
                                  files={"file": ("image.png", f, "image/png")}, timeout=10)
            else:
                response = requests.post(url, json=payload, timeout=5)
            
            # v5.5.0のスタイルで送信結果を表示
            status = "Success" if response.status_code in [200, 204] else f"Failed({response.status_code})"
            print(f"[{timestamp}]  └─ [{status}] Discord送信完了 ({style})")
        except Exception as e:
            print(f"[{timestamp}]  └─ [Error] 送信エラー: {e}")

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
        # フリーズチェック
        if not is_window_responding(target_proc.pid):
            print(f"[{time.strftime('%H:%M:%S')}] EqMaxがフリーズしています：再起動")
            try:
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
                return 
            except: pass

        # メモリチェック (Private Bytes)
        mem_mb = get_private_ram_mb(target_proc)
        if mem_mb and mem_mb > DEFAULT_RAM_LIMIT:
            print(f"[{time.strftime('%H:%M:%S')}] EqMaxのRAMしきい値({DEFAULT_RAM_LIMIT}MB)を超過({mem_mb:.1f}MB)：再起動")
            try:
                target_proc.kill(); time.sleep(3); os.startfile(exe_path)
            except: pass

# --- 8. メインループ ---
def start_combined_monitor():
    check_for_updates()
    config = load_config()
    exe_path = os.path.join(config["eqmax_dir"], "EqMax.exe")
    log_file = os.path.join(config["eqmax_dir"], "Twitter.log")
    
    print(f"="*50 + f"\n Running...EqMax-Discord-Bridge v{CURRENT_VERSION}...\n" + f"="*50)

    last_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
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
                                    pending_block = "" # 処理完了後にリセット
                    last_size = current_size
            
            health_counter += 1
            if health_counter % DEFAULT_REPORT_INT == 0:
                mem_display = "停止中または見つかりません"
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
    start_combined_monitor()