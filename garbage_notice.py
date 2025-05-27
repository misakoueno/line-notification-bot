import os
import datetime

garbage_schedule = {
    "若田町": {
        "燃やせるごみ": ["月曜日", "木曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "金曜日", "occurrences": [2, 4]},
        "地区": "八幡"
    },
    "若松町（1）､（2）､（3）､（4）､（坂下）": {
        "燃やせるごみ": ["月曜日", "木曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "水曜日", "occurrences": [1, 3]},
        "地区": "南"
    },
    "我峰町": {
        "燃やせるごみ": ["火曜日", "金曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "木曜日", "occurrences": [2, 4]},
        "地区": "長野"
    },
    "和田町（1）､（2）､（3）": {
        "燃やせるごみ": ["月曜日", "木曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "水曜日", "occurrences": [1, 3]},
        "地区": "南"
    },
    "和田多中町（住居表示1番から4番）": {
        "燃やせるごみ": ["火曜日", "金曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "水曜日", "occurrences": [2, 4]},
        "地区": "城南"
    },
    "和田多中町（上記以外の地域）": {
        "燃やせるごみ": ["火曜日", "金曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "火曜日", "occurrences": [1, 3]},
        "地区": "佐野"
    },
    "綿貫町": {
        "燃やせるごみ": ["月曜日", "木曜日"],
        "燃やせないごみ（資源物）": {"type": "第n曜日", "day_of_week": "金曜日", "occurrences": [2, 4]},
        "地区": "岩鼻"
    }
}

# 曜日を数値に変換するためのヘルパー（月曜日が0）
day_mapping = {
    "月曜日": 0, "火曜日": 1, "水曜日": 2, "木曜日": 3, "金曜日": 4, "土曜日": 5, "日曜日": 6
}

import requests
import json

# 環境変数から設定を読み込む
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID") # 通知先のあなたのLINEユーザーID

def get_day_of_week_occurrence(date_obj):
    """指定された日付が、その月の何回目のその曜日かを返す (例: 第2火曜日なら2)"""
    first_day_of_month = date_obj.replace(day=1)
    occurrence = 0
    # 1日から指定された日までループし、同じ曜日が何回あったかを数える
    for i in range(date_obj.day):
        current_day = first_day_of_month + datetime.timedelta(days=i)
        if current_day.weekday() == date_obj.weekday():
            occurrence += 1
    return occurrence

def send_line_message(message):
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("エラー: LINE_CHANNEL_ACCESS_TOKEN または LINE_USER_ID が設定されていません。")
        if not LINE_CHANNEL_ACCESS_TOKEN:
            print("デバッグ情報: LINE_CHANNEL_ACCESS_TOKEN が見つかりません。GitHub Secretsに正しく設定されているか確認してください。")
        if not LINE_USER_ID:
            print("デバッグ情報: LINE_USER_ID が見つかりません。GitHub Secretsに正しく設定されているか確認してください。")
        return False # 送信失敗を示す

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    
    print(f"送信先ユーザーID: {LINE_USER_ID[:5]}... (マスキング済み)") # ユーザーIDの一部をマスキングして表示
    print(f"送信メッセージ: {message}")

    response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("メッセージが正常に送信されました。")
        return True
    else:
        print(f"メッセージ送信に失敗しました。ステータスコード: {response.status_code}")
        print(f"エラー内容: {response.text}")
        return False

def main():
    # GitHub Actionsの実行環境のタイムゾーンを日本時間に設定するため、
    # os.environ['TZ'] = 'Asia/Tokyo'
    # datetime.timezone.utc から datetime.timezone(datetime.timedelta(hours=9)) を使うなど、
    # 確実に日本時間で日付を取得できるようにします。
    # GitHub Actionsのワークフロー側で環境変数 TZ を設定するのが一般的です。
    
    # 現在の日本時間を取得
    jst = datetime.timezone(datetime.timedelta(hours=9))
    today_jst = datetime.datetime.now(jst).date()
    tomorrow_jst = today_jst + datetime.timedelta(days=1)

    print(f"今日の日付 (JST): {today_jst}")
    print(f"明日の日付 (JST): {tomorrow_jst}")

    messages_to_send = []
    day_name_tomorrow = ["月", "火", "水", "木", "金", "土", "日"][tomorrow_jst.weekday()]

    # 環境変数からユーザーの町名を取得
    user_town_name = os.environ.get("USER_TOWN_NAME")
    if not user_town_name:
        print("致命的エラー: 環境変数 USER_TOWN_NAME が設定されていません。プログラムを終了します。")
        print("GitHub Actionsのワークフローファイル (.github/workflows/line_notify.yml) の env セクションで USER_TOWN_NAME を設定してください。")
        exit(1)

    if user_town_name not in garbage_schedule:
        print(f"致命的エラー: 設定された町名「{user_town_name}」の収集スケジュールが見つかりません。")
        print(f"利用可能な町名: {', '.join(garbage_schedule.keys())}")
        print("USER_TOWN_NAME の設定を確認するか、garbage_scheduleに情報を追加してください。")
        exit(1)

    schedule_for_town = garbage_schedule[user_town_name]
    print(f"町名「{user_town_name}」のスケジュールで通知を確認します。")

    # 燃やせるゴミのチェック
    if "燃やせるごみ" in schedule_for_town:
        for day_str in schedule_for_town["燃やせるごみ"]:
            if day_mapping.get(day_str) == tomorrow_jst.weekday():
                messages_to_send.append(f"明日は「燃やせるごみ」の日です。({tomorrow_jst.strftime('%Y-%m-%d')} {day_name_tomorrow}曜日)")
                break 

    # 燃やせないごみ（資源物）のチェック
    if "燃やせないごみ（資源物）" in schedule_for_town:
        non_burnable_schedule = schedule_for_town["燃やせないごみ（資源物）"]
        if non_burnable_schedule.get("type") == "第n曜日":
            target_day_of_week_num = day_mapping.get(non_burnable_schedule.get("day_of_week"))
            if target_day_of_week_num is not None and target_day_of_week_num == tomorrow_jst.weekday():
                occurrence = get_day_of_week_occurrence(tomorrow_jst) 
                if occurrence in non_burnable_schedule.get("occurrences", []):
                    messages_to_send.append(f"明日は「燃やせないごみ（資源物）」の日です。(第{occurrence}{day_name_tomorrow}曜日)")


    if messages_to_send:
        full_message = "\n".join(messages_to_send)
        print(f"送信予定メッセージ:\n{full_message}")
        send_line_message(full_message)
    else:
        print(f"明日は通知対象のゴミ出しはありません。({tomorrow_jst.strftime('%Y-%m-%d')} {day_name_tomorrow}曜日)")

if __name__ == "__main__":
    # LINE_CHANNEL_ACCESS_TOKEN と LINE_USER_ID の存在チェックを最初に行う
    if not os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"):
        print("致命的エラー: 環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません。プログラムを終了します。")
        exit(1)
    if not os.environ.get("LINE_USER_ID"):
        print("致命的エラー: 環境変数 LINE_USER_ID が設定されていません。プログラムを終了します。")
        exit(1)
    main()
