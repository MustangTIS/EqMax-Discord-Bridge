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
        self.geometry("750x1000")
        ctk.set_appearance_mode("dark")

        self.log_view = ctk.CTkTextbox(self, height=150)
        self.log_view.pack(pady=10, padx=20, fill="x")
        self.log_view.insert("0.0", "待機中...\n")
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_to_entry)

# --- 3. タイトルエリア ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax Discord連携ボット配置", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 0)) # 下の余白を少し調整

        self.label_subtitle = ctk.CTkLabel(
            self, 
            text="マルチ通知対応版 (Discord / Slack / Matrix)", 
            font=("Yu Gothic", 12),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 10))

        # --- 4. メインコンテンツ ---
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe があるフォルダを選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=530)
        self.entry_path.pack(side="left", padx=(0, 5))
        # --- ショートカット作成オプション ---
        self.var_desktop = ctk.BooleanVar(value=True)
        self.var_startup = ctk.BooleanVar(value=True)

        self.check_desktop = ctk.CTkCheckBox(self, text="デスクトップにショートカットを作成", variable=self.var_desktop)
        self.check_desktop.pack(pady=5)
        self.check_startup = ctk.CTkCheckBox(self, text="スタートアップに登録", variable=self.var_startup)
        self.check_startup.pack(pady=5)

        # --- 配置ボタン ---
        self.btn_deploy = ctk.CTkButton(self, text="ボットを配置する", command=self.run_deploy, fg_color="green")
        self.btn_deploy.pack(pady=20)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        self.label_webhook = ctk.CTkLabel(self, text="2. 送信先Webhook (最大5つ) と通知形式を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_webhook.pack(pady=(20, 5))
        
        # --- ループ開始 ---
        self.webhook_entries = []
        self.style_options = ["通知タイプを選択...", "DiscordEmbed", "DiscordSimple", "Slack", "Matrix"]

        for i in range(5):
            # メインフレーム
            main_frame = ctk.CTkFrame(self)
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

    def on_style_change(self, choice, main_frame):
        # 該当する webhook_entries を探して表示制御
        for item in self.webhook_entries:
            if item["style"].get() == choice:
                if choice == "Matrix":
                    item["matrix_frame"].pack(fill="x", padx=10)
                else:
                    item["matrix_frame"].pack_forget()

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

    def run_deploy(self):
        eqmax_dir = self.entry_path.get().strip()
        if not eqmax_dir or not os.path.isdir(eqmax_dir):
            messagebox.showerror("エラー", "EqMax.exe があるフォルダを正しく選択してください。")
            return

        bot_dir = os.path.join(eqmax_dir, "DiscordBot")
        os.makedirs(bot_dir, exist_ok=True)
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        templates_dir = os.path.join(base_dir, "Templates")
        assets_dir = os.path.join(base_dir, "Assets")

        try:
            # --- 修正: コピー対象のリストに "senders.py" を追加 ---
            for f in ["eqmax_discord.py", "eqmax_discord.bat", "senders.py"]:
                src = os.path.join(templates_dir, f)
                if os.path.exists(src):
                    shutil.copy2(src, bot_dir)
                    self.write_log(f"{f} をコピーしました。")

            ico_src = os.path.join(assets_dir, "eq-dis.ico")
            if os.path.exists(ico_src):
                shutil.copy2(ico_src, bot_dir)
                self.write_log("eq-dis.ico をコピーしました。")

            target_bat = os.path.join(bot_dir, "eqmax_discord.bat")

            # --- 修正箇所: run_deploy メソッド内のループ部分 ---
            webhooks_data = []
            
            # マッピング定義（UI表記 -> 内部コード）
            style_map = {
                "DiscordEmbed": "disembed",
                "DiscordSimple": "dissimple",
                "Slack": "slack",
                "Matrix": "matrix"
            }
            
            for item in self.webhook_entries:
                url = item["entry"].get().strip()
                style_raw = item["style"].get()
                
                if not url: continue # 入力がない場合はスキップ

                # 1. 形式の正規化（Matrixかどうかにかかわらず先にやる）
                style_normalized = style_map.get(style_raw, "disembed")
                
                # 2. ガードレール
                if style_normalized == "matrix":
                    if not url.startswith("https://"):
                        messagebox.showerror("設定エラー", "MatrixのサーバーURLは 'https://' から始めてください。")
                        return
                    if not item["token"].get().strip() or not item["room"].get().strip():
                        messagebox.showerror("設定エラー", "MatrixのTokenとRoom IDは必須です。")
                        return
                
                # 3. データ作成
                data = {"url": url, "style": style_normalized}
                if style_normalized == "matrix":
                    data["token"] = item["token"].get().strip()
                    data["room"] = item["room"].get().strip()
                
                webhooks_data.append(data)
            
            config = {"eqmax_dir": eqmax_dir, "destinations": webhooks_data}
            with open(os.path.join(bot_dir, "config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.write_log("config.json を保存しました。")

            # ショートカット作成
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

            msg = (
                "ボットの配置が完了しました。\n\n"
                "【アイコン表示についてのご案内】\n"
                "このWebhookを本ボット専用にしている場合、\n"
                "DiscordのWebhook設定からアイコンを「eq-dis.png」に変更して保存すると、\n"
                "通知がより見分けやすくなります。\n\n"
                "※他のツールとWebhookを共有している場合は、\n"
                "そのままでも動作に影響はありません。\n\n"
                "デスクトップのショートカットを確認してください。"
            )
            messagebox.showinfo("成功", msg)
            self.destroy()

        except Exception as e:
            self.write_log(f"エラー発生: {str(e)}")
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")

if __name__ == "__main__":
    EqMaxBotDeployer().mainloop()