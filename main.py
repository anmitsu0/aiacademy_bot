from flask import Flask
from flask import request
from flask import abort

from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent
from linebot.models import TextMessage
from linebot.models import TextSendMessage

import os
import random

import const
import google_calender

app = Flask(__name__)

# 環境変数
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if const.IS_PARROT_REPLY:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        return
    for keyword in const.KEYWORDS_REPLY:
        if keyword in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=random.choice(const.KEYWORDS_REPLY[keyword])
                )
            )
            if keyword == "予定":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=google_calender.get_schedule(const.MY_CALENDAR_ID)
                    )
                )
            return
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=random.choice(const.NORMAL_REPLY))
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
