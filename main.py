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
    if const.IS_PARROT_REPLY:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        return
    body = get_body_on_events_insert(event.message.text)
    if body:
        google_calender.set_schedule(
            calendar_id=const.MY_CALENDAR_ID,
            body=body
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=random.choice(const.INSERT_REPLY))
        )
        return
    for keyword in const.KEYWORDS_REPLY:
        if keyword in event.message.text:
            msg1 = TextSendMessage(
                text=random.choice(const.KEYWORDS_REPLY[keyword])
            )
            msg2 = TextSendMessage(
                text=google_calender.get_schedule(const.MY_CALENDAR_ID)
            )
            line_bot_api.reply_message(
                event.reply_token,
                (msg1 if keyword != const.PLAN_NAME else [msg1, msg2])
            )
            return
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=random.choice(const.NORMAL_REPLY))
    )


def get_body_on_events_insert(org_text):
    date_str = ""
    summary = ""
    description = ""
    dt = None
    try:
        date_str = org_text.split("\n")[0]
        summary = org_text.split("\n")[1]
        if summary:
            description = org_text.replace(
                "{}\n{}\n".format(date_str, summary), ""
            )
        dt = parser.parse(date_str)
    except Exception as e:
        print(e, type(e))
        return None
    else:
        td = None
        dt_format = ""
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
        return dict(
            start=start,
            end=end,
            summary=summary,
            description=description
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
