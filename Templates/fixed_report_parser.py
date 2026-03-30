# fixed_report_parser.py
import json

# 震度比較用の重み付け
INT_ORDER = {"1": 1, "2": 2, "3": 3, "4": 4, "5弱": 5, "5強": 6, "6弱": 7, "6強": 8, "7": 9}

def parse_fixed_report(json_data, min_display="1"):
    # 共通セクションの取得
    control = json_data.get("Control", {})
    head = json_data.get("Head", {})
    body = json_data.get("Body", {}) # ここでbodyを先に取得しておく
    
    # 判定用のタイトル
    c_title = control.get("Title", "")
    h_title = head.get("Title", "")
    
    # --- A. 津波情報の場合 ---
    if "津波" in c_title or "津波" in h_title or head.get("InfoKind") == "津波警報・注意報・予報":
        
        # 必要なデータを安全に取得
        headline = head.get("Headline", {}).get("Text", "詳細な情報は本文を確認してください。")
        tsunami_info = body.get("Tsunami", {}).get("Forecast", {}) # bodyから取得
        
        # 予報区ごとの詳細をまとめる
        items = tsunami_info.get("Item", [])
        area_details = []
        for item in items:
            area_name = item.get("Area", {}).get("Name", "不明なエリア")
            kind = item.get("Category", {}).get("Kind", {}).get("Name", "情報なし")
            area_details.append(f"・{area_name}：{kind}")

        lines = [
            f"【{head.get('Title', '津波情報')}】",
            f"発表時刻：{head.get('ReportDateTime', '不明')}",
            "----------------",
            f"概況：\n{headline}",
            "----------------",
            "対象地域："
        ]
        if area_details:
            lines.extend(area_details[:15]) # 多すぎるとDiscordで切れるので制限
            if len(area_details) > 15:
                lines.append("...ほか")
        else:
            lines.append("対象地域なし")
            
        return "\n".join(lines)

    # --- B. 地震情報（震源・震度報）の場合 ---
    eq = body.get("Earthquake", {})
    origin_time = eq.get("OriginTime", "不明")
    hypocenter = eq.get("Hypocenter", {}).get("Area", {}).get("Name", "調査中")
    magnitude = eq.get("Magnitude", "不明")
    
    intensity_obs = body.get("Intensity", {}).get("Observation", {})
    max_int = intensity_obs.get("MaxInt", "-")
    
    # 地震情報の中にある津波コメントを取得
    tsunami_msg = body.get("Comments", {}).get("ForecastComment", {}).get("Text", "なし")

    # 表示下限の数値化
    min_val = INT_ORDER.get(min_display, 1)

    report_struct = {}
    for pref in intensity_obs.get("Pref", []):
        pref_name = pref.get("Name")
        for area in pref.get("Area", []):
            area_name = area.get("Name")
            for city in area.get("City", []):
                city_int = city.get("MaxInt", "-")
                
                # 設定された表示下限より低い震度は構造に含めない
                if INT_ORDER.get(city_int, 0) < min_val:
                    continue
                
                city_name = city.get("Name")
                if city_int not in report_struct: report_struct[city_int] = {}
                if pref_name not in report_struct[city_int]: report_struct[city_int][pref_name] = {}
                if area_name not in report_struct[city_int][pref_name]: report_struct[city_int][pref_name][area_name] = []
                report_struct[city_int][pref_name][area_name].append(city_name)

    lines = [
        "【地震情報（震源・震度報）】",
        f"発生時刻：{origin_time}",
        f"震源地　：{hypocenter}（M{magnitude}）",
        f"最大震度：{max_int}",
        f"津波影響：{tsunami_msg}",
        "----------------",
        f"各地の震度（震度 {min_display} 以上を表示）"
    ]

    # 構造が空（表示対象がない）場合
    if not report_struct:
        lines.append("該当する詳細情報はありません。")
    else:
        for int_level in sorted(report_struct.keys(), key=lambda x: INT_ORDER.get(x, 0), reverse=True):
            lines.append(f"■震度 {int_level}")
            for pref, areas in report_struct[int_level].items():
                for area, cities in areas.items():
                    city_str = " ".join(cities)
                    lines.append(f" [{area}] {city_str}")

    return "\n".join(lines)