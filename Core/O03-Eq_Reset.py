import os
import time
from tkinter import filedialog, messagebox
import customtkinter as ctk
import shutil
import winreg
from datetime import datetime
try:
    from PIL import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        Image = None

class EqMaxResetTool(ctk.CTk):
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
        self.title("EqMax 初期化・クリーンアップツール")
        self.geometry("600x720")
        ctk.set_appearance_mode("dark")

        # --- 3. タイトルエリア ---
        self.label_title = ctk.CTkLabel(
            self, 
            text=" EqMax 初期化ツール", 
            image=self.logo_image,
            compound="left", 
            font=("Yu Gothic", 24, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # --- 4. ロジック設定 ---
        self.keep_files = {"EqMax.exe", "EqMax_08082_TwitteeUpdate.pdf", "LiveCamList2.csv", "sk4d.dll", "WebView2Loader.dll"}
        self.keep_folder = "Sound"

        self.caution_frame = ctk.CTkFrame(self, fg_color="#331111", border_color="#D32F2F", border_width=2)
        self.caution_frame.pack(pady=10, padx=20, fill="x")
        
        caution_title = ctk.CTkLabel(self.caution_frame, text="【重要・免責事項】", font=("Yu Gothic", 14, "bold"), text_color="#FF4444")
        caution_title.pack(pady=(10, 5))
        
        c_txt = "本機能は不具合時の復旧用です。\nINI設定、Discordボット、監視設定が全て削除され、\n元に戻せません。実行による損害は自己責任となります。"
        self.label_caution = ctk.CTkLabel(self.caution_frame, text=c_txt, font=("Yu Gothic", 11), justify="left")
        self.label_caution.pack(pady=(0, 10), padx=15)

        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe があるフォルダを選択:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=400)
        self.entry_path.pack(side="left", padx=5)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="選択...", width=60, command=self.browse_file)
        self.btn_browse.pack(side="left")

        self.check_var = ctk.BooleanVar(value=False)
        self.check_agree = ctk.CTkCheckBox(self, text="免責事項に同意して初期化する", variable=self.check_var, command=self.toggle_button)
        self.check_agree.pack(pady=10)

        self.btn_run = ctk.CTkButton(self, text="クリーンアップを実行", fg_color="#D32F2F", hover_color="#B71C1C", height=50, command=self.run_reset, state="disabled")
        self.btn_run.pack(pady=10)

        self.log_view = ctk.CTkTextbox(self, width=550, height=200)
        self.log_view.pack(pady=10)

    # --- メソッド群 ---

    def toggle_button(self):
        state = "normal" if self.check_var.get() else "disabled"
        self.btn_run.configure(state=state)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EqMax.exe", "EqMax.exe")])
        if file_path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, os.path.dirname(file_path))

    def write_log(self, text):
        self.log_view.insert("end", f"{datetime.now().strftime('%H:%M:%S')} : {text}\n")
        self.log_view.see("end")

    def get_desktop_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desk_path, _ = winreg.QueryValueEx(key, "Desktop")
            return desk_path
        except:
            return os.path.join(os.environ["USERPROFILE"], "Desktop")

    def open_folders(self):
        """ショートカットがあると思われるフォルダを開く"""
        desk_path = self.get_desktop_path()
        startup_base = os.environ.get("APPDATA", "")
        startup_sub = r"Microsoft\Windows\Start Menu\Programs\Startup"
        startup_path = os.path.join(startup_base, startup_sub)

        opened = []
        if os.path.exists(desk_path):
            try:
                os.startfile(desk_path)
                opened.append("デスクトップ")
            except: pass

        if os.path.exists(startup_path):
            try:
                os.startfile(startup_path)
                opened.append("スタートアップ")
            except: pass
        
        if opened:
            self.write_log(f"{'と'.join(opened)}フォルダを開きました。")
            messagebox.showinfo("手動削除のお願い", 
                "ショートカット自体の自動削除はリスク回避のため行いません。\n\n"
                "デスクトップやスタートアップ内に不要なショートカットがある場合は、"
                "今開いたフォルダから手動で削除をお願いします。")

    def run_reset(self):
        """実行メインロジック"""
        target_dir = self.entry_path.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Select Folder.")
            return

        final_msg = "【警告】本当に実行しますか？\n全てのカスタム設定が完全に消去されます。"
        if not messagebox.askyesno("Final Warning", final_msg): return

        # EqMaxプロセス終了
        os.system('taskkill /F /IM EqMax.exe /T >nul 2>&1')
        
        # フォルダを開く案内
        self.open_folders()

        try:
            # 本体ファイルの削除
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                
                if item == self.keep_folder:
                    # Soundフォルダの中身だけ消す
                    for s_item in os.listdir(item_path):
                        s_path = os.path.join(item_path, s_item)
                        try:
                            if os.path.isfile(s_path): os.remove(s_path)
                            else: shutil.rmtree(s_path)
                        except: pass
                    self.write_log("Sound folder cleaned.")
                
                elif item not in self.keep_files:
                    # 特定のファイル以外は削除
                    try:
                        if os.path.isfile(item_path): os.remove(item_path)
                        else: shutil.rmtree(item_path)
                        self.write_log(f"Deleted: {item}")
                    except: pass
            
            messagebox.showinfo("Success", "本体側の初期化が完了しました。")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

if __name__ == "__main__":
    EqMaxResetTool().mainloop()