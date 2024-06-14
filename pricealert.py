import sqlite3
import time
from getprice import getprice
from linenotify import send_line_notify

def check_and_notify():
    conn = sqlite3.connect('icrypto.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 查詢所有的價格提醒
    cursor.execute('SELECT * FROM pricealert')
    pricealerts = cursor.fetchall()

    user_messages = {}  # 用於存儲每個使用者的消息
    alerts_to_update = []  # 用於存儲需要更新的提醒

    for alert in pricealerts:
        alert_id, userid, symbol, price, change = alert['id'], alert['userid'], alert['symbol'], alert['price'], alert['change']

        # 查詢最新價格
        latest_price = getprice(symbol)

        # 判斷是否需要發送通知
        if latest_price > price + change or latest_price < price - change:
            message = f"\n{symbol} : {latest_price}"
            if userid not in user_messages:
                user_messages[userid] = []
            user_messages[userid].append(message)
            alerts_to_update.append((latest_price, alert_id))

    # 發送通知
    for userid, messages in user_messages.items():
        cursor.execute('SELECT linetoken FROM users WHERE id=?', (userid,))
        user = cursor.fetchone()
        if user:
            linetoken = user['linetoken']
            message = "\n".join(messages)
            send_line_notify(message, linetoken)

    # 更新有發送行為的提醒的價格
    for latest_price, alert_id in alerts_to_update:
        cursor.execute('UPDATE pricealert SET price=? WHERE id=?', (latest_price, alert_id))

    conn.commit()
    cursor.close()
    conn.close()

# 定時執行
while True:
    check_and_notify()
    time.sleep(900)  # 每分鐘執行一次
