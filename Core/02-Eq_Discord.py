#02-Eq_Discord.py
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
            "Matrix": "matrix"
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
        self.geometry("750x800")
        ctk.set_appearance_mode("dark")

        self.log_view = ctk.CTkTextbox(self, height=150)
        self.log_view.pack(pady=10, padx=20, fill="x")
        self.log_view.insert("0.0", "待機中...\n")
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_to_entry)

        # --- 3. タイトルエリア ---
        self.label_title = ctk.CTkLabel(
            self.main_container, 
            text=" EqMax Discord連携ボット配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 0)) # 下の余白を少し調整

        self.label_subtitle = ctk.CTkLabel(
            self.main_container, 
            text="マルチ通知対応版 (Discord / Slack / Matrix)", 
            font=("Yu Gothic", 12),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 10))

        # --- 4. メインコンテンツ ---
        self.label_path = ctk.CTkLabel(self.main_container, text="1. EqMax.exe があるフォルダを選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=530)
        self.entry_path.pack(side="left", padx=(0, 5))
        # --- ショートカット作成オプション ---
        self.var_desktop = ctk.BooleanVar(value=True)
        self.var_startup = ctk.BooleanVar(value=True)

        self.check_desktop = ctk.CTkCheckBox(self.main_container, text="デスクトップにショートカットを作成", variable=self.var_desktop)
        self.check_desktop.pack(pady=5)
        self.check_startup = ctk.CTkCheckBox(self.main_container, text="スタートアップに登録", variable=self.var_startup)
        self.check_startup.pack(pady=5)

        # --- 配置ボタン ---
        self.btn_deploy = ctk.CTkButton(self.main_container, text="ボットを配置する", command=self.run_deploy, fg_color="green")
        # --- 3. 通知フィルタリング設定 ---
        self.label_filter = ctk.CTkLabel(self.main_container, text="3. 確定震度通知・表示フィルタリング設定(EEWの通知設定ではありません):", font=("Yu Gothic", 12, "bold"))
        self.label_filter.pack(pady=(10, 0))
        
        filter_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        filter_frame.pack(pady=5)

        # 通知しきい値（この震度以上の地震なら送る）
        self.label_min_int = ctk.CTkLabel(filter_frame, text="通知する最大震度:")
        self.label_min_int.pack(side="left", padx=5)
        self.combo_min_int = ctk.CTkOptionMenu(filter_frame, values=["1", "2", "3", "4", "5弱", "5強"], width=80)
        self.combo_min_int.set("3")
        self.combo_min_int.pack(side="left", padx=(0, 20))

        # 詳細表示しきい値（リストに載せる最小震度）
        self.label_detail_int = ctk.CTkLabel(filter_frame, text="詳細を表示する最小震度:")
        self.label_detail_int.pack(side="left", padx=5)
        self.combo_detail_int = ctk.CTkOptionMenu(filter_frame, values=["1", "2", "3", "4"], width=80)
        self.combo_detail_int.set("1") # 震度1から全部出すのがデフォルト
        self.combo_detail_int.pack(side="left", padx=5)
        
        self.btn_deploy.pack(pady=20)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        self.label_webhook = ctk.CTkLabel(self.main_container, text="2. 送信先Webhook (最大5つ) と通知形式を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_webhook.pack(pady=(20, 5))
        
        # --- ループ開始 ---
        self.webhook_entries = []
        self.style_options = ["通知タイプを選択...", "DiscordEmbed", "DiscordSimple", "Slack", "Matrix"]

        for i in range(5):
            # メインフレーム
            main_frame = ctk.CTkFrame(self.main_container) 
            main_frame.pack(pady=3, padx=20, fill="x")
            
            # コンテナ（上段・下段を管理）
            container = ctk.CTkFrame(main_frame, fg_color="transparent")
            container.pack(fill="x", pady=5)
            
            entry = ctk.CTkEntry(container, placeholder_text=f"Webhook / Matrix Homeserver URL {i+1}", width=480)
            entry.pack(side="left", padx=10)
            entry.bind("<Button-3>", lambda e, en=entry: self.show_context_menu(e, en))
            
            style_var = ctk.StringVar(value=self.style_options[0])
            combo = ctk.CTkOptionMenu(container, values=self.style_options, variable=style_var, 
                                     width=120, command=lambda c, m=main_frame: self.on_style_change(c, m))
            combo.pack(side="right", padx=10)
            
            # 下段用（最初は非表示）
            matrix_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            token_entry = ctk.CTkEntry(matrix_frame, placeholder_text="Access Token", width=200)
            room_entry = ctk.CTkEntry(matrix_frame, placeholder_text="Room ID", width=200)
            
            # 貼り付けメニューを紐付ける
            token_entry.bind("<Button-3>", lambda e, en=token_entry: self.show_context_menu(e, en))
            room_entry.bind("<Button-3>", lambda e, en=room_entry: self.show_context_menu(e, en))
            
            token_entry.pack(side="left", padx=(10, 5), pady=5)
            room_entry.pack(side="left", padx=5, pady=5)
            
            self.webhook_entries.append({
                "entry": entry, "style": style_var, 
                "matrix_frame": matrix_frame, "token": token_entry, "room": room_entry
            })

    def load_existing_config(self, config_path):
        """既存のconfig.jsonを読み込み、フォームに値をセットする"""
        if not os.path.exists(config_path):
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                destinations = data.get("destinations", [])

            # 既存の入力欄をクリアしてから値をセット
            for i, item in enumerate(destinations):
                if i >= len(self.webhook_entries): break
                
                # 震度設定の復元
                if "min_trigger_int" in data:
                    self.combo_min_int.set(data["min_trigger_int"])
                if "detail_intensity" in data:
                    self.combo_detail_int.set(data["detail_intensity"])

                # --- Webhook URL の読み込み ---
                entry_widget = self.webhook_entries[i]["entry"]
                entry_widget.delete(0, "end")  # ★まず今の内容を消す
                entry_widget.insert(0, item.get("url", ""))

                # --- スタイル（内部コード -> UI表記）の読み込み ---
                rev_style_map = {v: k for k, v in self.style_map.items()} 
                ui_style = rev_style_map.get(item.get("style"), "通知タイプを選択...")
                self.webhook_entries[i]["style"].set(ui_style)

                # --- Matrixの場合の特殊処理（トークン類） ---
                # Matrixでなくても、一旦入力欄を消しておかないとゴミが残るので一括処理
                token_w = self.webhook_entries[i]["token"]
                room_w = self.webhook_entries[i]["room"]
                
                token_w.delete(0, "end")  # ★消す
                room_w.delete(0, "end")   # ★消す

                if item.get("style") == "matrix":
                    self.webhook_entries[i]["matrix_frame"].pack(fill="x", padx=10) # ここ
                    token_w.insert(0, item.get("token", ""))
                    room_w.insert(0, item.get("room", ""))

            self.write_log("既存の設定を読み込みました。")
        except Exception as e:
            self.write_log(f"設定の読み込みに失敗しました: {e}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            eqmax_dir = os.path.dirname(file_path)
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, eqmax_dir)

            # --- ここに読み込み処理を追加 ---
            config_path = os.path.join(eqmax_dir, "DiscordBot", "config.json")
            if os.path.exists(config_path):
                self.load_existing_config(config_path)
            else:
                self.write_log("既存のconfig.jsonは見つかりませんでした。")

    def on_style_change(self, choice, main_frame):
        # 該当する webhook_entries を探して表示制御
        for item in self.webhook_entries:
            if item["style"].get() == choice:
                if choice == "Matrix":
                    item["matrix_frame"].pack(fill="x", padx=10)
                else:
                    item["matrix_frame"].pack_forget()
    
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
        """通常版：Pythonを直接起動しアイコンを指定する"""
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
            self.write_log(f"{os.path.basename(l_path)} を作成しました（通常版）。")
            return True
        except Exception as e:
            self.write_log(f"通常ショートカット作成失敗: {e}")
            return False

    def create_safe_shortcut_wsh(self, target_bat_path, link_full_path):
        """セーフモード版：バッチファイルを直接起動し環境修復を優先する"""
        l_path = os.path.normpath(os.path.abspath(link_full_path))
        t_path = os.path.normpath(os.path.abspath(target_bat_path))
        w_dir = os.path.dirname(t_path)

        ps_command = (
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{l_path}'); "
            f"$s.TargetPath = '{t_path}'; "
            f"$s.WorkingDirectory = '{w_dir}'; "
            f"$s.WindowStyle = 1; " # <--- ここを 7 から 1 に変更
            f"$s.Save()"
        )
        try:
            if os.path.exists(l_path): os.remove(l_path)
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, check=True)
            self.write_log(f"{os.path.basename(l_path)} を作成しました（セーフモード版）。")
            return True
        except Exception as e:
            self.write_log(f"セーフモードショートカット作成失敗: {e}")
            return False

    def kill_existing_bot(self, script_name="eqmax_discord.py"):
        """実行中の同名スクリプトプロセスを探して終了させる"""
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # プロセス引数にスクリプト名が含まれているか確認
                cmdline = proc.info.get('cmdline')
                if cmdline and any(script_name in s for s in cmdline):
                    self.write_log(f"稼働中の旧ボット(PID: {proc.info['pid']})を終了させます...")
                    proc.terminate()  # 終了信号を送る
                    try:
                        proc.wait(timeout=3) # 終了を待つ
                    except psutil.TimeoutExpired:
                        proc.kill() # 頑固な場合は強制終了
                    found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return found

    def run_deploy(self):
        eqmax_dir = self.entry_path.get().strip()
        if not eqmax_dir or not os.path.isdir(eqmax_dir):
            messagebox.showerror("エラー", "EqMax.exe があるフォルダを正しく選択してください。")
            return

        bot_dir = os.path.join(eqmax_dir, "DiscordBot")
        os.makedirs(bot_dir, exist_ok=True)
        
        # --- 1. 旧ボットの停止 (ファイルのロックを解除するために最初に行う) ---
        if self.kill_existing_bot():
            self.write_log("稼働中の旧ボットを終了しました。")
            import time
            time.sleep(1) # プロセスが完全に消え、ファイルが解放されるのを待つ

        # --- ここから配置処理 ---
        base_dir = os.path.dirname(os.path.dirname(__file__))
        templates_dir = os.path.join(base_dir, "Templates")
        assets_dir = os.path.join(base_dir, "Assets")

        try:
            # --- 2. ファイルのコピー ---
            required_files = [
                "eqmax_discord.bat",
                "eqmax_discord.py",
                "config_manager.py",
                "log_monitor.py",
                "eew_parser.py",
                "fixed_report_parser.py",
                "eq_guardian_core.py",
                "senders.py"
            ]
            for f in required_files:
                src = os.path.join(templates_dir, f)
                if os.path.exists(src):
                    shutil.copy2(src, bot_dir)
                    self.write_log(f"{f} をコピーしました。")

            ico_src = os.path.join(assets_dir, "eq-dis.ico")
            if os.path.exists(ico_src):
                shutil.copy2(ico_src, bot_dir)
                self.write_log("eq-dis.ico をコピーしました。")

            target_bat = os.path.join(bot_dir, "eqmax_discord.bat")

            # --- 3. 設定データの構築と保存 (既存) ---
            webhooks_data = []
            style_map = {
                "DiscordEmbed": "disembed",
                "DiscordSimple": "dissimple",
                "Slack": "slack",
                "Matrix": "matrix"
            }

            for item in self.webhook_entries:
                url = item["entry"].get().strip()
                style_raw = item["style"].get()
                if not url: continue

                style_normalized = style_map.get(style_raw, "disembed")

                if style_normalized == "matrix":
                    if not url.startswith("https://"):
                        messagebox.showerror("設定エラー", "MatrixのサーバーURLは 'https://' から始めてください。")
                        return
                    if not item["token"].get().strip() or not item["room"].get().strip():
                        messagebox.showerror("設定エラー", "MatrixのTokenとRoom IDは必須です。")
                        return

                data = {"url": url, "style": style_normalized}
                if style_normalized == "matrix":
                    data["token"] = item["token"].get().strip()
                    data["room"] = item["room"].get().strip()

                webhooks_data.append(data)

            config = {
                "eqmax_dir": eqmax_dir, 
                "exe_path": os.path.join(eqmax_dir, "EqMax.exe"), # 明示しておくと親切
                "min_trigger_int": self.combo_min_int.get(),     
                "min_display_int": self.combo_detail_int.get(),  # 本体側は 'min_display_int' を参照している箇所があるため
                "ram_limit": 1024,                               # デフォルト値として入れておくと安心
                "destinations": webhooks_data
            }

            with open(os.path.join(bot_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.write_log("config.json を保存しました。")

            # --- 4. ショートカット作成 (既存) ---
            lnk_name = "EqMax-Discord通知ボット.lnk"
            safe_lnk_name = "EqMax-Discord通知ボット(セーフモード).lnk"

            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                desk_path, _ = winreg.QueryValueEx(key, "Desktop")
                winreg.CloseKey(key)
            except:
                desk_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

            if self.var_desktop.get() and desk_path:
                self.create_shortcut_wsh(target_bat, os.path.join(desk_path, lnk_name))
                self.create_safe_shortcut_wsh(target_bat, os.path.join(desk_path, safe_lnk_name))

            if self.var_startup.get():
                appdata = os.environ.get("APPDATA")
                if appdata:
                    start_path = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup", lnk_name)
                    self.create_shortcut_wsh(target_bat, start_path)

            # --- 5. 完了通知と再起動確認 (新機能) ---
            self.write_log("すべての配置作業が完了しました。")

            if messagebox.askyesno("成功", "ボットの配置が完了しました。\n\n今すぐボットを起動（再起動）しますか？"):
                # 新しいコンソールでボットを起動
                # pythonw.exe にすると黒い画面なしで起動できますが、
                # デバッグしやすさを考慮して python.exe (黒い画面あり) で起動させています
                subprocess.Popen(
                    [sys.executable, "eqmax_discord.py"],
                    cwd=bot_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                self.write_log("ボットを起動しました。")
                messagebox.showinfo("起動完了", "ボットを起動しました。正常に動作するか確認してください。")
            else:
                messagebox.showinfo("成功", "ボットの配置が完了しました。\n手動で起動する場合はショートカットを使用してください。")

            self.destroy()

        except Exception as e:
            self.write_log(f"エラー発生: {str(e)}")
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")

if __name__ == "__main__":
    EqMaxBotDeployer().mainloop()