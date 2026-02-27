# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import json
from datetime import datetime
import subprocess

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
        self.geometry("620x780")
        ctk.set_appearance_mode("dark")

        # アイコンの設定
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except:
                pass

        # ロゴ画像の読み込み
        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(
                    light_image=opened_img,
                    dark_image=opened_img,
                    size=(45, 45)
                )
            except:
                pass

        # --- 2. 画面レイアウト ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax 安定化監視配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # EqMax.exe 選択
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe 本体を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(15, 0))
        
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=10)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=400, placeholder_text="例: C:\\EqMax\\EqMax.exe")
        self.entry_path.pack(side="left", padx=5)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # オプション
        self.option_frame = ctk.CTkFrame(self)
        self.option_frame.pack(pady=10, padx=40, fill="x")
        
        self.label_opt = ctk.CTkLabel(self.option_frame, text="ショートカット作成オプション:", font=("Yu Gothic", 11, "bold"))
        self.label_opt.pack(pady=(10, 5), padx=20, anchor="w")

        self.var_desktop = ctk.BooleanVar(value=True)
        self.check_desktop = ctk.CTkCheckBox(self.option_frame, text="デスクトップにショートカットを作成", variable=self.var_desktop, font=("Yu Gothic", 11))
        self.check_desktop.pack(pady=10, padx=30, anchor="w")

        self.var_startup = ctk.BooleanVar(value=True)
        self.check_startup = ctk.CTkCheckBox(self.option_frame, text="スタートアップに登録（自動起動推奨）", variable=self.var_startup, font=("Yu Gothic", 11))
        self.check_startup.pack(pady=10, padx=30, anchor="w")

        # 実行ボタン
        self.btn_run = ctk.CTkButton(self, text="監視ボットを配置・設定保存", 
                                     fg_color="#1f538d", hover_color="#14375e", 
                                     height=60, font=("Yu Gothic", 14, "bold"),
                                     command=self.run_deploy)
        self.btn_run.pack(pady=20)

        # ログ表示
        self.log_view = ctk.CTkTextbox(self, width=540, height=150, font=("Consolas", 11))
        self.log_view.pack(pady=10)

    # --- 3. ロジック ---

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="EqMax.exeを選択してください",
            filetypes=[("EqMax本体", "EqMax.exe"), ("すべてのファイル", "*.*")]
        )
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, file_path)

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n")
        self.log_view.see("end")

    def create_shortcut(self, watch_dir, link_path):
        py_script = os.path.join(watch_dir, "Eq_Watchdog.py")
        exe_icon_path = self.entry_path.get().strip()

        p_script = os.path.abspath(py_script).replace("\\", "\\\\")
        l_path = os.path.abspath(link_path).replace("\\", "\\\\")
        i_path = os.path.abspath(exe_icon_path).replace("\\", "\\\\")
        w_dir = os.path.abspath(watch_dir).replace("\\", "\\\\")

        vbs_content = (
            f'Set oWS = CreateObject("WScript.Shell")\n'
            f'Set oLink = oWS.CreateShortcut("{l_path}")\n'
            f'oLink.TargetPath = "python.exe"\n'
            f'oLink.Arguments = "{p_script}"\n'
            f'oLink.WorkingDirectory = "{w_dir}"\n'
            f'oLink.IconLocation = "{i_path},0"\n' 
            f'oLink.WindowStyle = 7\n'
            f'oLink.Save'
        )
        temp_vbs = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "make_watchdog_lnk.vbs")
        try:
            with open(temp_vbs, "w", encoding="shift-jis") as f:
                f.write(vbs_content)
            subprocess.run(["cscript", "//nologo", temp_vbs], shell=True)
            if os.path.exists(temp_vbs): os.remove(temp_vbs)
            return True
        except Exception as e:
            self.write_log(f"作成エラー: {e}")
            return False

    def run_deploy(self):
        exe_path = self.entry_path.get().strip()
        if not exe_path or not os.path.isfile(exe_path):
            messagebox.showerror("エラー", "EqMax.exe を正しく選択してください。")
            return

        eqmax_dir = os.path.dirname(exe_path)
        watch_dir = os.path.join(eqmax_dir, "Watchdog")
        
        try:
            os.makedirs(watch_dir, exist_ok=True)
            base_dir = os.path.dirname(os.path.dirname(__file__))
            
            # 1. ファイルコピー
            for f in ["Eq_Watchdog.py", "Eq_Watchdog.bat"]:
                src = os.path.join(base_dir, "Templates", f)
                if os.path.exists(src):
                    shutil.copy2(src, watch_dir)
                    self.write_log(f"{f} をコピーしました。")

            # 2. 設定保存
            with open(os.path.join(watch_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump({"eqmax_dir": eqmax_dir}, f, indent=4)
            self.write_log("config.json を保存しました。")

            # 3. ショートカット作成
            lnk_name = "EqMax-Watchdog.lnk"
            
            # 安全なデスクトップパスの取得
            desk_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            if self.var_desktop.get():
                target_lnk = os.path.join(desk_path, lnk_name)
                if self.create_shortcut(watch_dir, target_lnk):
                    self.write_log("デスクトップにショートカットを作成しました。")

            if self.var_startup.get():
                appdata = os.environ.get("APPDATA")
                if appdata:
                    start_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", lnk_name)
                    if self.create_shortcut(watch_dir, start_path):
                        self.write_log("スタートアップに登録しました。")

            messagebox.showinfo("完了", "安定化監視ボットの配置が完了しました！")
            self.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    app = EqWatchdogDeployer()
    app.mainloop()