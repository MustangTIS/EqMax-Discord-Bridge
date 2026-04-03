# log_monitor.py
import os
import time

class LogMonitor:
    def __init__(self, log_path):
        self.log_path = log_path
        self.last_size = os.path.getsize(log_path) if os.path.exists(log_path) else 0
        self.pending_block = ""

    def check_new_logs(self):
        if not os.path.exists(self.log_path):
            return None

        current_size = os.path.getsize(self.log_path)
        if current_size < self.last_size:
            self.last_size = 0  # ローテーション対応

        new_content = ""
        if current_size > self.last_size:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(self.last_size)
                new_content = f.read()
            self.last_size = current_size

        if not new_content:
            return None

        detected_blocks = []
        for line in new_content.splitlines():
            raw_line = line.strip()
            if not raw_line: continue

            # ブロック開始判定
            if "緊急地震速報：" in raw_line or "[Twitter] Post Success:" in raw_line:
                self.pending_block = raw_line + "\n"
            # ブロック蓄積中
            elif self.pending_block:
                if raw_line == ":": continue
                self.pending_block += raw_line + "\n"
                # 送信トリガー (画像パス判定)
                low_line = raw_line.lower()
                if ".png" in low_line and "capture" in low_line:
                    detected_blocks.append(self.pending_block)
                    self.pending_block = ""

        return detected_blocks if detected_blocks else None