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
        """VBSを使わず、Powershell経由でショートカットを作成する（アイコン指定が可能）"""
        py_script = os.path.join(watch_dir, "Eq_Watchdog.py")
        exe_icon_path = self.entry_path.get().strip() # EqMax.exeからアイコンを拝借

        # パスの正規化
        p_script = os.path.normpath(os.path.abspath(py_script))
        l_path = os.path.normpath(os.path.abspath(link_path))
        w_dir = os.path.normpath(os.path.abspath(watch_dir))
        i_path = os.path.normpath(os.path.abspath(exe_icon_path))

        # PowerShellコマンド：ショートカット作成 (これならVBSよりブロックされにくい)
        ps_command = (
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{l_path}'); "
            f"$s.TargetPath = 'python.exe'; "
            f"$s.Arguments = '\"{p_script}\"'; "
            f"$s.WorkingDirectory = '{w_dir}'; "
            f"$s.IconLocation = '{i_path},0'; "
            f"$s.WindowStyle = 7; " # 最小化で実行
            f"$s.Save()"
        )

        try:
            # 既存のショートカットを削除
            if os.path.exists(l_path):
                os.remove(l_path)
            
            # PowerShellを実行して作成
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, check=True)
            self.write_log(f"{os.path.basename(l_path)} を作成しました（アイコン付）。")
            return True

        except Exception as e:
            self.write_log("PowerShell方式失敗。バッチファイル直接コピーに切り替えます。")
            # --- 失敗時のフォールバック（バックアッププラン） ---
            try:
                dst_bat = l_path.replace(".lnk", ".bat")
                src_bat = os.path.join(watch_dir, "Eq_Watchdog.bat")
                shutil.copy2(src_bat, dst_bat)
                self.write_log(f"バッチファイルとして {os.path.basename(dst_bat)} を配置しました。")
                return True
            except:
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
            
            # --- 【強化ポイント】より確実なデスクトップパスの取得 ---
            desk_path = None
            try:
                # Windowsの環境変数から取得を試みる
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                desk_path, _ = winreg.QueryValueEx(key, "Desktop")
                winreg.CloseKey(key)
            except:
                # 失敗した場合は標準的なパスを使用
                desk_path = os.path.join(os.path.expanduser("~"), "Desktop")

            if self.var_desktop.get() and desk_path:
                target_lnk = os.path.join(desk_path, lnk_name)
                if self.create_shortcut(watch_dir, target_lnk):
                    self.write_log(f"デスクトップにショートカットを作成しました: {desk_path}")
                else:
                    self.write_log("デスクトップへのショートカット作成に失敗しました。")

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