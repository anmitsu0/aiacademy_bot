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

from dateutil import parser
import datetime

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
    reply_text = ""
    plan_text = ""
    if const.IS_PARROT_REPLY:
        reply_text = event.message.text
        reply(event, reply_text, plan_text)
        return
    body = get_body_on_events_insert(event.message.text)
    if body:
        google_calender.set_schedule(
            calendar_id=const.MY_CALENDAR_ID,
            body=body
        )
        reply_text = random.choice(const.INSERT_REPLY)
        reply(event, reply_text, plan_text)
        return
    keywords = [s for s in const.KEYWORDS_REPLY if s in event.message.text]
    if not keywords:
        reply_text = random.choice(const.NORMAL_REPLY)
    elif const.PLAN_NAME in keywords:
        keyword = const.PLAN_NAME
        reply_text = random.choice(const.KEYWORDS_REPLY[keyword])
        plan_text = google_calender.get_schedule(const.MY_CALENDAR_ID)
    else:
        keyword = random.choice(keywords)
        reply_text = random.choice(const.KEYWORDS_REPLY[keyword])
    reply(event, reply_text, plan_text)


def get_body_on_events_insert(org_text=""):
    try:
        lines = org_text.split("\n")
        date_str = lines[0]
        dt = parser.parse(date_str)
    except Exception as e:
        print(e, type(e))
        return None
    else:
        start = None
        end = None
        if dt.strftime(const.TIME_FORMAT) == const.TOP_TIME:
            td = datetime.timedelta(days=1)
            dt_format = const.DATE_FORMAT
            start = dict(date=dt.strftime(dt_format))
            end = dict(date=(dt + td).strftime(dt_format))
        else:
            td = datetime.timedelta(hours=1)
            dt_format = const.DATETIME_FORMAT
            start = dict(
                dateTime=dt.strftime(dt_format),
                timeZone=const.TIME_ZONE
            )
            end = dict(
                dateTime=(dt + td).strftime(dt_format),
                timeZone=const.TIME_ZONE
            )
        summary = ""
        description = ""
        if len(lines) >= 1:
            summary = lines[1]
        if len(lines) >= 2:
            description = lines[2:]
        return dict(
            start=start,
            end=end,
            summary=summary,
            description=description
        )


def reply(event, reply_text="", plan_text=""):
    if plan_text:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_text),
                TextSendMessage(text=plan_text)
            ]
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
