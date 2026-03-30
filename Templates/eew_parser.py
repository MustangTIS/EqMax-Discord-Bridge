# eew_parser.py
import re

def get_alert_details(text_block):
    """
    抽出されたテキストブロックから、震度・マグニチュード・本文・色を解析する。
    """
    if "緊急地震速報：" not in text_block: 
        return None, None, None

    lines = text_block.strip().split('\n')
    shindo, mag_str, mag_val = "不明", "不明", 0.0
    clean_lines, found_essential = [], False 

    for line in lines:
        line = line.strip()
        if not line: continue

        # --- [重要] 実機ログのヘッダー除去 ---
        # "2026/03/18 06:14:16-TTwitterForm.CheckEEWCondition: true" 等の対策
        # ハイフン以降を本文として抽出
        if "-" in line and ("TTwitter" in line or "PostTweet" in line):
            line = line.split("-", 1)[-1]
            # 識別子部分も除去して「速報：」から始まるように整える
            line = re.sub(r'TTwitter\w+\.\w+:\s*', '', line)
            line = re.sub(r'PostTweet:\s*', '', line)
            line = line.strip()

        # 除外ワードの判定（ヘッダー除去後の純粋な本文で判定）
        if any(x in line for x in ["=", "remaining", "Image Filename:"]): continue
        if "尚、これは" in line: break
        
        # 地震情報の抽出
        if "震源地：" in line: 
            found_essential = True
        if "推定最大震度：" in line: 
            shindo = line.split("：")[1].strip()
        if "マグニチュード：" in line:
            mag_str = line.split("：")[1].strip()
            m_match = re.search(r"(\d+\.\d+|\d+)", mag_str)
            if m_match: 
                mag_val = float(m_match.group(1))
                found_essential = True
        
        # パース後の有効な行を蓄積
        if line:
            clean_lines.append(line)

    if not found_essential: 
        return None, None, None

    description = "\n".join(clean_lines)
    title = f"EEW Alert📢 【最大震度 {shindo} / {mag_str}】"
    
# 色設定（Discord Embed用）
    color = 0x808080 # 灰色（判定不能時）
    colors = {
        "7":   0xFF0000, # 赤
        "6強": 0xA52A2A, # 濃い赤（茶色系で差別化）
        "6弱": 0xFF4500, # 朱色（オレンジ赤）
        "5強": 0xFF8C00, # 濃いオレンジ
        "5弱": 0xFFA500, # オレンジ
        "4":   0xFFFF00, # 黄色
        "3":   0x00FF00, # 緑色
        "2":   0x00FFFF, # 水色
        "1":   0xFFFFFF  # 白色
    }
        
    for k, v in colors.items():
        if k in shindo: color = v; break

    # 海域判定
    if any(k in description for k in ["海", "沖", "灘", "湾"]):
        if mag_val >= 7.5:
            description = "🚨**【巨大地震・大津波警戒】直ちに避難！**\n\n" + description
            color = 0xff0000 #赤
        elif mag_val >= 6.0:
            description = "⚠️**大規模な海域地震：津波警戒**\n\n" + description
            color = 0xffa500 #濃いオレンジ
        else:
            description = "ℹ️海域地震：念のため注意\n\n" + description

    return title, description, color

def parse_log_content(content):
    """
    Twitter.logから送られてきた生データを解析し、
    タイトル、本文、色、画像パスを返す。
    """
    # 正規表現で「速報の開始から画像パスまで」を1ブロックとして抽出
    # 実機ログの日付ヘッダーがあってもマッチするように調整
    pattern = re.compile(r"(緊急地震速報：.*?)(C:\\.*?\.png)", re.DOTALL)
    matches = pattern.findall(content)
    
    if not matches:
        return None, None, None, None

    # 最新の情報を採用
    full_text, image_path = matches[-1]
    title, description, color = get_alert_details(full_text)
    
    return title, description, color, image_path