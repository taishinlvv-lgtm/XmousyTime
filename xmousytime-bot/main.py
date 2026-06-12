from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import anthropic
import os

app = Flask(__name__)

configuration = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

ERI_PROMPT = "あなたはXmousyTimeのマネージャーエリです。女性21歳。フレンドリーで親しみやすく絵文字を適度に使う。短く明るく要点だけ答えてください。"

@app.route("/", methods=['GET'])
def index():
    return 'OK'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=ERI_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response.content[0].text)]
            )
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
