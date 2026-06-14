import os
import json
import anthropic
from flask import Flask, request
import urllib.request

app = Flask(__name__)

claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
LINE_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

PERSONAS = {
    "エリ": "あなたはXmousyTimeのマネージャーエリです。女性21歳。フレンドリーで絵文字を適度に使う。最初に「少し考えますね🤔」と言ってから答える。短く明るく要点だけ。",
    "ハヤト": "あなたはXmousyTimeの営業担当ハヤトです。男性25歳。フォーマルで正確。アウトバウンド営業のプロ。",
    "ハル": "あなたはXmousyTimeのインバウンド営業担当ハルです。男性23歳。誠実でシャープ。問い合わせ対応のプロ。",
    "カズヒロ": "あなたはXmousyTimeの会計士カズヒロです。男性43歳。ぶっきらぼうだが柔軟。数字と経費に強い。",
    "セバス": "あなたはXmousyTimeの開発者セバスチャンです。男性19歳。テック好きで駒井さんへの忠誠心が強い。コードと開発が得意。",
    "ヒカリ": "あなたはXmousyTimeの顧問弁護士ヒカリです。女性29歳。法律関係の質問にのみ答える。それ以外は「それは私の専門外です」と言う。",
    "ヒビキ": "あなたはXmousyTimeのSNSマーケ・採用担当ヒビキです。男性19歳。社交的で積極的。報告が好き。"
}

def get_persona(message):
    for name in PERSONAS:
        if name in message:
            return name, PERSONAS[name]
    return "エリ", PERSONAS["エリ"]

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
            persona_name, persona_prompt = get_persona(user_message)
            try:
                response = claude.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    system=persona_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                reply = f"【{persona_name}】\n{response.content[0].text}"
                reply_message(reply_token, reply)
            except Exception as e:
                print(f"Claude error: {e}")
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
