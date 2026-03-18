import os
import json
import requests
import sys
import time
import shutil
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog

try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None

class EqMaxTestSender(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 1. アイコンと画像の設定 ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.normpath(os.path.join(self.base_dir, "..", "Assets"))
        
        icon_path = os.path.join(self.assets_dir, "eq-dis.ico")
        img_path = os.path.join(self.assets_dir, "eq-dis.png")

        # ウィンドウアイコン
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        # ロゴ画像の読み込み
        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                # 40x40程度のアイコンサイズ
                self.logo_image = ctk.CTkImage(light_image=opened_img, dark_image=opened_img, size=(40, 40))
            except: pass

        # ダミー画像のソースパス
        self.dummy_img_name = "dummy_eq.png"
        self.dummy_img_src = os.path.join(self.assets_dir, self.dummy_img_name)

        # UI設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("EqMAX Discord Bridge - 地震速報テスト投稿ツール")
        self.geometry("600x820")

        # --- UIレイアウト ---
        # ヘッダー部分 (アイコン + タイトル横並び)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")

        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_image, text="")
            self.logo_label.pack(side="left", padx=(0, 15))
            
        self.label_title = ctk.CTkLabel(
            self.header_frame, 
            text="地震速報テスト投稿ツール", 
            font=("Yu Gothic", 22, "bold")
        )
        self.label_title.pack(side="left")

        # 1. EqMax パス指定
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.path_frame, text="EqMaxの場所 (Twitter.logがあるフォルダ):", font=("Yu Gothic", 12, "bold")).pack(pady=(10, 0), padx=10, anchor="w")
        
        self.inner_path_frame = ctk.CTkFrame(self.path_frame, fg_color="transparent")
        self.inner_path_frame.pack(pady=5, padx=10, fill="x")
        self.entry_path = ctk.CTkEntry(self.inner_path_frame, placeholder_text="C:\\Program Files\\EqMax")
        self.entry_path.pack(side="left", padx=(0, 5), expand=True, fill="x")
        self.btn_browse = ctk.CTkButton(self.inner_path_frame, text="参照", width=60, command=self.browse_path)
        self.btn_browse.pack(side="left")

        # 2. 地震情報のパラメータ設定
        self.param_frame = ctk.CTkFrame(self)
        self.param_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.param_frame, text="地震情報のパラメータ設定", font=("Yu Gothic", 12, "bold")).pack(pady=10, padx=10, anchor="w")

        # 震源地
        self.epicenter_type = ctk.StringVar(value="内陸")
        self.ep_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        self.ep_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.ep_frame, text="震源種別:").pack(side="left", padx=5)
        # 修正: 第1引数を self.ep_frame に
        ctk.CTkRadioButton(self.ep_frame, text="内陸 (十勝地方)", variable=self.epicenter_type, value="内陸").pack(side="left", padx=10)
        ctk.CTkRadioButton(self.ep_frame, text="海域 (十勝沖)", variable=self.epicenter_type, value="海域").pack(side="left", padx=10)

        # 震度
        self.shindo_var = ctk.StringVar(value="5弱")
        self.sh_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        self.sh_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.sh_frame, text="予想震度:").pack(side="left", padx=5)
        shindo_options = ["1", "2", "3", "4", "5弱", "5強", "6弱", "6強", "7"]
        self.shindo_menu = ctk.CTkOptionMenu(self.sh_frame, values=shindo_options, variable=self.shindo_var, width=100)
        self.shindo_menu.pack(side="left", padx=10)

        # マグニチュード
        self.mag_var = ctk.StringVar(value="6.5")
        self.mag_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        self.mag_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.mag_frame, text="規模(M):").pack(side="left", padx=5)
        self.entry_mag = ctk.CTkEntry(self.mag_frame, textvariable=self.mag_var, width=60)
        self.entry_mag.pack(side="left", padx=10)
        
        # 報数
        self.report_num = ctk.StringVar(value="最終報")
        self.rep_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent")
        self.rep_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.rep_frame, text="報数種別:").pack(side="left", padx=5)
        # 修正: 第1引数を self.rep_frame に
        ctk.CTkRadioButton(self.rep_frame, text="第1報", variable=self.report_num, value="第1報").pack(side="left", padx=10)
        ctk.CTkRadioButton(self.rep_frame, text="最終報", variable=self.report_num, value="最終報").pack(side="left", padx=10)

        # 3. ログ表示
        self.log_text = ctk.CTkTextbox(self, height=180)
        self.log_text.pack(pady=10, padx=20, fill="x")

        # 実行ボタン
        self.btn_run = ctk.CTkButton(self, text="擬似地震発生 (Twitter.log追記)", font=("Yu Gothic", 16, "bold"), height=60, fg_color="#d35400", hover_color="#e67e22", command=self.run_log_test)
        self.btn_run.pack(pady=20)

    def browse_path(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.dirname(file_path))

    def write_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def run_log_test(self):
        eq_path = self.entry_path.get().strip()
        if not eq_path or not os.path.isdir(eq_path):
            messagebox.showerror("エラー", "EqMaxのフォルダを正しく選択してください。")
            return

        # 1. 画像の準備
        capture_dir = os.path.join(eq_path, "Capture")
        os.makedirs(capture_dir, exist_ok=True)
        
        target_img_name = f"CapturedImage_test_{int(time.time())}.png"
        target_img_path = os.path.normpath(os.path.join(capture_dir, target_img_name))
        
        try:
            if os.path.exists(self.dummy_img_src):
                shutil.copy(self.dummy_img_src, target_img_path)
            else:
                with open(target_img_path, "wb") as f: pass
        except Exception as e:
            self.write_log(f"Error: 画像配置失敗: {e}")
            return

        # 2. ログブロックの生成
        now_dt = datetime.now()
        ts = now_dt.strftime("%Y/%m/%d %H:%M:%S")
        
        ep_type = self.epicenter_type.get()
        shindo = self.shindo_var.get()
        mag = self.mag_var.get()
        rep = self.report_num.get()
        
        ep_name = "十勝地方" if ep_type == "内陸" else "十勝沖"
        coords = "(42.3N 144.2E)"
        rep_text = f"{rep}(終)予報" if rep == "最終報" else f"{rep}予報"

        log_lines = [
            f"{ts}-TTwitterBot2.PostTweet: because of TwitterDummyPost, exit !",
            f"{ts}-TTwitterForm.CheckEEWCondition: true",
            f"{ts}-緊急地震速報：{rep_text}",
            f"震源地：{ep_name}{coords}",
            f"マグニチュード：M{mag}",
            "深さ：20km",
            f"推定最大震度：{shindo}",
            f"{target_img_path}",
            ": "
        ]
        
        log_block_text = "\n".join(log_lines) + "\n"

        # 3. 書き込み
        log_file = os.path.join(eq_path, "Twitter.log")
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_block_text)
                f.flush()
                os.fsync(f.fileno())
            
            self.write_log("Twitter.log に擬似ブロックを追記しました。")
            self.write_log(f"内容: {ep_name} / {rep_text} / 震度{shindo}")
            messagebox.showinfo("成功", "実ログ形式で書き込みました。\nボットの反応を確認してください。")
        except Exception as e:
            self.write_log(f"Error: 書き込み失敗: {e}")

if __name__ == "__main__":
    app = EqMaxTestSender()
    app.mainloop()