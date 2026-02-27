import customtkinter as ctk
import os
import subprocess
import sys
try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        # それでもダメなら、Pillowなしで動くようにセーフティをかける
        Image = None
        
class EqMAXTopHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 1. アイコンと画像の設定 ---
        base_dir = os.path.dirname(__file__)
        # Assetsフォルダの場所を定義（Coreフォルダの一つ上にあるAssetsを指す）
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        # アイコンの設定
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception as e:
                print(f"Icon Error: {e}")

        # 画像の読み込み（ガード付き）
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
        else:
            self.logo_image = None

        # --- 2. ウィンドウ基本設定 ---
        self.title("EqMAX Discord Bridge v4 - 統合管理ハブ")
        self.geometry("650x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- 3. タイトルエリア (画像付き) ---
        # ※古い self.label_title = ... の記述は削除してここだけにします
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMAX Discord Bridge", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(30, 5))

        self.label_ver = ctk.CTkLabel(self, text="Version 4.6", font=("Yu Gothic", 12))
        self.label_ver.pack(pady=(0, 20))

        # --- 4. ボタンエリア ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(expand=True, fill="both", padx=40, pady=20)

        self.create_menu_button("1. EqMAX 初期設定", "01-Eq_Initialize.py", "EqMAXのEEW通知をDiscordに受け渡す下準備(疑似X(Twitter)ボット化含む)")
        self.create_menu_button("2. Discord 連携実装", "02-Eq_Discord.py", "EqMAXのボットをWebhookに送信するシステムを実装")
        self.create_menu_button("3. EqMAX初期化処理", "03-Eq_Reset.py", "EqMAX及びボットの不具合発生時に初期設定時に戻す") 
        self.create_menu_button("おまけ1. ログ・画像クリーナー", "O01-Eq_Cleaner.py", "EqMaxの長期使用で溜まった不要なファイルを掃除")
        self.create_menu_button("おまけ2. EqMAX安定化スクリプト", "O02-Eq_Watch.py", "EqMAXのメモリリーク問題に焦点をおいた安定化ボット") 

        # 足跡
        self.label_footer = ctk.CTkLabel(self, text="© 2026 Mustang_TIS", font=("Yu Gothic", 10), text_color="gray")
        self.label_footer.pack(pady=10)

    def create_menu_button(self, text, script_name, info, state="normal"):
        btn = ctk.CTkButton(
            self.btn_frame, 
            text=text, 
            height=50,
            state=state,
            command=lambda: self.launch_script(script_name)
        )
        btn.pack(fill="x", pady=5)
        
        lbl = ctk.CTkLabel(self.btn_frame, text=info, font=("Yu Gothic", 14), text_color="gray70")
        lbl.pack(pady=(0, 10))

    def launch_script(self, script_name):
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
        else:
            print(f"Error: {script_name} が見つかりません。")

if __name__ == "__main__":
    app = EqMAXTopHub()
    app.mainloop()