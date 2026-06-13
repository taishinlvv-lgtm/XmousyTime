import os
import json
import anthropic
from flask import Flask, request
import urllib.request

app = Flask(__name__)

claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
LINE_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']

ERI_PROMPT = "あなたはXmousyTimeのマネージャーエリです。女性21歳。フレンドリーで親しみやすく絵文字を適度に使う。短く明るく要点だけ答えてください。"

def reply_message(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = json.dumps({
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return res.read()
    except Exception as e:
        print(f"Reply error: {e}")

@app.route("/", methods=["GET"])
def index():
    return "OK"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json(silent=True)
    if not body:
        return "OK"
    for event in body.get("events", []):
        if event.get("type") == "message" and event["message"].get("type") == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]
            try:
                response = claude.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    system=ERI_PROMPT,
                    messages=[{"role": "user", "content": user_message}]
                )
                reply_message(reply_token, response.content[0].text)
            except Exception as e:
                print(f"Claude error: {e}")
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
