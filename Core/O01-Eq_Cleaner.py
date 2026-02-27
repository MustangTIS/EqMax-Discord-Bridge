import os
import time
from tkinter import filedialog, messagebox
import customtkinter as ctk
import shutil

# 画像処理ライブラリのインポート
try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None

class EqMaxCleaner(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. アイコンと画像の設定 (統合ハブから移植) ---
        base_dir = os.path.dirname(__file__)
        # Assetsフォルダの場所を定義（Coreフォルダの一つ上にあるAssetsを指す）
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        # ウィンドウアイコンの設定
        if os.path.exists(icon_path):
            try:
                # 起動直後にアイコンをセット
                self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception as e:
                print(f"Icon Error: {e}")

        # ロゴ画像の読み込み
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
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("EqMax ログ・画像クリーナー")
        self.geometry("550x580") # ロゴ表示分、高さを少し確保

        # --- 3. タイトルエリア (ロゴ付き) ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax クリーナー", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # --- 4. コントロール群 ---
        # 1. フォルダ選択
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe を選択してください:")
        self.label_path.pack(pady=(10, 0))
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=350)
        self.entry_path.pack(side="left", padx=(0, 5))
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=80, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 2. クリーンアップオプション
        self.option_frame = ctk.CTkFrame(self)
        self.option_frame.pack(pady=20, padx=20, fill="x")

        self.var_logs = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="各種ログファイルをリセット (0KB化)\n(Debug, EEW, Error, Info, Twitter関連)", variable=self.var_logs).pack(pady=10, padx=20, anchor="w")

        self.var_tw_dir = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="Twitterフォルダ内の未送信データを削除", variable=self.var_tw_dir).pack(pady=10, padx=20, anchor="w")

        # 3. Captureフォルダ整理
        self.cap_label = ctk.CTkLabel(self, text="Captureフォルダの画像整理:")
        self.cap_label.pack(pady=(10, 0))
        self.cap_mode = ctk.StringVar(value="keep_7")
        self.cap_frame = ctk.CTkFrame(self)
        self.cap_frame.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkRadioButton(self.cap_frame, text="7日以上前を削除", variable=self.cap_mode, value="keep_7").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(self.cap_frame, text="30日以上前を削除", variable=self.cap_mode, value="keep_30").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(self.cap_frame, text="すべて削除", variable=self.cap_mode, value="all").pack(side="left", padx=20, pady=10)

        self.btn_run = ctk.CTkButton(self, text="クリーンアップを実行する", fg_color="darkred", height=60, command=self.run_clean)
        self.btn_run.pack(pady=30)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.dirname(file_path))

    def run_clean(self):
        path = self.entry_path.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("エラー", "EqMaxのフォルダを正しく選択してください。")
            return

        # EqMax.exe を強制終了
        try:
            os.system('taskkill /F /IM EqMax.exe /T >nul 2>&1')
        except Exception as e:
            print(f"プロセス終了中にエラー: {e}")

        summary = []
        # ログのリセット
        if self.var_logs.get():
            target_logs = [
                "Debug.log", "EEW.log", "EqMaxError.log", "EqMaxInfo.log", 
                "KMMonitor.log", "Tokens.log", "Twitter.log", "TwitterResponse.log"
            ]
            for log in target_logs:
                p = os.path.join(path, log)
                if os.path.exists(p):
                    try:
                        with open(p, "wb") as f: pass
                    except: pass
            summary.append("・ログファイルをリセットしました。")

        # Twitterフォルダ
        if self.var_tw_dir.get():
            tw_path = os.path.join(path, "Twitter")
            if os.path.isdir(tw_path):
                for f in os.listdir(tw_path):
                    try:
                        os.remove(os.path.join(tw_path, f))
                    except: pass
                summary.append("・Twitterフォルダを空にしました。")

        # Capture整理 (サブフォルダ対応版)
        cap_dir = os.path.join(path, "Capture")
        if os.path.isdir(cap_dir):
            mode = self.cap_mode.get()
            now = time.time()
            days = 7 if mode == "keep_7" else 30
            count = 0
            for f in os.listdir(cap_dir):
                f_path = os.path.join(cap_dir, f)
                try:
                    if mode == "all" or os.stat(f_path).st_mtime < now - (days * 86400):
                        if os.path.isdir(f_path):
                            shutil.rmtree(f_path) # フォルダなら中身ごと削除
                        else:
                            os.remove(f_path)    # ファイルなら削除
                        count += 1
                except:
                    pass
            summary.append(f"・画像を {count} 件削除しました。")

        messagebox.showinfo("完了", "\n".join(summary))

if __name__ == "__main__":
    EqMaxCleaner().mainloop()