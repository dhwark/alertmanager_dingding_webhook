### dingding_webhook

webhook由fastapi编写，接收alertmanager的告警然后格式化发送到钉钉机器人

test_api是测试接口，模拟alertmanager向api发送json告警数据

使用加签的认证方式，只需要将你的url和密钥填入settings.json即可
```
{
    "secret": "exemple",
    "url": "exemple"
}
```
