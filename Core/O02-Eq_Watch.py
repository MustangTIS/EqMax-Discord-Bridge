#O02-Eq_Watch.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import json
from datetime import datetime
import subprocess
import winreg  # レジストリ参照用

# 画像処理ライブラリの読み込み
try:
    from PIL import Image
except ImportError:
    Image = None

class EqWatchdogDeployer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. パス・アセット設定 ---
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        # ウィンドウ基本設定
        self.title("EqMax 動作監視(Watchdog) 配置ツール")
        self.geometry("620x920") 
        ctk.set_appearance_mode("dark")

        # アイコン設定
        if os.path.exists(icon_path):
            try: self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(light_image=opened_img, dark_image=opened_img, size=(45, 45))
            except: pass

        # --- 2. 画面レイアウト ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax 安定化監視配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 28, "bold") 
        )
        self.label_title.pack(pady=(20, 15))

        # 1. EqMax.exe 選択
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe 本体を選択してください:", font=("Yu Gothic", 15, "bold"))
        self.label_path.pack(pady=(15, 0))
        
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=10)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=400, font=("Yu Gothic", 14), placeholder_text="「選択...」から選んでください")
        self.entry_path.pack(side="left", padx=5)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=90, font=("Yu Gothic", 13, "bold"), command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 2. 監視パラメーター設定
        self.param_frame = ctk.CTkFrame(self)
        self.param_frame.pack(pady=15, padx=40, fill="x")
        ctk.CTkLabel(self.param_frame, text="2. 監視パラメーター設定:", font=("Yu Gothic", 15, "bold")).pack(pady=(15, 5), padx=20, anchor="w")

        # RAM上限
        ram_f = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        ram_f.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(ram_f, text="再起動閾値 (MB):", font=("Yu Gothic", 14)).pack(side="left")
        self.entry_ram = ctk.CTkEntry(ram_f, width=100, font=("Consolas", 15, "bold")); self.entry_ram.insert(0, "1024"); self.entry_ram.pack(side="left", padx=15)
        
        ctk.CTkLabel(self.param_frame, text="【推奨】1000MB以上", font=("Yu Gothic", 12), text_color="#AAAAAA").pack(padx=30, anchor="w", pady=(0, 10))

        # 報告間隔
        int_f = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        int_f.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(int_f, text="生存報告間隔 (秒):", font=("Yu Gothic", 14)).pack(side="left")
        self.entry_int = ctk.CTkEntry(int_f, width=100, font=("Consolas", 15, "bold")); self.entry_int.insert(0, "3600"); self.entry_int.pack(side="left", padx=15)

        # 3. ショートカットオプション
        self.option_frame = ctk.CTkFrame(self)
        self.option_frame.pack(pady=10, padx=40, fill="x")
        self.var_desktop = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="デスクトップにショートカットを作成（通常＆セーフ）", variable=self.var_desktop, font=("Yu Gothic", 14)).pack(pady=12, padx=30, anchor="w")
        self.var_startup = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="スタートアップに登録（自動起動）", variable=self.var_startup, font=("Yu Gothic", 14)).pack(pady=12, padx=30, anchor="w")

        # 実行ボタン
        self.btn_run = ctk.CTkButton(self, text="監視ボットを配置・設定保存", fg_color="#1f538d", height=65, font=("Yu Gothic", 16, "bold"), command=self.run_deploy)
        self.btn_run.pack(pady=20)

        # ログ
        self.log_view = ctk.CTkTextbox(self, width=540, height=120, font=("Consolas", 11)); self.log_view.pack(pady=10)

    def browse_file(self):
        p = filedialog.askopenfilename(title="EqMax.exeを選択", filetypes=[("EqMax本体", "EqMax.exe"), ("すべて", "*.*")])
        if p:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.normpath(p))

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n"); self.log_view.see("end")

    def create_shortcut(self, watch_dir, link_path):
        """通常版：Pythonを直接起動しEqMaxのアイコンを適用する"""
        py_script = os.path.join(watch_dir, "Eq_Watchdog.py")
        exe_icon = self.entry_path.get().strip()
        ps_cmd = (
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{os.path.normpath(link_path)}'); "
            f"$s.TargetPath = 'python.exe'; "
            f"$s.Arguments = '\"{os.path.normpath(py_script)}\"'; "
            f"$s.WorkingDirectory = '{os.path.normpath(watch_dir)}'; "
            f"$s.IconLocation = '{os.path.normpath(exe_icon)},0'; "
            f"$s.WindowStyle = 7; $s.Save()"
        )
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
            return True
        except: return False

    def create_safe_shortcut(self, watch_dir, link_path):
        """セーフモード版：バッチファイルを直接起動し、環境チェックを通す"""
        target_bat = os.path.join(watch_dir, "Eq_Watchdog.bat")
        ps_cmd = (
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{os.path.normpath(link_path)}'); "
            f"$s.TargetPath = '{os.path.normpath(target_bat)}'; "
            f"$s.WorkingDirectory = '{os.path.normpath(watch_dir)}'; "
            f"$s.WindowStyle = 1; $s.Save()"
        )
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
            return True
        except: return False

    def run_deploy(self):
        exe_path = self.entry_path.get().strip()
        if not exe_path or not os.path.isfile(exe_path):
            messagebox.showerror("エラー", "EqMax.exeを選択してください。"); return

        eqmax_dir = os.path.dirname(exe_path)
        watch_dir = os.path.join(eqmax_dir, "Watchdog")
        
        try:
            os.makedirs(watch_dir, exist_ok=True)
            base_dir = os.path.dirname(os.path.dirname(__file__))
            
            for f in ["Eq_Watchdog.py", "eq_guardian_core.py", "config_manager.py", "Eq_Watchdog.bat"]:
                src = os.path.join(base_dir, "Templates", f)
                if os.path.exists(src):
                    shutil.copy2(src, watch_dir)
            
            with open(os.path.join(watch_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "eqmax_dir": eqmax_dir, 
                    "ram_limit": int(self.entry_ram.get()), # _mbを取って ram_limit に
                    "report_interval_sec": int(self.entry_int.get())
                }, f, indent=4)

            # ショートカット作成
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                desk_path, _ = winreg.QueryValueEx(key, "Desktop")
                winreg.CloseKey(key)
            except:
                desk_path = os.path.join(os.path.expanduser("~"), "Desktop")

            if self.var_desktop.get() and desk_path:
                # 通常版
                self.create_shortcut(watch_dir, os.path.join(desk_path, "EqMax-Watchdog.lnk"))
                # セーフモード版
                self.create_safe_shortcut(watch_dir, os.path.join(desk_path, "EqMax-Watchdog(セーフモード).lnk"))
                self.write_log("デスクトップにショートカットを作成しました。")

            if self.var_startup.get():
                appdata = os.environ.get("APPDATA")
                if appdata:
                    start_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", "EqMax-Watchdog.lnk")
                    self.create_shortcut(watch_dir, start_path)

            self.write_log("すべてのプロセスが完了しました。")
            messagebox.showinfo("完了", "配置完了！\n動かない時はセーフモードを試してください。")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", str(e))

if __name__ == "__main__":
    EqWatchdogDeployer().mainloop()