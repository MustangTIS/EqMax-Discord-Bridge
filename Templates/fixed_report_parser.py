import json
import re

# 震度比較用の重み付け（表記ゆれ対応版）
INT_ORDER = {
    "1": 1, "2": 2, "3": 3, "4": 4, 
    "5弱": 5, "5-": 5, 
    "5強": 6, "5+": 6, 
    "6弱": 7, "6-": 7, 
    "6強": 8, "6+": 8, 
    "7": 9
}

def ensure_list(obj):
    """辞書かリストか不明なオブジェクトを常にリスト化して安全に回すためのヘルパー"""
    if obj is None: return []
    return obj if isinstance(obj, list) else [obj]

def parse_fixed_report(json_data, min_display="1"):
    control = json_data.get("Control", {})
    head = json_data.get("Head", {})
    body = json_data.get("Body", {})
    c_title = control.get("Title", "")
    h_title = head.get("Title", "")

    # --- A. 津波情報の場合 ---
    if "津波" in h_title or head.get("InfoKind") == "津波警報・注意報・予報":
        headline = head.get("Headline", {}).get("Text", "詳細な情報は本文を確認してください。")
        tsunami_node = body.get("Tsunami", {})
        
        warn_details = []  
        forecast_details = [] 
        
        # 1. 予報（エリア名と種別）
        forecast_items = ensure_list(tsunami_node.get("Forecast", {}).get("Item", []))
        for item in forecast_items:
            area_name = item.get('Area', {}).get('Name', '不明なエリア')
            kind_name = item.get('Category', {}).get('Kind', {}).get('Name', '情報なし')
            if "予報" in kind_name:
                forecast_details.append(area_name)
            else:
                warn_details.append(f"・{area_name}：{kind_name}")

        # 2. 観測地点（ソート）
        obs_data_list = []
        obs_items = ensure_list(tsunami_node.get("Observation", {}).get("Item", []))
        for item in obs_items:
            stations = ensure_list(item.get("Station", []))
            for st in stations:
                st_name = st.get("Name", "不明な地点")
                max_h = st.get("MaxHeight", {})
                h_val = max_h.get("TsunamiHeight")
                condition = max_h.get("Condition")
                try:
                    # 数値が含まれる場合は抽出、なければ-1（ソート用）
                    sort_val = float(re.findall(r"\d+\.?\d*", str(h_val))[0]) if h_val else -1.0
                except:
                    sort_val = -1.0
                display_val = f"{h_val}m" if h_val else (condition if condition else "観測中")
                obs_data_list.append({"name": st_name, "val": display_val, "sort_key": sort_val})

        # 高い順にソート
        obs_data_list.sort(key=lambda x: x["sort_key"], reverse=True)

        # 構築開始
        lines = [
            f"【{h_title}】",
            f"発表時刻：{head.get('ReportDateTime', '不明')}",
            "----------------",
            f"概況：\n{headline}",
            "----------------",
            "情報詳細："
        ]

        lines.extend(warn_details)
        if forecast_details:
            lines.append(f"・予報(若干の海面変動)：{', '.join(forecast_details)}")
        
        if obs_data_list:
            lines.append("--- 潮位観測値（高い順） ---")
            for d in obs_data_list:
                lines.append(f"・{d['name']}：{d['val']}")
            
        return "\n".join(lines)

    # --- C. 遠地地震に関する情報の場合 ---
    elif "遠地地震" in h_title:
        eq = body.get("Earthquake", {})
        if not eq: 
            eqs = body.get("Earthquakes", [])
            if eqs: eq = eqs[0]
            else: return None
        origin_time = eq.get("OriginTime", "不明")
        hypocenter = eq.get("Hypocenter", {}).get("Area", {}).get("Name", "調査中")
        magnitude = eq.get("Magnitude", "不明")

        comments = body.get("Comments", {})
        tsunami_msg = comments.get("ForecastComment", {}).get("Text", "なし")
        free_comment = comments.get("FreeFormComment", "")

        lines = [
            "【遠地地震に関する情報】",
            f"発生時刻：{origin_time}",
            f"震源地　：{hypocenter}（M{magnitude}）",
            f"津波影響：\n{tsunami_msg.strip()}",
            "----------------"
        ]

        if free_comment:
            lines.append(f"付随情報：{free_comment}")
            lines.append("----------------")
        lines.append("※海外で発生した大規模な地震の情報です。")
        return "\n".join(lines)

    # --- B. 地震情報（震源・震度報）の場合 ---
    elif "震源" in c_title or "震度" in h_title:
        eq = body.get("Earthquake", {})
        origin_time = eq.get("OriginTime", "不明")
        hypocenter = eq.get("Hypocenter", {}).get("Area", {}).get("Name", "調査中")
        magnitude = eq.get("Magnitude", "不明")
        
        intensity_obs = body.get("Intensity", {}).get("Observation", {})
        max_int = intensity_obs.get("MaxInt", "-")
        tsunami_msg = body.get("Comments", {}).get("ForecastComment", {}).get("Text", "なし")

        min_val = INT_ORDER.get(min_display, 1)
        report_struct = {}
        for pref in intensity_obs.get("Pref", []):
            pref_name = pref.get("Name")
            for area in pref.get("Area", []):
                area_name = area.get("Name")
                for city in area.get("City", []):
                    city_int = city.get("MaxInt", "-")
                    if INT_ORDER.get(city_int, 0) < min_val: continue
                    if city_int not in report_struct: report_struct[city_int] = {}
                    if pref_name not in report_struct[city_int]: report_struct[city_int][pref_name] = {}
                    if area_name not in report_struct[city_int][pref_name]: report_struct[city_int][pref_name][area_name] = []
                    report_struct[city_int][pref_name][area_name].append(city.get("Name"))

        lines = [
            "【地震情報（震源・震度報）】",
            f"発生時刻：{origin_time}",
            f"震源地　：{hypocenter}（M{magnitude}）",
            f"最大震度：{max_int}",
            f"津波影響：{tsunami_msg}",
            "----------------",
            f"各地の震度（震度 {min_display} 以上を表示）"
        ]

        if not report_struct:
            lines.append("該当する詳細情報はありません。")
        else:
            for int_level in sorted(report_struct.keys(), key=lambda x: INT_ORDER.get(x, 0), reverse=True):
                lines.append(f"■震度 {int_level}")
                for pref, areas in report_struct[int_level].items():
                    for area, cities in areas.items():
                        lines.append(f" [{area}] {' '.join(cities)}")

        return "\n".join(lines)

    return None