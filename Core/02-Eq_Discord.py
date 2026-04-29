# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil
from datetime import datetime
import subprocess
import psutil
import sys

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

        self.style_map = {
            "DiscordEmbed": "disembed",
            "DiscordSimple": "dissimple",
            "Slack": "slack",
            "Matrix": "matrix",
            "Bluesky": "bluesky"
        }
        
        # --- 1. アイコンと画像の設定 ---
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception as e:
                print(f"Icon Error: {e}")

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
        self.geometry("750x850")
        ctk.set_appearance_mode("dark")

        # 右クリックメニューの作成
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_to_entry)

        self.log_view = ctk.CTkTextbox(self, height=150)
        self.log_view.pack(pady=10, padx=20, fill="x")
        self.log_view.insert("0.0", "待機中...\n")

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 3. タイトルエリア ---
        self.label_title = ctk.CTkLabel(
            self.main_container, 
            text=" EqMax Discord連携ボット配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 0))

        self.label_subtitle = ctk.CTkLabel(
            self.main_container, 
            text="マルチ通知対応版 (Discord / Slack / Matrix / Bluesky)", 
            font=("Yu Gothic", 12),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 10))

        # --- 4. パス選択エリア ---
        self.label_path = ctk.CTkLabel(self.main_container, text="1. EqMax.exe を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.path_frame.pack(pady=5)
        
        self.entry_path = ctk.CTkEntry(self.path_frame, width=530)
        self.entry_path.pack(side="left", padx=(0, 5))
        self.entry_path.bind("<Button-3>", lambda e, w=self.entry_path: self.show_context_menu(e, w))

        self.btn_browse = ctk.CTkButton(self.path_frame, text="ファイル選択...", width=100, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # オプション
        self.var_desktop = ctk.BooleanVar(value=True)
        self.var_startup = ctk.BooleanVar(value=True)

        self.check_desktop = ctk.CTkCheckBox(self.main_container, text="デスクトップにショートカットを作成", variable=self.var_desktop)
        self.check_desktop.pack(pady=5)
        self.check_startup = ctk.CTkCheckBox(self.main_container, text="スタートアップに登録", variable=self.var_startup)
        self.check_startup.pack(pady=5)

        # --- 5. 通知フィルタ設定 ---
        self.label_filter = ctk.CTkLabel(self.main_container, text="3. 震度通知・表示フィルタリング設定:", font=("Yu Gothic", 12, "bold"))
        self.label_filter.pack(pady=(10, 0))
        
        filter_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        filter_frame.pack(pady=5)

        self.label_min_int = ctk.CTkLabel(filter_frame, text="通知する最小震度:")
        self.label_min_int.pack(side="left", padx=5)
        self.combo_min_int = ctk.CTkOptionMenu(filter_frame, values=["1", "2", "3", "4", "5弱", "5強"], width=80)
        self.combo_min_int.set("3")
        self.combo_min_int.pack(side="left", padx=(0, 20))

        self.label_detail_int = ctk.CTkLabel(filter_frame, text="詳細表示の最小震度:")
        self.label_detail_int.pack(side="left", padx=5)
        self.combo_detail_int = ctk.CTkOptionMenu(filter_frame, values=["1", "2", "3", "4"], width=80)
        self.combo_detail_int.set("1")
        self.combo_detail_int.pack(side="left", padx=5)

        # --- 6. 送信先ループ設定 ---
        self.label_webhook = ctk.CTkLabel(self.main_container, text="2. 送信先情報 (最大5つ) と通知形式を選択:", font=("Yu Gothic", 12, "bold"))
        self.label_webhook.pack(pady=(20, 5))
        
        self.webhook_entries = []
        self.style_options = ["通知タイプを選択...", "DiscordEmbed", "DiscordSimple", "Slack", "Matrix", "Bluesky"]

        for i in range(5):
            main_frame = ctk.CTkFrame(self.main_container) 
            main_frame.pack(pady=3, padx=20, fill="x")
            
            container = ctk.CTkFrame(main_frame, fg_color="transparent")
            container.pack(fill="x", pady=5)
            
            entry = ctk.CTkEntry(container, placeholder_text=f"Webhook / Server URL {i+1}", width=480)
            entry.pack(side="left", padx=10)
            entry.bind("<Button-3>", lambda e, w=entry: self.show_context_menu(e, w))
            
            style_var = ctk.StringVar(value=self.style_options[0])
            combo = ctk.CTkOptionMenu(container, values=self.style_options, variable=style_var, 
                                      width=120, command=lambda c, m=main_frame: self.on_style_change(c, m))
            combo.pack(side="right", padx=10)
            
            extra_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            extra_1 = ctk.CTkEntry(extra_frame, placeholder_text="Token / Handle", width=200)
            extra_1.pack(side="left", padx=(10, 5), pady=5)
            extra_1.bind("<Button-3>", lambda e, w=extra_1: self.show_context_menu(e, w))

            extra_2 = ctk.CTkEntry(extra_frame, placeholder_text="Room ID / Password", width=200)
            extra_2.pack(side="left", padx=5, pady=5)
            extra_2.bind("<Button-3>", lambda e, w=extra_2: self.show_context_menu(e, w))
            
            self.webhook_entries.append({
                "entry": entry, "style": style_var, 
                "extra_frame": extra_frame, "extra_1": extra_1, "extra_2": extra_2
            })

        self.btn_deploy = ctk.CTkButton(self.main_container, text="ボットを配置する", command=self.run_deploy, fg_color="green", font=("Yu Gothic", 14, "bold"))
        self.btn_deploy.pack(pady=30)

    # --- メソッド群 ---

    def browse_file(self):
        f = filedialog.askopenfilename(title="EqMax.exe を選択してください", filetypes=[("実行ファイル", "EqMax.exe"), ("すべてのファイル", "*.*")])
        if f:
            d = os.path.dirname(f)
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, d)
            config_path = os.path.join(d, "DiscordBot", "config.json")
            if os.path.exists(config_path):
                self.load_existing_config(config_path)

    def on_style_change(self, choice, main_frame):
        target_item = next((item for item in self.webhook_entries if item["entry"].master.master == main_frame), None)
        if not target_item: return

        if choice == "Bluesky":
            current_url = target_item["entry"].get().strip()
            if not current_url or "bsky.app" in current_url:
                target_item["entry"].delete(0, "end")
                target_item["entry"].insert(0, "https://bsky.social")

        if choice in ["Matrix", "Bluesky"]:
            target_item["extra_frame"].pack(fill="x", padx=10, pady=2)
            if choice == "Bluesky":
                target_item["extra_1"].configure(placeholder_text="Handle (例: user.bsky.social)")
                target_item["extra_2"].configure(placeholder_text="App Password", show="*")
            else:
                target_item["extra_1"].configure(placeholder_text="Access Token")
                target_item["extra_2"].configure(placeholder_text="Room ID (!xxxx:yyyy)")
                target_item["extra_2"].configure(show="")
        else:
            target_item["extra_frame"].pack_forget()

    def show_context_menu(self, event, entry_widget):
        self.active_entry = entry_widget
        self.context_menu.post(event.x_root, event.y_root)

    def paste_to_entry(self):
        try:
            if hasattr(self, 'active_entry'):
                self.active_entry.insert("insert", self.clipboard_get())
        except: pass

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n")
        self.log_view.see("end")

    # --- ショートカット作成用 (PowerShell方式) ---
    def create_shortcut_wsh(self, target_bat_path, link_full_path):
        bot_dir = os.path.dirname(target_bat_path)
        py_script = os.path.join(bot_dir, "eqmax_discord.py")
        icon_path = os.path.join(bot_dir, "eq-dis.ico")
        p_script = os.path.normpath(os.path.abspath(py_script))
        l_path = os.path.normpath(os.path.abspath(link_full_path))
        w_dir = os.path.normpath(os.path.abspath(bot_dir))
        i_path = os.path.normpath(os.path.abspath(icon_path))

        ps_command = (
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{l_path}'); "
            f"$s.TargetPath = 'python.exe'; "
            f"$s.Arguments = '\"{p_script}\"'; "
            f"$s.WorkingDirectory = '{w_dir}'; "
            f"$s.IconLocation = '{i_path},0'; "
            f"$s.WindowStyle = 7; " # 最小化
            f"$s.Save()"
        )
        try:
            if os.path.exists(l_path): os.remove(l_path)
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, check=True)
            self.write_log(f"ショートカット作成: {os.path.basename(l_path)}")
            return True
        except Exception as e:
            self.write_log(f"ショートカット作成失敗: {e}")
            return False

    def kill_existing_bot(self):
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info.get('cmdline')
                if cmd and any("eqmax_discord.py" in s for s in cmd):
                    proc.terminate()
                    found = True
            except: continue
        return found

    def load_existing_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                destinations = data.get("destinations", [])
            if "min_trigger_int" in data: self.combo_min_int.set(data["min_trigger_int"])
            if "min_display_int" in data: self.combo_detail_int.set(data["min_display_int"])
            for i, item in enumerate(destinations):
                if i >= len(self.webhook_entries): break
                target = self.webhook_entries[i]
                target["entry"].delete(0, "end")
                target["entry"].insert(0, item.get("url", ""))
                rev_map = {v: k for k, v in self.style_map.items()}
                ui_style = rev_map.get(item.get("style"), "通知タイプを選択...")
                target["style"].set(ui_style)
                self.on_style_change(ui_style, target["entry"].master.master)
                if item.get("style") == "matrix":
                    target["extra_1"].insert(0, item.get("token", ""))
                    target["extra_2"].insert(0, item.get("room", ""))
                elif item.get("style") == "bluesky":
                    target["extra_1"].insert(0, item.get("bsky_handle") or item.get("handle", ""))
                    target["extra_2"].insert(0, item.get("bsky_password") or item.get("password", ""))
            self.write_log("設定をロードしました。")
        except Exception as e:
            self.write_log(f"設定ロード失敗: {e}")

    def run_deploy(self):
        eqmax_dir = self.entry_path.get().strip()
        if not eqmax_dir or not os.path.isdir(eqmax_dir):
            messagebox.showerror("エラー", "フォルダを正しく選択してください。")
            return

        bot_dir = os.path.join(eqmax_dir, "DiscordBot")
        os.makedirs(bot_dir, exist_ok=True)
        self.kill_existing_bot()

        base_dir = os.path.dirname(os.path.dirname(__file__))
        templates_dir = os.path.join(base_dir, "Templates")
        assets_dir = os.path.join(base_dir, "Assets")

        try:
            files = ["eqmax_discord.bat","eqmax_discord.py","config_manager.py","log_monitor.py","eew_parser.py","fixed_report_parser.py","eq_guardian_core.py","senders.py"]
            for f in files:
                src = os.path.join(templates_dir, f)
                if os.path.exists(src): shutil.copy2(src, bot_dir)
            
            ico_src = os.path.join(assets_dir, "eq-dis.ico")
            if os.path.exists(ico_src): shutil.copy2(ico_src, bot_dir)

            # JSON作成
            webhooks_data = []
            for item in self.webhook_entries:
                url = item["entry"].get().strip()
                style_raw = item["style"].get()
                if not url or style_raw == self.style_options[0]: continue
                style_norm = self.style_map.get(style_raw, "disembed")
                d = {"url": url, "style": style_norm}
                if style_norm == "matrix":
                    d["token"] = item["extra_1"].get().strip()
                    d["room"] = item["extra_2"].get().strip()
                elif style_norm == "bluesky":
                    d["bsky_handle"] = item["extra_1"].get().strip()
                    d["bsky_password"] = item["extra_2"].get().strip()
                webhooks_data.append(d)

            config = {
                "eqmax_dir": eqmax_dir,
                "exe_path": os.path.join(eqmax_dir, "EqMax.exe"),
                "min_trigger_int": self.combo_min_int.get(),
                "min_display_int": self.combo_detail_int.get(),
                "ram_limit": 1024,
                "destinations": webhooks_data
            }

            with open(os.path.join(bot_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            # --- ショートカット作成処理 (復旧) ---
            lnk_name = "EqMax-Discord通知ボット.lnk"
            target_bat = os.path.join(bot_dir, "eqmax_discord.bat")
            
            # デスクトップ
            if self.var_desktop.get():
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                    desk_path, _ = winreg.QueryValueEx(key, "Desktop")
                    winreg.CloseKey(key)
                except:
                    desk_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
                self.create_shortcut_wsh(target_bat, os.path.join(desk_path, lnk_name))

            # スタートアップ
            if self.var_startup.get():
                appdata = os.environ.get("APPDATA")
                if appdata:
                    start_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", lnk_name)
                    self.create_shortcut_wsh(target_bat, start_path)

            self.write_log("配置完了。")
            if messagebox.askyesno("完了", "配置に成功しました。今すぐ起動しますか？"):
                subprocess.Popen([sys.executable, "eqmax_discord.py"], cwd=bot_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"失敗しました: {e}")

if __name__ == "__main__":
    EqMaxBotDeployer().mainloop()