import requests
import json

# json load
filename = 'raw.json'
with open(filename, 'r', encoding='utf-8') as f:
    jsonLoad = json.load(f)
    # loads是解析json字符串，load是从文件中读取json数据

    # 转换为JSON字符串
    json_data = json.dumps(jsonLoad)
    

def send_alert_to_dingding(json_data):
    url = "http://192.168.1.100:8100/webhook"
    requests.post(url=url, data=json_data)

send_alert_to_dingding(json_data)