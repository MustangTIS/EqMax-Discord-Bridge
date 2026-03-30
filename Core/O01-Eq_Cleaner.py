import os
import time
from tkinter import filedialog, messagebox
import tkinter as tk
import customtkinter as ctk
import shutil

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

        # --- 1. アイコンと画像の設定 (Assetsフォルダから読み込み) ---
        base_dir = os.path.dirname(__file__)
        # 構造が Core/O01-Eq_Cleaner.py の場合、親の親にある Assets を参照
        assets_dir = os.path.normpath(os.path.join(base_dir, "..", "Assets"))
        
        icon_path = os.path.join(assets_dir, "eq-dis.ico")
        img_path = os.path.join(assets_dir, "eq-dis.png")

        # ウィンドウアイコンの設定
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except Exception as e:
                print(f"Icon Error: {e}")

        # ロゴ画像の設定
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
        self.title("EqMax 環境クリーンアップツール v2.5")
        self.geometry("600x850") # ロゴ追加分、少し高さを調整
        ctk.set_appearance_mode("dark")

        # --- 3. タイトルエリア (ロゴ付き) ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax 環境クリーンアップ", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # --- パス設定 ---
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=20, pady=10)
        self.label_hint = ctk.CTkLabel(path_frame, text="EqMax.exe を選択してください:", font=("Yu Gothic", 12))
        self.label_hint.pack(padx=10, anchor="w")
        self.entry_exe_path = ctk.CTkEntry(path_frame, placeholder_text="EqMax.exeを選択", width=350)
        self.entry_exe_path.pack(side="left", padx=10, pady=(0, 15))
        self.btn_browse = ctk.CTkButton(path_frame, text="選択", width=60, command=self.browse_exe)
        self.btn_browse.pack(side="left", padx=5, pady=(0, 15))

        # デフォルトパス（存在確認付き）
        default_path = "C:\\EqMax\\EqMax.exe"
        if os.path.exists(default_path):
            self.entry_exe_path.insert(0, default_path)

        # --- オプション設定 ---
        self.option_frame = ctk.CTkScrollableFrame(self)
        self.option_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.option_frame, text="[クリーンアップ項目（確実に消して良いもののみ）]", font=("Yu Gothic", 12, "bold"), text_color="cyan").pack(pady=(10, 5), padx=20, anchor="w")
        
        self.var_log_clean = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="各種ログ(*.log)を削除する", variable=self.var_log_clean).pack(pady=5, padx=40, anchor="w")

        self.var_trash_dir = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.option_frame, text="Debug / LiveImages / Twitter フォルダを削除", variable=self.var_trash_dir).pack(pady=5, padx=40, anchor="w")

        self.var_json_dir = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.option_frame, text="Json (地震情報の履歴) フォルダを削除", variable=self.var_json_dir).pack(pady=5, padx=40, anchor="w")

        ctk.CTkLabel(self.option_frame, text="[Captureフォルダの整理]", font=("Yu Gothic", 12, "bold"), text_color="cyan").pack(pady=(15, 5), padx=20, anchor="w")
        self.cap_mode = ctk.StringVar(value="keep_30")
        ctk.CTkRadioButton(self.option_frame, text="30日以上前の古い画像だけ削除", variable=self.cap_mode, value="keep_30").pack(pady=2, padx=40, anchor="w")
        ctk.CTkRadioButton(self.option_frame, text="7日以上前の古い画像だけ削除", variable=self.cap_mode, value="keep_7").pack(pady=2, padx=40, anchor="w")
        ctk.CTkRadioButton(self.option_frame, text="すべて削除 (全消去)", variable=self.cap_mode, value="all").pack(pady=2, padx=40, anchor="w")

        ctk.CTkLabel(self.option_frame, text="※上記以外のファイルやフォルダには一切触れません。", text_color="orange").pack(pady=20)

        self.btn_run = ctk.CTkButton(self, text="クリーンアップを実行する", fg_color="darkred", hover_color="red", height=60, font=("Yu Gothic", 16, "bold"), command=self.run_clean)
        self.btn_run.pack(pady=30, padx=20, fill="x")

    def browse_exe(self):
        file_path = filedialog.askopenfilename(title="EqMax.exeを選択", filetypes=[("EqMax.exe", "EqMax.exe"), ("All Files", "*.*")])
        if file_path:
            self.entry_exe_path.delete(0, "end")
            self.entry_exe_path.insert(0, file_path)

    def run_clean(self):
        exe_path = self.entry_exe_path.get().strip()
        if not exe_path or not os.path.isfile(exe_path):
            messagebox.showerror("エラー", "EqMax.exeを正しく選択してください。")
            return

        path = os.path.dirname(exe_path)
        if not messagebox.askyesno("確認", "指定した項目のみ削除します。よろしいですか？"):
            return

        summary = []
        trash_dir_names = ["Debug", "LiveImages", "Twitter"]

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    if item in trash_dir_names and self.var_trash_dir.get():
                        shutil.rmtree(item_path)
                        summary.append(f"・{item} フォルダを削除しました。")
                    elif item == "Json" and self.var_json_dir.get():
                        shutil.rmtree(item_path)
                        summary.append("・Json フォルダを削除しました。")
                    elif item == "Capture":
                        mode = self.cap_mode.get()
                        now = time.time()
                        days = 30 if mode == "keep_30" else 7
                        c_count = 0
                        for f in os.listdir(item_path):
                            f_p = os.path.join(item_path, f)
                            if mode == "all" or os.stat(f_p).st_mtime < now - (days * 86400):
                                if os.path.isdir(f_p): shutil.rmtree(f_p)
                                else: os.remove(f_p)
                                c_count += 1
                        if c_count > 0:
                            summary.append(f"・Captureフォルダ内を整理しました。")
                else:
                    if item.lower().endswith(".log") and self.var_log_clean.get():
                        os.remove(item_path)

            if not summary:
                summary.append("・削除対象の項目は見つかりませんでした。")
            else:
                summary.append("・ログファイルを一掃しました。")

            messagebox.showinfo("完了", "\n".join(summary))
        except Exception as e:
            messagebox.showerror("エラー", f"失敗: {e}")

if __name__ == "__main__":
    EqMaxCleaner().mainloop()