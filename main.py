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


KEYWORDS_REPLY = {
    "妹": [
        "妹じゃないです",
    ],
    "姉": [
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "呼びません！",
        "ココアお姉ちゃん… ですね",
        "シャロさんみたいな姉が欲しかったです",
        "…お姉ちゃんの ねぼすけ",
        "ごめんねお姉ちゃん…\nいい子になるからもう怒らないで…",
    ],
}

NORMAL_REPLY = [
    "おはようございます",
    "これからおじいちゃんを焼きます",
    "そんな危険なものをいれるくらいなら\nパサパサパンで我慢します！",
    "もふもふ喫茶…",
    "非売品です",
    "私の腹話術です",
    "えらい えらいです",
    "お話… 一緒に寝る…\n私にちゃんと出来るかな…",
    "ティッピーが頭に乗ってたら2倍の力が出せるんです\nうそじゃないです",
    "わ 私おいしくないです！\n食べないでください！",
    "もっと笑ってたら\nお客さん来てくれる…？",
]


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    is_parrot_reply = False  # default: True
    if is_parrot_reply:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        return
    for keyword in KEYWORDS_REPLY:
        if keyword in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=random.choice(KEYWORDS_REPLY[keyword])
                ))
            return
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=random.choice(NORMAL_REPLY)
        ))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
