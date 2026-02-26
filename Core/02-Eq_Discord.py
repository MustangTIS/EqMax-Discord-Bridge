# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil
from datetime import datetime
import subprocess

class EqMaxBotDeployer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")  # ダークモードに固定
        self.title("EqMax 多機能通知連携 - ボット配置ツール")
        self.geometry("750x850")

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="貼り付け", command=self.paste_to_entry)

        # 1. Path Selection
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe があるフォルダを選択してください:")
        self.label_path.pack(pady=(20, 0))
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=530)
        self.entry_path.pack(side="left", padx=(0, 5))
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 2. Webhook URLs
        self.label_webhook = ctk.CTkLabel(self, text="2. 送信先Webhook (最大5つ) と通知形式を選択してください:", font=("", 12, "bold"))
        self.label_webhook.pack(pady=(20, 5))
        
        self.webhook_entries = []
        self.style_options = ["embed", "simple"]

        for i in range(5):
            frame = ctk.CTkFrame(self)
            frame.pack(pady=3, padx=20, fill="x")
            entry = ctk.CTkEntry(frame, placeholder_text=f"URL {i+1}", width=480)
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
        self.check_desktop = ctk.CTkCheckBox(self.option_frame, text="デスクトップにショートカットを作成する", variable=self.var_desktop)
        self.check_desktop.pack(pady=5, padx=20, anchor="w")
        self.var_startup = ctk.BooleanVar(value=True)
        self.check_startup = ctk.CTkCheckBox(self.option_frame, text="Windows起動時に自動実行する", variable=self.var_startup)
        self.check_startup.pack(pady=5, padx=20, anchor="w")

        # Run Button
        self.btn_run = ctk.CTkButton(self, text="ボットを配置して設定保存", fg_color="darkgreen", height=60, command=self.run_deploy)
        self.btn_run.pack(pady=20)

        # ログ表示
        self.log_view = ctk.CTkTextbox(self, width=690, height=120, fg_color="#333333", text_color="#00FF00", border_width=1, border_color="#555555", font=("Consolas", 12))
        self.log_view.pack(pady=10)

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
        """ショートカットを作成。アイコンはコピー済みのbot_dir内を参照する"""
        bot_dir = os.path.dirname(target_bat_path)
        py_script = os.path.join(bot_dir, "eqmax_discord.py")
        icon_path = os.path.join(bot_dir, "eq-dis.ico")

        p_script = py_script.replace("\\", "\\\\")
        l_path = link_full_path.replace("\\", "\\\\")
        i_path = icon_path.replace("\\", "\\\\")
        w_dir = bot_dir.replace("\\", "\\\\")

        vbs = (
            f'Set oWS = CreateObject("WScript.Shell")\n'
            f'Set oLink = oWS.CreateShortcut("{l_path}")\n'
            f'oLink.TargetPath = "python.exe"\n'
            f'oLink.Arguments = "{p_script}"\n'
            f'oLink.WorkingDirectory = "{w_dir}"\n'
            f'oLink.IconLocation = "{i_path}"\n'
            f'oLink.WindowStyle = 7\n'
            f'oLink.Save'
        )
        
        vbs_path = os.path.join(os.environ["TEMP"], "create_lnk_dis.vbs")
        try:
            with open(vbs_path, "w", encoding="shift-jis") as f: 
                f.write(vbs)
            subprocess.run(["cscript", "//nologo", vbs_path], shell=True)
            if os.path.exists(vbs_path): os.remove(vbs_path)
        except Exception as e:
            self.write_log(f"Shortcut Error: {e}")

    def run_deploy(self):
        eqmax_dir = self.entry_path.get().strip()
        destinations = []
        for item in self.webhook_entries:
            url = item["entry"].get().strip()
            if url.startswith("https://"):
                destinations.append({"url": url, "style": item["style"].get()})

        if not eqmax_dir or not os.path.isdir(eqmax_dir):
            messagebox.showerror("Error", "Folder Error.")
            return
        if not destinations:
            messagebox.showerror("Error", "URL Error.")
            return

        bot_dir = os.path.join(eqmax_dir, "Discordbot")
        os.makedirs(bot_dir, exist_ok=True)
        
        # パス定義
        base_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Templates")
        assets_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Assets")
        target_bat = os.path.join(bot_dir, "eqmax_discord.bat")
        
        # ファイルコピー
        for f in ["eqmax_discord.py", "eqmax_discord.bat"]:
            src = os.path.join(base_src, f)
            if os.path.exists(src):
                shutil.copy2(src, bot_dir)
                self.write_log(f"Copied: {f}")

        # アイコンの物理コピー（これでツールを消してもアイコンが維持される）
        icon_file = "eq-dis.ico"
        icon_src_path = os.path.join(assets_src, icon_file)
        if os.path.exists(icon_src_path):
            shutil.copy2(icon_src_path, bot_dir)
            self.write_log(f"Copied: {icon_file}")

        # JSON保存
        normalized_dir = os.path.normpath(eqmax_dir).replace("\\", "/")
        config_path = os.path.join(bot_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"eqmax_dir": normalized_dir, "destinations": destinations}, f, indent=4, ensure_ascii=False)

        # ショートカット作成
        lnk_name = "EqMax-Discord通知ボット.lnk"
        if self.var_desktop.get():
            self.create_shortcut_wsh(target_bat, os.path.join(os.environ["USERPROFILE"], "Desktop", lnk_name))
            self.write_log("Created: Desktop shortcut")
        if self.var_startup.get():
            self.create_shortcut_wsh(target_bat, os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup", lnk_name))
            self.write_log("Registered: Windows Startup")

        messagebox.showinfo("成功", "書き換え完了\nインストール用フォルダは削除しても大丈夫です。")
        self.destroy()

if __name__ == "__main__":
    EqMaxBotDeployer().mainloop()