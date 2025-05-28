from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import warnings
import cohere_history


warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)

# LINEチャンネル設定
line_bot_api = LineBotApi(os.getenv("MSG_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 状態管理（グローバル変数）
is_chatting = False
chat_partner_user_id = None
requester_user_id = None
chat_history = []
conversation_stage = "idle"

# ユーザーIDと名前の対応辞書（仮のIDで埋めてあります）
user_directory = {
    "渡辺": "Uc39c7a912ddb27237116400b2347b924",
    "五十嵐": "U22222222222222222222222222222222",
    "佐藤": "U33333333333333333333333333333333",
    "鈴木": "U44444444444444444444444444444444",
    "田中": "U55555555555555555555555555555555",
    "高橋": "U66666666666666666666666666666666",
    "伊藤": "U77777777777777777777777777777777",
    "山本": "U88888888888888888888888888888888",
    "中村": "U99999999999999999999999999999999",
    "小林": "U00000000000000000000000000000001",
    "加藤": "U00000000000000000000000000000002",
    "吉田": "U00000000000000000000000000000003",
    "山田": "U00000000000000000000000000000004",
    "佐々木": "U00000000000000000000000000000005",
    "清水": "U00000000000000000000000000000006",
    "松本": "U00000000000000000000000000000007",
    "井上": "U00000000000000000000000000000008",
    "木村": "U00000000000000000000000000000009",
    "林": "U00000000000000000000000000000010",
    "斎藤": "U00000000000000000000000000000011",
    "原": "U00000000000000000000000000000012",
    "岡田": "U00000000000000000000000000000013"
}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel token/secret.")
        abort(400)

    return "OK"


import re

def contains_link(text):
    return bool(re.search(r'https?://[^\s]+', text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global is_chatting, chat_partner_user_id, requester_user_id, conversation_stage

    user_text = event.message.text
    user_id = event.source.user_id
    reply_token = event.reply_token

    if reply_token == "00000000000000000000000000000000":
        return

    if user_text == "会話を終了する":
        line_bot_api.reply_message(reply_token, TextSendMessage(text="会話を終了しました。"))
        if chat_partner_user_id:
            line_bot_api.push_message(chat_partner_user_id, TextSendMessage(text="お相手が会話を終了しました。"))
        is_chatting = False
        chat_partner_user_id = None
        requester_user_id = None
        conversation_stage = "idle"
        return

    if user_text == "日程を調整する":
        result = cohere_history.chat2("マッチングしたお相手の名前を教えてください", chat_history)
        chouseisan_url = "https://chouseisan.com/"
        line_bot_api.reply_message(reply_token, TextSendMessage(
            text=f"日程調整をお願いします：\n{chouseisan_url}\nリンクを送ってください。"
        ))

        for name in user_directory:
            requester_user_id = user_id
            if name in result:
                chat_partner_user_id = user_directory[name]
                conversation_stage = "waiting_for_link"
                return

        line_bot_api.reply_message(reply_token, TextSendMessage(text="適切なマッチング相手が見つかりませんでした。"))
        return

    # 🔽ここが追加された処理（リンク検知 → 相手に送信）
    if conversation_stage == "waiting_for_link" and contains_link(user_text):
        is_chatting = True
        conversation_stage = "chatting"
        line_bot_api.reply_message(reply_token, TextSendMessage(text="リンクを確認しました。会話を開始します。"))
        line_bot_api.push_message(chat_partner_user_id, TextSendMessage(text=f"こちらの日程調整リンクをご確認ください：\n{user_text}"))
        line_bot_api.push_message(chat_partner_user_id, TextSendMessage(text="お相手と1on1チャットを開始しました。"))
        line_bot_api.push_message(requester_user_id, TextSendMessage(text="マッチ相手にリンクを送りました。1on1をどうぞ。"))
        return

    # チャット中のメッセージ転送
    if is_chatting and chat_partner_user_id:
        if user_id == chat_partner_user_id:
            line_bot_api.push_message(requester_user_id, TextSendMessage(text=f"お相手からのメッセージ：\n{user_text}"))
        else:
            line_bot_api.push_message(chat_partner_user_id, TextSendMessage(text=f"お相手からのメッセージ：\n{user_text}"))
        line_bot_api.reply_message(reply_token, TextSendMessage(text="メッセージを転送しました。"))
        return

    # 通常応答
    response = cohere_history.chat2(user_text, chat_history)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=response))
