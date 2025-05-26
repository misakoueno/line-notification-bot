import os
import datetime
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
    
    # 翌日が火曜日かチェック
    if tomorrow_jst.weekday() == 1: # 0:月, 1:火, ...
        messages_to_send.append(f"明日は「燃えるゴミ」の日です。({tomorrow_jst.strftime('%Y-%m-%d')} {day_name_tomorrow}曜日)")

        # 第何火曜日かを判定
        occurrence = get_day_of_week_occurrence(tomorrow_jst)
        print(f"明日は第{occurrence}火曜日です。")
        
        if occurrence == 1 or occurrence == 3:
            messages_to_send.append("明日は「燃えないゴミ」も出せます。")

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
