# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil
from datetime import datetime
import subprocess
try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None

class EqMaxBotDeployer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. アイコンと画像の設定 ---
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        # ウィンドウアイコン
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception as e:
                print(f"Icon Error: {e}")

        # ロゴ画像
        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(
                    light_image=opened_img,
                    dark_image=opened_img,
                    size=(45, 45)
                )
            except Exception as e:
                print(f"Image Load Error: {e}")

        # --- 2. ウィンドウ基本設定 ---
        self.title("EqMax 多機能通知連携 - ボット配置ツール")
        self.geometry("750x920") # コンテンツ量に合わせて高さを調整
        ctk.set_appearance_mode("dark")

        # コンテキストメニュー（右クリック貼り付け用）
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_to_entry)

        # --- 3. タイトルエリア (ロゴ付き) ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax Discord連携ボット配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # --- 4. メインコンテンツ ---

        # 1. Path Selection
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe があるフォルダを選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=530)
        self.entry_path.pack(side="left", padx=(0, 5))
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 2. Webhook URLs
        self.label_webhook = ctk.CTkLabel(self, text="2. 送信先Webhook (最大5つ) と通知形式を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_webhook.pack(pady=(20, 5))
        
        self.webhook_entries = []
        self.style_options = ["embed", "simple"]

        for i in range(5):
            frame = ctk.CTkFrame(self)
            frame.pack(pady=3, padx=20, fill="x")
            entry = ctk.CTkEntry(frame, placeholder_text=f"Discord Webhook URL {i+1}", width=480)
            entry.pack(side="left", padx=10, pady=10)
            entry.bind("<Button-3>", lambda e, en=entry: self.show_context_menu(e, en))
            style_var = ctk.StringVar(value="embed")
            combo = ctk.CTkOptionMenu(frame, values=self.style_options, variable=style_var, width=100)
            combo.pack(side="right", padx=10)
            self.webhook_entries.append({"entry": entry, "style": style_var})

        # 3. Options
        self.option_frame = ctk.CTkFrame(self)
        self.option_frame.pack(pady=20, padx=20, fill="x")
        self.var_desktop = ctk.BooleanVar(value=True)
        self.check_desktop = ctk.CTkCheckBox(self.option_frame, text="デスクトップにショートカットを作成する", variable=self.var_desktop, font=("Yu Gothic", 11))
        self.check_desktop.pack(pady=5, padx=20, anchor="w")
        self.var_startup = ctk.BooleanVar(value=True)
        self.check_startup = ctk.CTkCheckBox(self.option_frame, text="Windows起動時に自動実行する（推奨）", variable=self.var_startup, font=("Yu Gothic", 11))
        self.check_startup.pack(pady=5, padx=20, anchor="w")

        # Run Button
        self.btn_run = ctk.CTkButton(self, text="ボットを配置して設定を保存", fg_color="#28a745", hover_color="#218838", height=60, 
                                     font=("Yu Gothic", 14, "bold"), command=self.run_deploy)
        self.btn_run.pack(pady=10)

        # ログ表示
        self.log_view = ctk.CTkTextbox(self, width=690, height=120, fg_color="#1a1a1a", text_color="#00FF00", border_width=1, border_color="#444444", font=("Consolas", 12))
        self.log_view.pack(pady=10)

    # --- 以下、ロジック部分は変更なし ---

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.dirname(file_path))

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n")
        self.log_view.see("end")

    def show_context_menu(self, event, entry_widget):
        self.active_entry = entry_widget
        self.context_menu.post(event.x_root, event.y_root)

    def paste_to_entry(self):
        try:
            self.active_entry.insert("insert", self.clipboard_get())
        except: pass

    def create_shortcut_wsh(self, target_bat_path, link_full_path):
        """VBSを使わず、Powershell経由でショートカットを作成する（アイコン指定が可能）"""
        bot_dir = os.path.dirname(target_bat_path)
        py_script = os.path.join(bot_dir, "eqmax_discord.py")
        # アイコンはAssetsフォルダからコピーしてきたものを使用
        icon_path = os.path.join(bot_dir, "eq-dis.ico")

        # パスの正規化
        p_script = os.path.normpath(os.path.abspath(py_script))
        l_path = os.path.normpath(os.path.abspath(link_full_path))
        w_dir = os.path.normpath(os.path.abspath(bot_dir))
        i_path = os.path.normpath(os.path.abspath(icon_path))

        # PowerShellコマンド：ショートカット作成
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
            
            # PowerShellを実行
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, check=True)
            self.write_log(f"{os.path.basename(l_path)} を作成しました（アイコン付）。")
            return True

        except Exception as e:
            self.write_log("PowerShell方式失敗。バッチファイル直接コピーに切り替えます。")
            try:
                dst_bat = l_path.replace(".lnk", ".bat")
                shutil.copy2(target_bat_path, dst_bat)
                self.write_log(f"バッチファイルとして {os.path.basename(dst_bat)} を配置しました。")
                return True
            except:
                return False

    def run_deploy(self):
        # 1. 基本的な入力チェック
        eqmax_dir = self.entry_path.get().strip()
        if not eqmax_dir or not os.path.isdir(eqmax_dir):
            messagebox.showerror("エラー", "EqMax.exe があるフォルダを正しく選択してください。")
            return

        # 保存先ディレクトリの設定
        bot_dir = os.path.join(eqmax_dir, "DiscordBot")
        os.makedirs(bot_dir, exist_ok=True)
        
        # テンプレートディレクトリの特定（Coreフォルダの親 -> Templates）
        base_dir = os.path.dirname(os.path.dirname(__file__))
        templates_dir = os.path.join(base_dir, "Templates")
        assets_dir = os.path.join(base_dir, "Assets")

        try:
            # 2. ファイルのコピー処理
            # 実行に必要なスクリプト類
            for f in ["eqmax_discord.py", "eqmax_discord.bat"]:
                src = os.path.join(templates_dir, f)
                if os.path.exists(src):
                    shutil.copy2(src, bot_dir)
                    self.write_log(f"{f} をコピーしました。")
            
            # アイコンファイル（ショートカット用）
            ico_src = os.path.join(assets_dir, "eq-dis.ico")
            if os.path.exists(ico_src):
                shutil.copy2(ico_src, bot_dir)

            # 配置したバッチファイルのフルパスを変数に格納 (NameErrorの修正箇所)
            target_bat = os.path.join(bot_dir, "eqmax_discord.bat")

            # 3. Webhook設定の保存
            webhooks_data = []
            for item in self.webhook_entries:
                url = item["entry"].get().strip()
                if url:
                    webhooks_data.append({"url": url, "style": item["style"].get()})
            
            if not webhooks_data:
                messagebox.showwarning("警告", "Webhook URLが1つも入力されていません。")

            config = {
                "eqmax_dir": eqmax_dir,
                "destinations": webhooks_data  # ここを destinations に書き換える
            }
            
            with open(os.path.join(bot_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.write_log("config.json を保存しました。")

            # 4. ショートカット作成 (強化版ロジック)
            lnk_name = "EqMax-Discord通知ボット.lnk"
            
            # レジストリから正確なデスクトップパスを取得
            desk_path = None
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                desk_path, _ = winreg.QueryValueEx(key, "Desktop")
                winreg.CloseKey(key)
            except:
                desk_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

            if self.var_desktop.get() and desk_path:
                self.create_shortcut_wsh(target_bat, os.path.join(desk_path, lnk_name))
                
            if self.var_startup.get():
                appdata = os.environ.get("APPDATA")
                if appdata:
                    start_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", lnk_name)
                    self.create_shortcut_wsh(target_bat, start_path)

            messagebox.showinfo("成功", "ボットの配置と設定保存が完了しました。")
            self.destroy()

        except Exception as e:
            self.write_log(f"エラー発生: {str(e)}")
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")

if __name__ == "__main__":
    EqMaxBotDeployer().mainloop()