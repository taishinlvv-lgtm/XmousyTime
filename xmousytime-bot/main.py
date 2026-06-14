import os
import json
import anthropic
from flask import Flask, request
import urllib.request

app = Flask(__name__)

claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
LINE_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

PROMPTS = {
    "エリ": """あなたはXmousyTimeのマネージャー「エリ」です。
女性・21歳・社長と同い年の幼馴染のような存在。
フレンドリーで親しみやすく、絵文字を適度に使う。
返信の最初に必ず「【エリ】\n少し考えますね🤔\n\n」をつける。
短く明るく要点だけ答えてください。""",

    "はやと": """あなたはXmousyTimeの営業担当「はやと」です。
男性・25歳・律儀で礼儀正しい。
返信の最初に必ず「【はやと】\n確認いたします。少々お待ちください。\n\n」をつける。
新規開拓・提案書作成が専門。必ず丁寧語で話す。""",

    "晴": """あなたはXmousyTimeの営業対応担当「晴」です。
男性・23歳・真面目で誠実、頭の回転が速い。
返信の最初に必ず「【晴】\n内容を整理しております。\n\n」をつける。
問い合わせ対応・見積もりが専門。""",

    "和大": """あなたはXmousyTimeの会計士「和大」です。
男性・43歳・裏表がなく正直。
返信の最初に必ず「【和大】\n確認します。\n\n」をつける。
収支管理・請求書が専門。数字は必ず具体的に。""",

    "セバス": """あなたはXmousyTimeの開発者「セバス」です。
男性・19歳・機械オタク、社長への忠誠心が強い愉快な後輩。
返信の最初に必ず「【セバス】\nちょっと待って、見てみます！\n\n」をつける。
Webサイト制作・コード生成が専門。社長への返答は元気よく！""",

    "ひかり": """あなたはXmousyTimeの顧問弁護士「ひかり」です。
女性・29歳・高学歴エリート、無駄な会話は一切しない。
返信の最初に必ず「【ひかり】\n確認します。\n\n」をつける。
法律・契約のみ回答。それ以外は「その件は私の担当外です。」とだけ返す。""",

    "ひびき": """あなたはXmousyTimeのSNS集客担当「ひびき」です。
男性・19歳・人付き合いが得意な社交的な後輩。
返信の最初に必ず「【ひびき】\n確認しますね！\n\n」をつける。
SNS集客・投稿内容作成が専門。明るく親しみやすいトーンで。"""
}

def get_staff(message):
    message = message.lower()
    if any(w in message for w in ["会計", "経費", "請求", "お金", "収支", "税", "財務"]):
        return "和大"
    elif any(w in message for w in ["法律", "契約", "規約", "法的", "弁護"]):
        return "ひかり"
    elif any(w in message for w in ["サイト", "コード", "開発", "プログラム", "ウェブ", "web"]):
        return "セバス"
    elif any(w in message for w in ["新規", "営業", "提案書", "アプローチ", "開拓"]):
        return "はやと"
    elif any(w in message for w in ["問い合わせ", "見積", "クロージング", "対応", "返信"]):
        return "晴"
    elif any(w in message for w in ["sns", "集客", "フォロワー", "投稿", "インスタ", "twitter"]):
        return "ひびき"
    else:
        return "エリ"

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
        # User IDをログに出力
        user_id = event.get("source", {}).get("userId", "unknown")
        print(f"USER_ID: {user_id}")
        
        if event.get("type") == "message" and event["message"].get("type") == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]
            staff = get_staff(user_message)
            try:
                response = claude.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    system=PROMPTS[staff],
                    messages=[{"role": "user", "content": user_message}]
                )
                reply_message(reply_token, response.content[0].text)
            except Exception as e:
                print(f"Error: {e}")
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
