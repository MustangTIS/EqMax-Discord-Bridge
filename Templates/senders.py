# senders.py
import requests
import json
import os

# --- 1. ペイロード構築ロジック ---
def build_payload(style, title, description, color, bot_name, current_version):
    # Discord系
    if style == "dissimple":
        return {
            "content": f"📢 **{title}** / {description}".replace("\n", " / ").strip(),
            "username": bot_name
        }
    elif style == "disembed":
        return {
            "username": bot_name,
            "embeds": [{
                "title": title, 
                "description": description, 
                "color": color,
                "image": {"url": "attachment://image.png"},
                "footer": {"text": f"EqMax Guardian v{current_version}"}
            }]
        }
    
    # Slack用
    elif style == "slack":
        return {
            "text": f"📢 *{title}*\n{description}",
            "username": bot_name
        }
        
    # Matrix用
    elif style == "matrix":
        return {
            "msgtype": "m.text",
            "body": f"{title}\n{description}"
        }
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
    """Matrix APIを使用してメッセージを送信する"""
    try:
        # URLを整えてAPIエンドポイントを構築
        base_url = url.rstrip('/')
        api_url = f"{base_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        return requests.post(api_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        return e

# --- 3. 司令塔 (ディスパッチャ) ---
def dispatch(style, title, description, color, image_path, url, bot_name, current_version, matrix_token=None, matrix_room=None):
    style_key = style.lower()
    payload = build_payload(style_key, title, description, color, bot_name, current_version)
    
    # Discord系
    if style_key in ["disembed", "dissimple"]:
        return send_to_discord(payload, style_key, image_path, url, bot_name, current_version)
    
    # Slack系
    elif style_key == "slack":
        return send_to_slack(payload, url)
        
    # Matrix系
    elif style_key == "matrix":
        if not matrix_token or not matrix_room:
            return Exception("Matrix: TokenまたはRoom IDが設定されていません")
        return send_to_matrix(payload, url, matrix_token, matrix_room)
    
    return Exception(f"未対応の送信スタイル: {style}")