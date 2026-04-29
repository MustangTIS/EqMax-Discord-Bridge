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

    # Slack / Matrix / Bluesky 用 (テキストベース)
    elif style in ["slack", "matrix", "bluesky"]:
        body = f"{bold_title} / 送信時 {timestamp}\n{description}\n───────────"

        if style == "slack":
            return {"text": body, "username": bot_name}
        elif style == "matrix":
            return {"msgtype": "m.text", "body": body}
        elif style == "bluesky":
            # Blueskyはプレーンテキストのみを返す（装飾はAPI側で行う）
            return {"text": f"📢 {title}\n\n{description}\n\n({timestamp} 送信)"}

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
    try:
        txid = int(time.time() * 1000)
        base_url = url.rstrip('/')
        api_url = f"{base_url}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txid}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return requests.put(api_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        return e

def send_to_bluesky(payload, handle, password, image_path=None, pds_url="https://bsky.social"):
    """Bluesky (AT Protocol) への投稿処理"""
    try:
        # A. セッション作成 (ログイン)
        session_res = requests.post(
            f"{pds_url}/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password}, timeout=10
        )
        session_res.raise_for_status()
        session = session_res.json()
        headers = {"Authorization": f"Bearer {session['accessJwt']}"}

        # B. 画像がある場合はアップロード (Blob化)
        embed = None
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img_data = f.read()
            
            blob_res = requests.post(
                f"{pds_url}/xrpc/com.atproto.repo.uploadBlob",
                headers={**headers, "Content-Type": "image/png"},
                data=img_data, timeout=15
            )
            if blob_res.status_code == 200:
                blob = blob_res.json().get("blob")
                embed = {
                    "$type": "app.bsky.embed.images",
                    "images": [{"alt": "Earthquake Report", "image": blob}]
                }

        # C. ポスト作成
        post_payload = {
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "text": payload["text"][:300], # Blueskyの文字数制限対策
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "$type": "app.bsky.feed.post"
            }
        }
        if embed:
            post_payload["record"]["embed"] = embed

        res = requests.post(f"{pds_url}/xrpc/com.atproto.repo.createRecord", 
                           headers=headers, json=post_payload, timeout=10)
        return res
    except Exception as e:
        return e

# --- 3. 司令塔 (ディスパッチャ) ---
def dispatch(style, title, description, color, image_path, url, bot_name, current_version, timestamp, 
             matrix_token=None, matrix_room=None, shared_image_url=None,
             handle=None, password=None, **kwargs): # ← 「**kwargs」を最後に追加
    
    # 呼び出し元が旧名（bsky_handle / bsky_pass）で送ってきた場合でも値を拾う
    actual_handle = handle or kwargs.get("bsky_handle")
    actual_password = password or kwargs.get("bsky_pass")

    style_key = style.lower()

    # 画像URLが共有されていれば末尾に付記
    current_description = description
    if style_key in ["slack", "matrix", "bluesky"] and shared_image_url:
        current_description += f"\n画像: {shared_image_url}"

    payload = build_payload(style_key, title, current_description, color, bot_name, current_version, timestamp)

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

    # Bluesky系
    elif style_key == "bluesky":
        # 拾い直した actual_handle / actual_password を使う
        if not actual_handle or not actual_password: 
            return Exception("Bluesky: HandleまたはApp Passwordが設定されていません")
        
        pds = url if (url and url.startswith("http")) else "https://bsky.social"
        return send_to_bluesky(payload, actual_handle, actual_password, image_path, pds)

    return Exception(f"未対応の送信スタイル: {style}")