# O03-EEW-Test.py
import os
import json
import sys
import time
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
        
        # --- 1. パスと資産（Assets）の設定 ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # 構造が Core/O03-EEW-Test.py の場合、親にある Assets を参照
        self.assets_dir = os.path.normpath(os.path.join(self.base_dir, "..", "Assets"))
        
        icon_path = os.path.join(self.assets_dir, "eq-dis.ico")
        img_path = os.path.join(self.assets_dir, "eq-dis.png")

        # ウィンドウアイコンの設定
        if os.path.exists(icon_path):
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        # ロゴ画像の設定
        self.logo_image = None
        if Image is not None and os.path.exists(img_path):
            try:
                opened_img = Image.open(img_path)
                self.logo_image = ctk.CTkImage(
                    light_image=opened_img,
                    dark_image=opened_img,
                    size=(40, 40)
                )
            except: pass

        # --- 2. ウィンドウ基本設定 ---
        self.title("EqMax 総合テスト送信ユニット v2.1")
        self.geometry("600x920") # ロゴ追加に伴い高さを少し拡張
        ctk.set_appearance_mode("dark")

        # --- 3. GUI構築 ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # タイトル (ロゴ付き)
        self.label_title = ctk.CTkLabel(
            self.main_container, 
            text=" EqMax 総合テスト送信ユニット", 
            image=self.logo_image,
            compound="left",
            font=("Yu Gothic", 20, "bold")
        )
        self.label_title.pack(pady=20)

        # EqMax.exe パス設定
        path_frame = ctk.CTkFrame(self.main_container)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        self.label_path_hint = ctk.CTkLabel(path_frame, text="EqMax.exe を選択してください:", font=("Yu Gothic", 12))
        self.label_path_hint.pack(padx=10, pady=(5, 0), anchor="w")

        self.entry_exe_path = ctk.CTkEntry(path_frame, placeholder_text="C:\\EqMax\\EqMax.exe", width=350)
        self.entry_exe_path.pack(side="left", padx=10, pady=(0, 15))
        
        self.btn_browse = ctk.CTkButton(path_frame, text="選択", width=60, command=self.browse_exe)
        self.btn_browse.pack(side="left", padx=5, pady=(0, 15))

        # デフォルトパス
        if os.path.exists("C:\\EqMax\\EqMax.exe"):
            self.entry_exe_path.insert(0, "C:\\EqMax\\EqMax.exe")

        # 各セクション作成
        self.create_eew_section()
        self.create_fixed_section()
        self.create_tsunami_section()

    # --- 以下、ロジック部分は変更なし ---
    def create_eew_section(self):
        lbl = ctk.CTkLabel(self.main_container, text="── 緊急地震速報 (EEW) テスト ──", text_color="orange", font=("Yu Gothic", 13, "bold"))
        lbl.pack(pady=(20, 5))
        container = ctk.CTkFrame(self.main_container)
        container.pack(fill="x", padx=10, pady=5)
        self.epicenter_type = ctk.StringVar(value="内陸")
        seg = ctk.CTkSegmentedButton(container, values=["内陸", "海域"], variable=self.epicenter_type)
        seg.pack(pady=10)
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(pady=5)
        ctk.CTkLabel(inner, text="震度:").pack(side="left", padx=5)
        self.shindo_var = ctk.StringVar(value="4")
        ctk.CTkOptionMenu(inner, values=["1", "2", "3", "4", "5弱", "5強", "6弱", "6強", "7"], variable=self.shindo_var, width=80).pack(side="left", padx=5)
        ctk.CTkLabel(inner, text="M:").pack(side="left", padx=5)
        self.mag_var = ctk.StringVar(value="5.5")
        ctk.CTkEntry(inner, textvariable=self.mag_var, width=50).pack(side="left", padx=5)
        self.btn_eew = ctk.CTkButton(container, text="EEW送信 (Text形式/BOMなし)", command=self.send_eew_test, fg_color="#d35400")
        self.btn_eew.pack(pady=10)

    def create_fixed_section(self):
        lbl = ctk.CTkLabel(self.main_container, text="── 確定報 (震源・震度報) テスト ──", text_color="cyan", font=("Yu Gothic", 13, "bold"))
        lbl.pack(pady=(20, 5))
        container = ctk.CTkFrame(self.main_container)
        container.pack(fill="x", padx=10, pady=5)
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(pady=10)
        ctk.CTkLabel(inner, text="最大震度:").pack(side="left", padx=5)
        self.fixed_shindo_var = ctk.StringVar(value="3")
        ctk.CTkOptionMenu(inner, values=["1", "2", "3", "4", "5弱", "5強", "6弱", "6強", "7"], variable=self.fixed_shindo_var, width=80).pack(side="left", padx=5)
        self.btn_fixed = ctk.CTkButton(container, text="確定報送信 (JSON形式/BOM付き)", command=self.send_fixed_report_test, fg_color="#2980b9")
        self.btn_fixed.pack(pady=10)

    def create_tsunami_section(self):
        lbl = ctk.CTkLabel(self.main_container, text="── 津波情報 テスト ──", text_color="pink", font=("Yu Gothic", 13, "bold"))
        lbl.pack(pady=(20, 5))
        container = ctk.CTkFrame(self.main_container)
        container.pack(fill="x", padx=10, pady=5)
        self.tsunami_type_var = ctk.StringVar(value="津波予報")
        ctk.CTkOptionMenu(container, values=["津波予報", "津波注意報", "津波警報", "大津波警報"], variable=self.tsunami_type_var, width=200).pack(pady=10)
        self.btn_tsunami = ctk.CTkButton(container, text="津波情報送信 (JSON形式/BOM付き)", command=self.send_tsunami_test, fg_color="#c0392b")
        self.btn_tsunami.pack(pady=10)

    def browse_exe(self):
        file_path = filedialog.askopenfilename(
            title="EqMax.exeを選択してください",
            filetypes=[("Executable", "EqMax.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.entry_exe_path.delete(0, "end")
            self.entry_exe_path.insert(0, file_path)

    def _get_target_path(self):
        exe_path = self.entry_exe_path.get().strip()
        if not exe_path or not os.path.isfile(exe_path):
            messagebox.showerror("エラー", "EqMax.exeを正しく選択してください。")
            return None
        return os.path.dirname(exe_path)

    def _write_log(self, content, inject_bom=False):
        eq_dir = self._get_target_path()
        if not eq_dir: return
        log_file = os.path.join(eq_dir, "Twitter.log")
        try:
            mode = "ab"
            with open(log_file, mode) as f:
                if inject_bom:
                    f.write(b'\xef\xbb\xbf')
                f.write(content.encode("utf-8"))
        except Exception as e:
            messagebox.showerror("エラー", f"書き込み失敗: {e}")

    def _direct_write(self, content, inject_bom=False):
        self._write_log(content, inject_bom)

    def send_eew_test(self):
        eq_dir = self._get_target_path()
        if not eq_dir: return

        capture_dir = os.path.join(eq_dir, "Capture")
        os.makedirs(capture_dir, exist_ok=True)

        dummy_img_src = os.path.join(self.assets_dir, "dummy_eq.png")
        target_img_name = f"CapturedImage_test_{int(time.time())}.png"
        target_img_path = os.path.normpath(os.path.join(capture_dir, target_img_name))

        try:
            if os.path.exists(dummy_img_src):
                import shutil
                shutil.copy(dummy_img_src, target_img_path)
            else:
                with open(target_img_path, "wb") as f: pass
        except Exception as e:
            messagebox.showerror("エラー", f"画像配置失敗: {e}")
            return

        ts_log = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        ep_name = "十勝地方" if self.epicenter_type.get() == "内陸" else "十勝沖"
        shindo = self.shindo_var.get()
        mag = self.mag_var.get()
        
        payload = (
            f"緊急地震速報：第9報(最終報)\n"
            f"震源地：{ep_name}(42.3N 144.2E)\n"
            f"マグニチュード：M{mag}\n"
            f"深さ：20km\n"
            f"推定最大震度：{shindo}\n"
            f"{target_img_path}"
        )
        final_payload = f"\n{ts_log}-{payload}\n: \n"
        self._direct_write(final_payload, inject_bom=False)
        messagebox.showinfo("送信完了", "EEWテストを送信しました。")

    def send_fixed_report_test(self):
        eq_dir = self._get_target_path()
        if not eq_dir: return

        now = datetime.now()
        ts_iso = now.isoformat() + "+09:00"
        ts_file = now.strftime("%Y%m%d%H%M%S")
        
        json_dir = os.path.join(eq_dir, "Json", now.strftime("%Y"), now.strftime("%m"))
        os.makedirs(json_dir, exist_ok=True)
        
        filename = f"{ts_file}_{ts_file}_VXSE5k_1.json"
        json_file_path = os.path.join(json_dir, filename)

        shindo = self.fixed_shindo_var.get()
        
        data = {
            "Control": {
                "Title": "震源・震度に関する情報",
                "DateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Status": "通常",
                "EditorialOffice": "気象庁本庁",
                "PublishingOffice": "気象庁"
            },
            "Head": {
                "Title": "震源・震度情報",
                "ReportDateTime": ts_iso,
                "TargetDateTime": ts_iso,
                "EventID": ts_file,
                "InfoType": "発表",
                "Serial": "1",
                "InfoKind": "地震情報",
                "Headline": {"Text": f"{now.strftime('%d日%H時%M分')}ころ、地震がありました。"}
            },
            "Body": {
                "Earthquake": {
                    "OriginTime": ts_iso,
                    "ArrivalTime": ts_iso,
                    "Hypocenter": {
                        "Area": {
                            "Name": "十勝地方中部",
                            "Code": "182",
                            "Coordinate": "+42.9+143.2-10000/"
                        },
                        "Magnitude": "5.0"
                    }
                },
                "Intensity": {
                    "Observation": {
                        "MaxInt": shindo,
                        "Pref": [{
                            "Name": "北海道",
                            "Code": "01",
                            "MaxInt": shindo,
                            "Area": [{
                                "Name": "十勝地方中部",
                                "Code": "182",
                                "MaxInt": shindo,
                                "City": [{
                                    "Name": "帯広市",
                                    "Code": "0120700",
                                    "MaxInt": shindo
                                }]
                            }]
                        }]
                    }
                },
                "Comments": {
                    "ForecastComment": {"Text": "この地震による津波の心配はありません。"}
                }
            }
        }

        self._save_json_file(json_file_path, data, "確定報")

    def send_tsunami_test(self):
        eq_dir = self._get_target_path()
        if not eq_dir: return

        now = datetime.now()
        ts_iso = now.isoformat() + "+09:00"
        ts_file = now.strftime("%Y%m%d%H%M%S")
        
        json_dir = os.path.join(eq_dir, "Json", now.strftime("%Y"), now.strftime("%m"))
        os.makedirs(json_dir, exist_ok=True)
        
        filename = f"{ts_file}_{ts_file}_VTSE41_0.json"
        json_file_path = os.path.join(json_dir, filename)

        t_type = self.tsunami_type_var.get()
        msg_map = {
            "津波予報": "若干の海面変動が予想されますが、被害の心配はありません。",
            "津波注意報": "海岸から離れてください。",
            "津波警報": "ただちに避難してください！",
            "大津波警報": "巨大な津波が襲います！避難！！"
        }

        data = {
            "Control": {
                "Title": "津波警報・注意報・予報a",
                "DateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Status": "通常",
                "EditorialOffice": "気象庁本庁",
                "PublishingOffice": "気象庁"
            },
            "Head": {
                "Title": t_type,
                "ReportDateTime": ts_iso,
                "TargetDateTime": ts_iso,
                "EventID": ts_file,
                "InfoType": "発表",
                "Serial": "1",
                "InfoKind": "津波警報・注意報・予報",
                "Headline": {"Text": msg_map[t_type]}
            },
            "Body": {
                "Tsunami": {
                    "Forecast": {
                        "Item": [{
                            "Area": {
                                "Name": "北海道太平洋沿岸東部",
                                "Code": "101"
                            },
                            "Category": {
                                "Kind": {"Name": t_type, "Code": "50"},
                                "LastKind": {"Name": t_type, "Code": "50"}
                            },
                            "FirstHeight": {"Condition": "津波到達中と推測"},
                            "MaxHeight": {"DateTime": ts_iso, "Condition": "重要", "Height": "1.0"}
                        }]
                    }
                }
            }
        }

        self._save_json_file(json_file_path, data, "津波情報")

    def _save_json_file(self, path, data, label):
        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Success: {path}")
            messagebox.showinfo("成功", f"{label}ファイルを生成しました:\n{os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル生成失敗: {e}")
            
if __name__ == "__main__":
    EqMaxTestSender().mainloop()