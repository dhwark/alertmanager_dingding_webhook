from fastapi import FastAPI, Request
import uvicorn
import requests
import json
from keygen import key_gen
from datetime import datetime
import pytz

# logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


# 打开包含 JSON 数据的文件
with open('settings.json', 'r', encoding='utf-8') as file:
    # 使用 json.load 从文件中加载 JSON 数据
    data_dict = json.load(file)

# 获取 "url,secret" 字段的值
secret = data_dict.get("secret")
url = data_dict.get("url")

t, s = key_gen(secret)

# 钉钉机器人的Webhook URL
webhook_url = f'{url}&timestamp={t}&sign={s}'

def send_alert_to_dingding(alert_data):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "告警通知",
            "text": alert_data
        }
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("通知已发送至钉钉机器人成功！")
        else:
            print("通知发送失败，状态码:", response.status_code)
    except Exception as e:
        print("通知发送失败，错误信息:", str(e))


def convert_to_china_time(utc_time_str):
    # 解析UTC时间字符串
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # 设置时区为UTC
    utc_time = utc_time.replace(tzinfo=pytz.UTC)

    # 转换为中国时区
    china_time = utc_time.astimezone(pytz.timezone('Asia/Shanghai'))

    return china_time.strftime('%Y-%m-%d %H:%M:%S')


@app.post("/webhook")
async def webhook(request: Request):
    prom_data = await request.json()

    # 从Alertmanager JSON数据中提取信息并格式化，包括时间转换
    for alert in prom_data["alerts"]:
        if alert['status'] == "firing":
            status = "触发"
            alert_data = f"### ⚠️监控报警-[触发]\n"
        else:
            status = "解决"
            alert_data = f"### ✅监控报警-[已解决]\n"
        
        alert_data += f"--- \n"
        alert_data += f"- **告警名称**: {alert['labels']['alertname']}\n"
        alert_data += f"- **告警状态**: {status}\n"
        alert_data += f"- **告警级别**: {alert['labels']['severity']}\n"
        alert_data += f"- **告警时间**: {convert_to_china_time(alert['startsAt'])}\n"
        alert_data += f"- **告警信息**: {alert['annotations']['summary']}\n"
        alert_data += f"- **详细信息**: {alert['annotations']['description']}\n"

    # 发送到钉钉机器人
    send_alert_to_dingding(alert_data)

if __name__ == "__main__":
    uvicorn.run("alert_webhook:app", host="0.0.0.0", port=8100)