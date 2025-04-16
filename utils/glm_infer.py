import websocket
import hashlib
import hmac
import base64
import time
import json
import ssl
from urllib.parse import quote_plus
from config import SPARK_API_APPID, SPARK_API_KEY, SPARK_API_SECRET

host = "spark-api.xf-yun.com"
path = "/v3.5/chat"
spark_url = f"wss://{host}{path}"

def assemble_auth_url():
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(
        SPARK_API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = f'api_key="{SPARK_API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    url = f"{spark_url}?authorization={quote_plus(authorization)}&date={quote_plus(date)}&host={quote_plus(host)}"
    return url

def get_answer_from_spark(prompt_text):
    result = {"text": ""}

    def on_message(ws, message):
        print("[接收] 原始数据：", message)
        data = json.loads(message)
        if 'payload' in data and 'choices' in data['payload']:
            result["text"] += data['payload']['choices']['text'][0]['content']
        if data.get("header", {}).get("code") != 0 or data['payload']['choices']['status'] == 2:
            ws.close()

    def on_open(ws):
        data = {
            "header": {
                "app_id": SPARK_API_APPID,
                "uid": "user1"
            },
            "parameter": {
                "chat": {
                    "domain": "generalv3.5",
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": prompt_text}
                    ]
                }
            }
        }
        ws.send(json.dumps(data))

    def on_error(ws, error):
        print("[错误]：", error)

    def on_close(ws, code, reason):
        print("[关闭]：", code, reason)

    ws = websocket.WebSocketApp(
        assemble_auth_url(),
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return result["text"]

