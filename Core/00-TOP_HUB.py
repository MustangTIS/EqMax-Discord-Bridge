import customtkinter as ctk
import os
import subprocess
import sys
import requests
import webbrowser
from datetime import datetime
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
        self.CURRENT_VERSION = "v9.0.0" 
        self.REPO_URL = "MustangTIS/EqMax-Discord-Bridge"
        self.update_url = f"https://github.com/{self.REPO_URL}/releases/latest"
        
        # --- 1. アイコンと画像の設定 ---
        self.base_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.normpath(os.path.join(self.base_dir, "..", "Assets"))
        self.manual_path = os.path.normpath(os.path.join(self.base_dir, "..", "Manual", "Index.html"))
        
        icon_path = os.path.join(self.assets_dir, "eq-dis.ico")
        img_path = os.path.join(self.assets_dir, "eq-dis.png")

        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(light_image=opened_img, dark_image=opened_img, size=(50, 50))
            except: pass

        # UI設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title(f"EqMAX Discord Bridge - {self.CURRENT_VERSION}")
        self.geometry("700x650")
        self.resizable(False, False)

        # --- 2. ヘッダー (ロゴ + タイトル + 更新/GitHubリンク) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10), padx=30, fill="x")
        
        # 左側: ロゴとタイトル
        self.title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_box.pack(side="left")
        
        if self.logo_image:
            ctk.CTkLabel(self.title_box, image=self.logo_image, text="").pack(side="left", padx=(0, 15))
        
        self.title_text_box = ctk.CTkFrame(self.title_box, fg_color="transparent")
        self.title_text_box.pack(side="left")
        ctk.CTkLabel(self.title_text_box, text="EqMAX Discord Bridge", font=("Yu Gothic", 24, "bold")).pack(anchor="w")
        self.version_label = ctk.CTkLabel(self.title_text_box, text=f"© 2026 Mustang_TIS \n System Version: {self.CURRENT_VERSION} ", font=("Yu Gothic", 12))
        self.version_label.pack(anchor="w")

        # 右側: 更新通知とGitHubリンク
        self.info_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.info_box.pack(side="right")
        
        self.update_btn = ctk.CTkButton(
            self.info_box, text="🔄 アップデート確認中...", font=("Yu Gothic", 11),
            fg_color="#34495e", width=160, height=28, command=self.open_release_page
        )
        self.update_btn.pack(pady=2)
        
        self.github_btn = ctk.CTkButton(
            self.info_box, text="🌐 GitHubへ (Readme)", font=("Yu Gothic", 11),
            fg_color="#2c3e50", hover_color="#34495e", width=160, height=28,
            command=lambda: webbrowser.open(f"https://github.com/{self.REPO_URL}")
        )
        self.github_btn.pack(pady=2)

        # --- 3. メインコンテンツ (左右2列) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=30, pady=10)

        # --- 左列: セットアップ系 ---
        self.left_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_col.pack(side="left", expand=True, fill="both", padx=(0, 10))

        # セクション: 基本設定
        self.setup_group = ctk.CTkFrame(self.left_col)
        self.setup_group.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.setup_group, text="📊 初期設定・連携", font=("Yu Gothic", 14, "bold")).pack(pady=10)
        
        self.create_main_button(self.setup_group, "01. EqMax 初期設定ツール", "01-Eq_Initialize.py", "#2980b9", "#3498db").pack(pady=10, padx=20, fill="x")
        self.create_main_button(self.setup_group, "02. Discord 連携実装", "02-Eq_Discord.py", "#2c3e50", "#34495e").pack(pady=10, padx=20, fill="x")

        # --- 右列: メンテナンス系 (2x2 Grid) ---
        self.right_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_col.pack(side="left", expand=True, fill="both", padx=(10, 0))

        self.maint_group = ctk.CTkFrame(self.right_col)
        self.maint_group.pack(fill="both", expand=True)
        ctk.CTkLabel(self.maint_group, text="🛠️ メンテナンス補助", font=("Yu Gothic", 14, "bold")).pack(pady=10)
        
        # Gridレイアウト用フレーム
        self.grid_frame = ctk.CTkFrame(self.maint_group, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.grid_frame.columnconfigure((0, 1), weight=1)
        
        # メンテナンスボタン群 (2x2)
        # 1-1: ログ掃除
        self.create_grid_button(self.grid_frame, "🧹 ログ・画像クリーナー\n(Cleaner)", "O01-Eq_Cleaner.py", 0, 0)
        # 1-2: 安定化
        self.create_grid_button(self.grid_frame, "🛡️ 安定化監視\n(Watch)", "O02-Eq_Watch.py", 0, 1)
        # 2-1: テスト投稿
        self.create_grid_button(self.grid_frame, "📢 テスト投稿\n(EEW-Test)", "O03-EEW-Test.py", 1, 0, color="#d35400")
        # 2-2: オフラインマニュアル (Manual/Index.html)
        self.create_grid_button(self.grid_frame, "📖 ヘルプ\n(Manual)", "OFFLINE_MANUAL", 1, 1, color="#27ae60")

        # --- 4. 下部: 特殊操作 ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=30, pady=(0, 20))
        
        self.reset_btn = ctk.CTkButton(
            self.footer_frame, text="⚠️ システムリセット (全設定初期化)", 
            font=("Yu Gothic", 12), fg_color="#c0392b", hover_color="#e74c3c",
            command=lambda: self.launch_script("99-Eq_Reset.py")
        )
        self.reset_btn.pack(side="right")

        # 初回アップデートチェック
        self.after(1000, self.check_for_updates)

    def create_main_button(self, master, text, script, color, hover):
        return ctk.CTkButton(
            master, text=text, font=("Yu Gothic", 15, "bold"),
            height=60, fg_color=color, hover_color=hover,
            command=lambda: self.launch_script(script)
        )

    def create_grid_button(self, master, text, action, row, col, color="#2c3e50"):
        btn = ctk.CTkButton(
            master, text=text, font=("Yu Gothic", 12),
            height=80, fg_color=color,
            command=lambda: self.handle_action(action)
        )
        btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        return btn

    def handle_action(self, action):
        if action == "OFFLINE_MANUAL":
            if os.path.exists(self.manual_path):
                # file:/// 形式でブラウザで開く
                webbrowser.open(f"file:///{self.manual_path.replace('\\', '/')}")
            else:
                messagebox.showerror("Error", f"マニュアルが見つかりません:\n{self.manual_path}")
        else:
            self.launch_script(action)

    def launch_script(self, script_name):
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        print("-" * 50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching: {script_name}")
        if os.path.exists(script_path):
            try:
                subprocess.Popen([sys.executable, script_path])
                print(f"[Info]   : Process for {script_name} has been detached.")
            except Exception as e:
                print(f"[Error]  : Failed to start process: {e}")
        else:
            print(f"[Error]  : {script_name} NOT FOUND.")
            messagebox.showerror("Error", f"{script_name} が見つかりません。")
        print("-" * 50)

    def open_release_page(self):
        webbrowser.open(self.update_url)

    def check_for_updates(self):
        api_url = f"https://api.github.com/repos/{self.REPO_URL}/releases/latest"
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name")
                if latest_tag and latest_tag != self.CURRENT_VERSION:
                    self.update_btn.configure(
                        text=f"🚀 新版 {latest_tag} が利用可能",
                        fg_color="#e67e22", hover_color="#d35400"
                    )
                else:
                    self.update_btn.configure(text="✅ 最新バージョンです")
            else:
                self.update_btn.configure(text="❌ 更新確認失敗")
        except:
            self.update_btn.configure(text="⚠️ 接続エラー")

if __name__ == "__main__":
    app = EqMAXTopHub()
    app.mainloop()