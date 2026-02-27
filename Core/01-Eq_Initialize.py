# -*- coding: utf-8 -*-
import os
import json
import webbrowser
import subprocess
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
        self.title("EqMax Discord連携 - 初期設定パッチ")
        self.geometry("580x920") # 高さを微調整
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- 3. タイトルエリア (ロゴ付き) ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax 初期設定パッチ", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))
        
        # --- 4. メインコンテンツ ---
        
        # 公式サイトボタン
        self.btn_web = ctk.CTkButton(
            self, 
            text="EqMax公式サイトを開く (DL・最新情報の確認)", 
            fg_color="#28a745",
            hover_color="#218838",
            text_color="white",
            font=("Yu Gothic", 12, "bold"),
            command=lambda: webbrowser.open("https://melanion.info/eqmax/")
        )
        self.btn_web.pack(pady=(10, 10))
        
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
        
        self.label_opt = ctk.CTkLabel(self.option_frame, text="2. セットアップオプション:", font=("Yu Gothic", 12, "bold"))
        self.label_opt.pack(pady=(10, 5), padx=20, anchor="w")

        self.var_tw_reset = ctk.BooleanVar(value=True)
        self.check_tw_reset = ctk.CTkCheckBox(self.option_frame, 
                                             text="Twitter(X)機能を現在使用していない\n(認証情報を初期化し、Discord専用として構成する)", 
                                             variable=self.var_tw_reset,
                                             font=("Yu Gothic", 11))
        self.check_tw_reset.pack(pady=10, padx=20, anchor="w")

        self.var_ini_base = ctk.BooleanVar(value=True)
        self.check_ini_base = ctk.CTkCheckBox(self.option_frame, 
                                             text="共通設定を適用 (EEWItems/連携有効化) ※解除不可", 
                                             variable=self.var_ini_base, state="disabled",
                                             font=("Yu Gothic", 11))
        self.check_ini_base.pack(pady=5, padx=20, anchor="w")

        self.var_cap = ctk.BooleanVar(value=True)
        self.check_cap = ctk.CTkCheckBox(self.option_frame, 
                                         text="自動キャプチャ・画像保存を有効化 ※解除不可", 
                                         variable=self.var_cap, state="disabled",
                                         font=("Yu Gothic", 11))
        self.check_cap.pack(pady=5, padx=20, anchor="w")

        self.var_check_count = ctk.BooleanVar(value=True)
        self.check_count = ctk.CTkCheckBox(self.option_frame, 
                                          text="通知の間引きを無効にする (全報通知)\n(※チェックなし：EqMax独自判定で通知を制限する)", 
                                          variable=self.var_check_count,
                                          font=("Yu Gothic", 11))
        self.check_count.pack(pady=10, padx=20, anchor="w")

        # 3. 表示例エリア
        self.example_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.example_frame.pack(pady=10, padx=20, fill="x")
        self.label_example_title = ctk.CTkLabel(self.example_frame, text="【Discord通知レイアウト例】", font=("Yu Gothic", 10, "bold"))
        self.label_example_title.pack(pady=(5, 0))
        
        example_text = (
            "緊急地震速報：第5報(終)予報\n"
            "震源地：奄美大島近海(28.0N 129.2E)\n"
            "マグニチュード：M3.8\n"
            "深さ：10km\n"
            "推定最大震度：3\n\n"
            "(ここに画像ファイルが添付されます)"
        )
        self.label_example = ctk.CTkLabel(self.example_frame, text=example_text, justify="left", font=("Consolas", 11) if os.name == 'nt' else ("monospace", 11))
        self.label_example.pack(pady=10, padx=10)

        # 実行ボタン
        self.btn_run = ctk.CTkButton(self, text="セットアップを実行", fg_color="#1f538d", hover_color="#14375e", height=60, 
                                     font=("Yu Gothic", 14, "bold"),
                                     command=self.run_patch, state="disabled")
        self.btn_run.pack(pady=10)

        # ログ表示
        self.log_view = ctk.CTkTextbox(self, width=500, height=120)
        self.log_view.pack(pady=10)

    # --- 以下、ロジック部分は変更なし ---

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.dirname(file_path))
            self.btn_run.configure(state="normal")

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n")
        self.log_view.see("end")

    def run_patch(self):
        path = self.entry_path.get().strip()
        exe_path = os.path.join(path, "EqMax.exe")
        ini_path = os.path.join(path, "EqMax.ini")

        if not path or not os.path.exists(exe_path):
            messagebox.showerror("エラー", "EqMax.exe が見つかりません。")
            return

        if not os.path.exists(ini_path):
            response = messagebox.askyesno(
                "初期設定が必要です", 
                "EqMax.ini が見つかりません。\n設定ファイルを作成するため、一度 EqMax を起動します。\n\n"
                "【手順】\n1. EqMaxが起動したら、そのまま「終了」させてください。\n"
                "2. 終了を確認後、自動的にパッチ処理を続行します。\n\n実行しますか？"
            )
            if response:
                try:
                    self.write_log("EqMax を起動しました。終了を待機しています...")
                    proc = subprocess.Popen([exe_path], cwd=path)
                    self.write_log(">>> EqMaxを終了（閉じ）してください...")
                    proc.wait() 
                    
                    if not os.path.exists(ini_path):
                        messagebox.showerror("エラー", "INIファイルが生成されませんでした。")
                        return
                    self.write_log("EqMax の終了を確認。設定ファイルの更新を開始します。")
                except Exception as e:
                    messagebox.showerror("エラー", f"EqMaxの起動に失敗しました: {e}")
                    return
            else:
                return

        try:
            self.write_log("プロセスをクリーンアップ中...")
            os.system('taskkill /F /IM EqMax.exe /T >nul 2>&1')
        except: pass

        try:
            with open(os.path.join(path, "Twitter.log"), 'wb') as f: pass
            self.write_log("Twitter.log を作成しました。")
        except Exception as e: self.write_log(f"ログ作成失敗: {e}")

        self.patch_ini_final(ini_path)
        
        if self.var_tw_reset.get():
            self.create_initial_json(path)
            self.write_log("Twitter認証情報を初期化しました。")
        
        messagebox.showinfo("完了", "セットアップが完了しました！\nこれで Discord 連携の準備がすべて整いました。")
        self.destroy()

    def patch_ini_final(self, ini_path):
        with open(ini_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        S = "\\t"
        items = ["", "[緊急地震速報：]", "報番号", "最終報", "警報", "<改行>", "[震源地：]", "震央名", "[(]", "緯度経度", "[)]", "<改行>", "[マグニチュード：M]", "マグニチュード", "<改行>", "[深さ：]", "深さ", "<改行>", "[推定最大震度：]", "最大震度", "<改行>", "<改行>", "画像"]
        eew_items_line = "EEWItems=" + S.join(items)

        updates = {
            "TwitterBotEnabled": "1", "EEWEnabled": "1", "Enable": "1", "v2": "1",
            "AppName": "EqMax_Discord", "AutoPost": "1", "UploadImage": "1", "AutoCapture": "1",
            "Format": "緊急地震速報：$Point$ $MaxShindo$ $Mag$ $Depth$",
            "CheckTweetCount": "1" if self.var_check_count.get() else "0"
        }

        if self.var_tw_reset.get():
            updates.update({
                "ConsumerKey": "", "ConsumerKeySecret": "", "AccessToken": "", "AccessTokenSecret": "",
                "ClientID": "dummy", "ClientSecret": "dummy", "RefreshToken": "dummy", "BearerToken": "dummy",
                "BearerObtainedAt": ""
            })

        new_lines = []
        applied_keys = set()
        for line in lines:
            line_s = line.strip()
            found = False
            if line_s.startswith("EEWItems="):
                new_lines.append(eew_items_line + "\n")
                applied_keys.add("EEWItems")
                found = True
            else:
                for k, v in updates.items():
                    if line_s.startswith(k + "="):
                        new_lines.append(f"{k}={v}\n")
                        applied_keys.add(k)
                        found = True
                        break
            if not found:
                new_lines.append(line if line.endswith('\n') else line + '\n')
        
        for k, v in updates.items():
            if k not in applied_keys: new_lines.append(f"{k}={v}\n")

        with open(ini_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.writelines(new_lines)
        self.write_log("EqMax.ini を更新しました。")

    def create_initial_json(self, path):
        json_path = os.path.join(path, "v2_Tokens.json")
        data = {
            "appname": "EqMax_Discord", "client_id": "dummy", "client_id_secret": "dummy", 
            "scopes": "tweet.read tweet.write users.read offline.access media.write", 
            "refresh_token": "dummy", "bearer_token": "dummy", 
            "bearer_token_obtained_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+09:00")
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    EqMaxSetupPatcher().mainloop()