import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import winreg
from datetime import datetime

class EqMaxResetTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        # タイトル: EqMax 初期化・クリーンアップツール
        self.title("EqMax \u521d\u671f\u5316\u30fb\u30af\u30ea\u30fc\u30f3\u30a2\u30c3\u30d7\u30c4\u30fc\u30eb")
        self.geometry("600x650")
        ctk.set_appearance_mode("dark")

        self.keep_files = {"EqMax.exe", "EqMax_08082_TwitteeUpdate.pdf", "LiveCamList2.csv", "sk4d.dll", "WebView2Loader.dll"}
        self.keep_folder = "Sound"

        # --- 免責事項エリア ---
        self.caution_frame = ctk.CTkFrame(self, fg_color="#331111", border_color="#D32F2F", border_width=2)
        self.caution_frame.pack(pady=20, padx=20, fill="x")
        
        # 【重要・免責事項】
        caution_title = ctk.CTkLabel(self.caution_frame, text="\u3010\u91cd\u8981\u30fb\u514d\u8cac\u4e8b\u9805\u3011", font=("Yu Gothic", 14, "bold"), text_color="#FF4444")
        caution_title.pack(pady=(10, 5))
        
        # 免責本文
        c_txt = "\u672c\u6a5f\u80fd\u306f\u4e0d\u5177\u5408\u6642\u306e\u5fa9\u65e7\u7528\u3067\u3059\u3002\n\u0049\u004e\u0049\u8a2d\u5b9a\u3001\u0044\u0069\u0073\u0063\u006f\u0072\u0064\u30dc\u30c3\u30c8\u3001\u76e3\u8996\u8a2d\u5b9a\u304c\u5168\u3066\u524a\u9664\u3055\u308c\u3001\n\u5143\u306b\u623b\u305b\u307e\u305b\u3093\u3002\u5b9f\u884c\u306b\u3088\u308b\u640d\u5bb3\u306f\u81ea\u5df1\u8cac\u4efb\u3068\u306a\u308a\u307e\u3059\u3002"
        self.label_caution = ctk.CTkLabel(self.caution_frame, text=c_txt, font=("Yu Gothic", 11), justify="left")
        self.label_caution.pack(pady=(0, 10), padx=15)

        # パス選択
        self.label_path = ctk.CTkLabel(self, text="1. EqMax.exe \u304c\u3042\u308b\u30d5\u30a9\u30eb\u30c0\u3092\u9078\u629e:", font=("Yu Gothic", 12, "bold"))
        self.label_path.pack(pady=(10, 0))
        
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=5)
        self.entry_path = ctk.CTkEntry(self.path_frame, width=400)
        self.entry_path.pack(side="left", padx=5)
        self.btn_browse = ctk.CTkButton(self.path_frame, text="\u9078\u629e...", width=60, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # 同意チェック
        self.check_var = ctk.BooleanVar(value=False)
        self.check_agree = ctk.CTkCheckBox(self, text="\u514d\u8cac\u4e8b\u9805\u306b\u540c\u610f\u3057\u3066\u521d\u671f\u5316\u3059\u308b", variable=self.check_var, command=self.toggle_button)
        self.check_agree.pack(pady=10)

        self.btn_run = ctk.CTkButton(self, text="\u30af\u30ea\u30fc\u30f3\u30a2\u30c3\u30d7\u3092\u5b9f\u884c", fg_color="#D32F2F", hover_color="#B71C1C", height=50, command=self.run_reset, state="disabled")
        self.btn_run.pack(pady=10)

        self.log_view = ctk.CTkTextbox(self, width=550, height=200)
        self.log_view.pack(pady=10)

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

    def remove_shortcuts(self):
        shortcut_names = ["EqMax-DiscordBot.lnk", "EqMax-Watchdog.lnk"]
        desk_path = self.get_desktop_path()
        # スタートアップのパスを安全に結合
        startup_base = os.environ.get("APPDATA", "")
        startup_sub = r"Microsoft\Windows\Start Menu\Programs\Startup"
        startup_path = os.path.join(startup_base, startup_sub)

        for name in shortcut_names:
            for folder in [desk_path, startup_path]:
                path = os.path.join(folder, name)
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        self.write_log(f"Removed: {name}")
                    except: pass

    def run_reset(self):
        target_dir = self.entry_path.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Select Folder.")
            return

        # 【警告】本当に実行しますか？ 全てのカスタム設定が完全に消去されます。
        final_msg = "\u3010\u8b66\u544a\u3011\u672c\u5f53\u306b\u5b9f\u884c\u3057\u307e\u3059\u304b\uff1f\n\u5168\u3066\u306e\u30ab\u30b3\u30bf\u30e0\u8a2d\u5b9a\u304c\u5b8c\u5168\u306b\u6d88\u53bb\u3055\u308c\u307e\u3059\u3002"
        if not messagebox.askyesno("Final Warning", final_msg): return

        os.system('taskkill /F /IM EqMax.exe /T >nul 2>&1')
        self.remove_shortcuts()

        try:
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if item == self.keep_folder:
                    for s_item in os.listdir(item_path):
                        s_path = os.path.join(item_path, s_item)
                        try:
                            if os.path.isfile(s_path): os.remove(s_path)
                            else: shutil.rmtree(s_path)
                        except: pass
                    self.write_log("Sound folder cleaned.")
                elif item not in self.keep_files:
                    try:
                        if os.path.isfile(item_path): os.remove(item_path)
                        else: shutil.rmtree(item_path)
                        self.write_log(f"Deleted: {item}")
                    except: pass
            
            messagebox.showinfo("Success", "\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

if __name__ == "__main__":
    EqMaxResetTool().mainloop()