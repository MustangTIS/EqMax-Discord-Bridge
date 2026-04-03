# fixed_report_parser.py
import json

# 震度比較用の重み付け（表記ゆれ対応版）
INT_ORDER = {
    "1": 1, "2": 2, "3": 3, "4": 4, 
    "5弱": 5, "5-": 5, 
    "5強": 6, "5+": 6, 
    "6弱": 7, "6-": 7, 
    "6強": 8, "6+": 8, 
    "7": 9
}

def parse_fixed_report(json_data, min_display="1"):
    control = json_data.get("Control", {})
    head = json_data.get("Head", {})
    body = json_data.get("Body", {})
    c_title = control.get("Title", "")
    h_title = head.get("Title", "")

    # --- A. 津波情報の場合 ---
    if "津波" in c_title or "津波" in h_title or head.get("InfoKind") == "津波警報・注意報・予報":
        headline = head.get("Headline", {}).get("Text", "詳細な情報は本文を確認してください。")
        tsunami_info = body.get("Tsunami", {}).get("Forecast", {})
        items = tsunami_info.get("Item", [])
        area_details = [f"・{item.get('Area', {}).get('Name', '不明なエリア')}：{item.get('Category', {}).get('Kind', {}).get('Name', '情報なし')}" for item in items]

        lines = [
            f"【{h_title}】",
            f"発表時刻：{head.get('ReportDateTime', '不明')}",
            "----------------",
            f"概況：\n{headline}",
            "----------------",
            "対象地域："
        ]
        lines.extend(area_details[:15])
        if len(area_details) > 15: lines.append("...ほか")
        return "\n".join(lines)

    # --- C. 遠地地震に関する情報の場合 (実機データ構造に合わせ修正) ---
    elif "遠地地震" in h_title:
        # 実機データでは Body > Earthquake (単一) の構造
        eq = body.get("Earthquake", {})
        if not eq: 
            # 万が一リスト形式(Earthquakes)で来た場合も考慮
            eqs = body.get("Earthquakes", [])
            if eqs: eq = eqs[0]
            else: return None
        origin_time = eq.get("OriginTime", "不明")
        hypocenter = eq.get("Hypocenter", {}).get("Area", {}).get("Name", "調査中")
        magnitude = eq.get("Magnitude", "不明")

        # 津波コメントの取得
        comments = body.get("Comments", {})
        tsunami_msg = comments.get("ForecastComment", {}).get("Text", "なし")

        # 自由付随コメント（太平洋津波報など）があれば追加
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