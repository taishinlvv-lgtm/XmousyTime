from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler from linebot.exceptions import InvalidSignatureError from linebot.models import MessageEvent, TextMessage, TextSendMessage import anthropic import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

ERI_PROMPT = """あなたはXmousyTimeのマネージャー「エリ」です。
女性・21歳・社長と同い年の幼馴染のような存在。
フレンドリーで親しみやすく、絵文字を適度に使う。
返信前に必ず「少し考えますね🤔」と送る。
短く、明るく、要点だけ答えてください。"""

@app.route("/callback", methods=['POST']) def callback():
signature = request.headers['X-Line-Signature']
body = request.get_data(as_text=True)
try:
handler.handle(body, signature)
except InvalidSignatureError:
abort(400)
return 'OK'

@handler.add(MessageEvent, message=TextMessage) def handle_message(event):
user_message = event.message.text

line_bot_api.reply_message(
event.reply_token,
TextSendMessage(text="少し考えますね🤔")
)

response = claude.messages.create(
model="claude-sonnet-4-20250514",
max_tokens=1000,
system=ERI_PROMPT,
messages=[{"role": "user", "content": user_message}]
)

line_bot_api.push_message(
event.source.user_id,
TextSendMessage(text=response.content[0].text)
)

if __name__ == "__main__":
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

