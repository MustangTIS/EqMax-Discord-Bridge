# -*- coding: utf-8 -*-
import os
import json
import shutil
import time
import subprocess
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None

class EqMaxSetupPatcher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. パス・アイコン・画像の設定 ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.normpath(os.path.join(self.base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(light_image=opened_img, dark_image=opened_img, size=(45, 45))
            except: pass

        # --- 2. ウィンドウ基本設定 ---
        self.title("EqMax Discord連携 - 初期設定パッチ")
        self.geometry("580x950")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 状態変数
        self.var_tw_reset = ctk.BooleanVar(value=True) 
        self.init_mode = ctk.StringVar(value="full") 
        self.var_check_count = ctk.BooleanVar(value=True) 

        self.create_widgets()

    def create_widgets(self):
        # 3. タイトルエリア
        self.label_title = ctk.CTkLabel(self, text=" EqMax 初期設定パッチ", image=self.logo_image,
                                        compound="left", font=("Yu Gothic", 24, "bold"))
        self.label_title.pack(pady=(20, 10))
        
        self.btn_web = ctk.CTkButton(self, text="EqMax公式サイトを開く (DL・最新情報の確認)", 
                                     fg_color="#28a745", hover_color="#218838", font=("Yu Gothic", 12, "bold"),
                                     command=lambda: webbrowser.open("https://melanion.info/eqmax/"))
        self.btn_web.pack(pady=(5, 10))

        # 1. フォルダ選択
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe を選択してください:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=350)
        self.entry_path.pack(side="left", padx=(0, 5))
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 2. セットアップオプション
        self.option_frame = ctk.CTkFrame(self)
        self.option_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.option_frame, text="2. セットアップオプション:", font=("Yu Gothic", 12, "bold")).pack(pady=(10, 5), padx=20, anchor="w")

        # Twitterバイパスチェック
        self.check_tw_reset = ctk.CTkCheckBox(self.option_frame, text="Twitter(X)機能を疑似認証でバイパスする\n(Discord連携専用として構築/既存の認証は消えてしまいます)", 
                                              variable=self.var_tw_reset, 
                                              command=self.toggle_template_options,
                                              font=("Yu Gothic", 11))
        self.check_tw_reset.pack(pady=5, padx=20, anchor="w")

        # テンプレート選択（フレーム）
        self.ini_select_frame = ctk.CTkFrame(self.option_frame, fg_color="#333333")
        self.ini_select_frame.pack(pady=5, padx=40, fill="x")
        
        self.r_current = ctk.CTkRadioButton(self.ini_select_frame, text="現状のINIを維持", variable=self.init_mode, value="current", font=("Yu Gothic", 10))
        self.r_current.pack(pady=2, padx=20, anchor="w")
        
        self.r_full = ctk.CTkRadioButton(self.ini_select_frame, text="Full構成テンプレート(通知＆YOUTUBE自動再生)を適用", variable=self.init_mode, value="full", font=("Yu Gothic", 10))
        self.r_full.pack(pady=2, padx=20, anchor="w")
        
        self.r_server = ctk.CTkRadioButton(self.ini_select_frame, text="Server用テンプレート(通知＆YOUTUBE自動再生無効化のメモリリーク対策構成)を適用", variable=self.init_mode, value="server", font=("Yu Gothic", 10))
        self.r_server.pack(pady=2, padx=20, anchor="w")

        # キャプチャ強制チェック（表示用）
        ctk.CTkCheckBox(self.option_frame, text="キャプチャと投稿用フォーマットを有効化 (強制)", variable=ctk.BooleanVar(value=True), state="disabled", font=("Yu Gothic", 11)).pack(pady=5, padx=20, anchor="w")
        
        # 間引き設定
        self.check_count = ctk.CTkCheckBox(self.option_frame, text="速報の間引き(未チェックで全報通知)", variable=self.var_check_count, font=("Yu Gothic", 11))
        self.check_count.pack(pady=5, padx=20, anchor="w")

        # 3. 表示例
        self.example_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.example_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.example_frame, text="【Discord通知レイアウト例】", font=("Yu Gothic", 10, "bold")).pack(pady=(5, 0))
        example_text = "緊急地震速報：第5報(終)予報\n震源地：奄美大島近海(28.0N 129.2E)\nマグニチュード：M3.8\n深さ：10km\n推定最大震度：3\n(ここに画像ファイルが添付されます)"
        ctk.CTkLabel(self.example_frame, text=example_text, justify="left", font=("Consolas", 11)).pack(pady=10, padx=10)

        # 実行ボタン
        self.btn_run = ctk.CTkButton(self, text="セットアップを実行", fg_color="#1f538d", hover_color="#14375e", height=60, 
                                     font=("Yu Gothic", 14, "bold"), command=self.run_patch, state="disabled")
        self.btn_run.pack(pady=10)

        # ログ表示
        self.log_view = ctk.CTkTextbox(self, width=500, height=120)
        self.log_view.pack(pady=10)

        # 初期状態の同期
        self.toggle_template_options()

    def toggle_template_options(self):
        """疑似認証バイパスがOFFなら、テンプレート上書き（＝Twitter初期化）をさせない"""
        if self.var_tw_reset.get():
            self.r_full.configure(state="normal")
            self.r_server.configure(state="normal")
        else:
            self.init_mode.set("current")
            self.r_full.configure(state="disabled")
            self.r_server.configure(state="disabled")

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if f:
            self.entry_path.delete(0, "end"); self.entry_path.insert(0, os.path.dirname(f))
            self.btn_run.configure(state="normal")

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n"); self.log_view.see("end")

    def run_patch(self):
        path = self.entry_path.get().strip()
        exe_path = os.path.join(path, "EqMax.exe")
        ini_path = os.path.join(path, "EqMax.ini")

        try:
            if not os.path.exists(ini_path):
                if messagebox.askyesno("初期設定", "EqMax.ini が見つかりません。\n一旦起動して終了させ、INIを生成してください。"):
                    subprocess.Popen([exe_path], cwd=path).wait()
                if not os.path.exists(ini_path): return

            while True:
                check = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq EqMax.exe'], capture_output=True, text=True)
                if "EqMax.exe" not in check.stdout: break
                messagebox.showinfo("要確認", "EqMaxを終了させてください。")

            # テンプレート適用 (疑似認証チェック時のみ動作)
            if self.init_mode.get() != "current":
                folder = "EqINI-Full" if self.init_mode.get() == "full" else "EqINI-Server"
                src = os.path.normpath(os.path.join(self.base_dir, "..", "Templates", folder, "EqMax.ini"))
                if os.path.exists(src):
                    shutil.copy2(src, ini_path)
                    self.write_log(f"テンプレート({folder})を適用しました。")

            self.patch_ini_final(ini_path)

            if self.var_tw_reset.get():
                self.create_initial_json(path)
                self.write_log("疑似認証用JSONを生成しました。")

            messagebox.showinfo("完了", "セットアップ完了！")
            self.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"失敗: {e}")

    def patch_ini_final(self, ini_path):
        with open(ini_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        S = "\\t"
        eew_line = "EEWItems=" + S.join(["", "[緊急地震速報：]", "報番号", "最終報", "警報", "<改行>", "[震源地：]", "震央名", "[(]", "緯度経度", "[)]", "<改行>", "[マグニチュード：M]", "マグニチュード", "<改行>", "[深さ：]", "深さ", "<改行>", "[推定最大震度：]", "最大震度", "<改行>", "画像"])
        
        # 常に適用する項目
        core_updates = {
            "AutoCapture": "1",
            "TwitterBotEnabled": "1",
            "EEWEnabled": "1",
            "CheckTweetCount": "1" if self.var_check_count.get() else "0"
        }

        # 疑似認証チェック時のみ適用する項目
        tw_bypass_updates = {
            "AppName": "EqMax_Discord",
            "BearerObtainedAt": "1899-12-30T00:00:00.000+09:00",
            "ClientID": "dummy_id",
            "ConsumerKey": "dummy",
            "AccessToken": "dummy" ,
            "TwitterDummyPost": "1"
        }

        target_updates = core_updates.copy()
        if self.var_tw_reset.get():
            target_updates.update(tw_bypass_updates)

        new_lines = []
        applied = set()
        for line in lines:
            ls = line.strip()
            if ls.startswith("EEWItems="):
                new_lines.append(eew_line + "\n"); applied.add("EEWItems"); continue
            
            found = False
            for k, v in target_updates.items():
                if ls.startswith(k + "="):
                    new_lines.append(f"{k}={v}\n"); applied.add(k); found = True; break
            if not found:
                new_lines.append(line if line.endswith('\n') else line + '\n')

        final_lines = []
        tw_found = False
        for line in new_lines:
            final_lines.append(line)
            if self.var_tw_reset.get() and line.strip().lower() == "[twitter]":
                tw_found = True
                for k in ["ClientID", "ClientSecret", "RefreshToken", "BearerToken", "BearerObtainedAt", "ConsumerKey", "ConsumerSecret", "AccessToken", "AccessTokenSecret"]:
                    if k not in applied:
                        final_lines.append(f"{k}={tw_bypass_updates.get(k, 'dummy')}\n"); applied.add(k)

        # 足りないキーを末尾に追記
        for k, v in target_updates.items():
            if k not in applied: final_lines.append(f"{k}={v}\n")

        with open(ini_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.writelines(final_lines)
        self.write_log("INIの更新（キャプチャ・間引き設定等）を完了。")

    def create_initial_json(self, path):
        json_path = os.path.join(path, "v2_Tokens.json")
        data = {"appname": "EqMax_Discord", "client_id": "dummy_id", "refresh_token": "dummy_refresh", "bearer_token_obtained_at": "1899-12-30T00:00:00.000+09:00"}
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    EqMaxSetupPatcher().mainloop()