import customtkinter as ctk
import os
import subprocess
import sys
import requests
import webbrowser
from datetime import datetime # 時刻表示用に追加
from tkinter import messagebox

try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None
        
class EqMAXTopHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 0. バージョン定義 ---
        self.CURRENT_VERSION = "v7.0.2" 
        self.REPO_URL = "MustangTIS/EqMax-Discord-Bridge"
        
        # --- 1. アイコンと画像の設定 ---
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
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
        self.title(f"EqMAX Discord Bridge {self.CURRENT_VERSION} - 統合管理ハブ")
        self.geometry("650x850")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # プロンプトへの起動通知
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running EqMax-Discord-Bridge {self.CURRENT_VERSION}")

        # --- 3. タイトルエリア ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMAX Discord Bridge", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(30, 5))

        self.label_ver = ctk.CTkLabel(self, text=f"Version {self.CURRENT_VERSION.replace('v','')}", font=("Yu Gothic", 12))
        self.label_ver.pack(pady=(0, 5))

        # 更新通知ボタン（GitHub API連動）
        self.update_label = ctk.CTkButton(
            self, text="", fg_color="transparent", text_color="#3b8ed0", 
            hover_color="#2b2b2b", font=("Yu Gothic", 11, "underline"),
            command=self.open_release_page
        )
        self.update_url = ""

        # --- 4. メインメニューエリア ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # 【メインプロセス】
        ctk.CTkLabel(self.btn_frame, text="▼ 推奨セットアップ手順", font=("Yu Gothic", 12, "bold"), text_color="#3b8ed0").pack(anchor="w", padx=10)
        self.create_menu_button("1. EqMAX 初期設定", "01-Eq_Initialize.py", "EEWレイアウト・キャプチャ・疑似認証を自動適用します")
        self.create_menu_button("2. Discord 連携実装", "02-Eq_Discord.py", "Webhook URLを登録し、通知システムを完成させます")

        # 【トラブルシューティング】
        ctk.CTkLabel(self.btn_frame, text="▼ 困った時は...", font=("Yu Gothic", 12, "bold"), text_color="#e74c3c").pack(anchor="w", padx=10, pady=(20, 0))
        self.create_menu_button("3. EqMAX初期化処理", "03-Eq_Reset.py", "注意：すべての設定をインストール直後の状態に戻します", fg="#c0392b") 

        # 【おまけ機能】
        ctk.CTkLabel(self.btn_frame, text="▼ メンテナンス・補助ツール", font=("Yu Gothic", 12, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=(20, 0))
        self.create_menu_button("おまけ1. ログ・画像掃除", "O01-Eq_Cleaner.py", "溜まった不要な画像やログを一括削除", height=40, fg="#444444")
        self.create_menu_button("おまけ2. EqMAX安定化", "O02-Eq_Watch.py", "メモリリーク対策用ウォッチドッグの起動", height=40, fg="#444444")

        # 足跡
        self.label_footer = ctk.CTkLabel(self, text="© 2026 Mustang_TIS", font=("Yu Gothic", 10), text_color="gray")
        self.label_footer.pack(pady=10)

        # 起動時に更新チェックを実行
        self.after(1000, self.check_for_updates)

    def create_menu_button(self, text, script_name, info, state="normal", fg=None, height=50):
        btn = ctk.CTkButton(
            self.btn_frame, 
            text=text, 
            height=height,
            state=state,
            fg_color=fg if fg else "#1f538d",
            command=lambda: self.launch_script(script_name)
        )
        btn.pack(fill="x", pady=5)
        
        lbl = ctk.CTkLabel(self.btn_frame, text=info, font=("Yu Gothic", 12), text_color="gray70")
        lbl.pack(pady=(0, 10))

    def launch_script(self, script_name):
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        # --- プロンプト用ログ出力強化 ---
        print("-" * 50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching: {script_name}")
        
        if os.path.exists(script_path):
            try:
                print(f"[Status] : Found script. Starting process...")
                subprocess.Popen([sys.executable, script_path])
                print(f"[Info]   : Process for {script_name} has been detached.")
            except Exception as e:
                print(f"[Error]  : Failed to start process: {e}")
        else:
            print(f"[Error]  : {script_name} NOT FOUND.")
            messagebox.showerror("Error", f"{script_name} が見つかりません。")
        
        print("-" * 50)

    def check_for_updates(self):
        api_url = f"https://api.github.com/repos/{self.REPO_URL}/releases/latest"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for updates from GitHub...")
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name")
                if latest_tag and latest_tag != self.CURRENT_VERSION:
                    print(f"[Update] : New version found ({latest_tag})")
                    self.update_url = data.get("html_url")
                    self.update_label.configure(text=f"🚀 新バージョン {latest_tag} が公開されています")
                    self.update_label.pack(pady=5)
                else:
                    print(f"[Update] : You are using the latest version.")
        except Exception as e:
            print(f"[Update] : Failed to check updates. ({e})")

    def open_release_page(self):
        if self.update_url:
            webbrowser.open(self.update_url)

if __name__ == "__main__":
    app = EqMAXTopHub()
    app.mainloop()