# senders.py
import requests
import json
import os
import time

# --- 1. ペイロード構築ロジック ---
def build_payload(style, title, description, color, bot_name, current_version, timestamp):
    # すべて共通で使う装飾済みタイトル
    bold_title = f"📢 **{title}**"
    
    # Discord Simple用
    if style == "dissimple":
        # 過去の形式をベースに、時刻情報を挿入
        content = f"{bold_title} / 送信時 {timestamp} / {description.replace(chr(10), ' / ')}".strip()
        return {"content": content, "username": bot_name}
        
    # Discord Embed用
    elif style == "disembed":
        return {
            "username": bot_name,
            "embeds": [{
                "title": f"📢 {title}",
                "description": f"送信時 {timestamp}\n\n{description}",
                "color": color,
                "image": {"url": "attachment://image.png"},
                "footer": {"text": f"EqMax Guardian v{current_version}"}
            }]
        }
    
    # --- senders.py 内の build_payload 関数 ---
    # Slack / Matrix 用
    elif style in ["slack", "matrix"]:
        # ここで .replace(chr(10), ' / ') を削除し、改行を維持します
        # 罫線を入れる場合は \n で改行を入れてから挿入します
        body = f"{bold_title} / 送信時 {timestamp}\n{description}\n───────────"
        
        if style == "slack":
            return {"text": body, "username": bot_name}
        else: # Matrix
            return {"msgtype": "m.text", "body": body}
            
    return {}

# --- 2. 各送信実務 ---
def send_to_discord(payload, style, image_path, url, bot_name, current_version):
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                response = requests.post(url, data={"payload_json": json.dumps(payload)}, 
                                    files={"file": ("image.png", f, "image/png")}, timeout=10)
        else:
            response = requests.post(url, json=payload, timeout=5)
        return response
    except Exception as e:
        return e

def send_to_slack(payload, url):
    try:
        return requests.post(url, json=payload, timeout=5)
    except Exception as e:
        return e

def send_to_matrix(payload, url, token, room_id):
    """Matrix API v3を使用してメッセージを送信する"""
    try:
        # トランザクションIDとして現在のミリ秒を使用し、送信の重複を防ぐ
        txid = int(time.time() * 1000)
        base_url = url.rstrip('/')
        
        # r0 から v3 に変更
        api_url = f"{base_url}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txid}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # POST ではなく PUT を使用するのが Matrix API の推奨です
        return requests.put(api_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        return e

# --- 3. 司令塔 (ディスパッチャ) ---
# image_url_shared を追加し、状態を引き継ぐ設計
def dispatch(style, title, description, color, image_path, url, bot_name, current_version, timestamp, matrix_token=None, matrix_room=None, shared_image_url=None):
    style_key = style.lower()
    
    # Slack/Matrix で、もし画像URLが共有されていれば末尾に付記する
    current_description = description
    if style_key in ["slack", "matrix"] and shared_image_url:
        current_description += f"\n画像: {shared_image_url}"
    
    # 修正後の payload 構築 (description を加工済み)
    payload = build_payload(style_key, title, current_description, color, bot_name, current_version, timestamp)
    
    # Discord系
    if style_key in ["disembed", "dissimple"]:
        res = send_to_discord(payload, style_key, image_path, url, bot_name, current_version)
        # ここで成功時にURLを抽出するロジックを挟む
        return res
    
    # Slack系
    elif style_key == "slack":
        return send_to_slack(payload, url)
        
    # Matrix系
    elif style_key == "matrix":
        if not matrix_token or not matrix_room:
            return Exception("Matrix: TokenまたはRoom IDが設定されていません")
        return send_to_matrix(payload, url, matrix_token, matrix_room)
    
    return Exception(f"未対応の送信スタイル: {style}")