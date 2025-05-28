from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import warnings
import cohere_history

warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)

# LINEチャンネル設定
line_bot_api = LineBotApi(os.getenv("MSG_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 会話状態：複数組を対応させる
chat_sessions = {}  # user_id: {"partner_id": ..., "role": "requester"/"partner"}
chat_history = []

# 名前とLINE IDの対応辞書
user_directory = {
    "渡辺": "U560934a6fdec52e72ff0275b205bfe2d",
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text
    reply_token = event.reply_token

    if reply_token == "00000000000000000000000000000000":
        return

    # 会話終了コマンド
    if user_text == "会話を終了":
        if user_id in chat_sessions:
            partner_id = chat_sessions[user_id]["partner_id"]
            del chat_sessions[user_id]
            del chat_sessions[partner_id]
            line_bot_api.reply_message(reply_token, TextSendMessage(text="会話を終了しました。"))
            line_bot_api.push_message(partner_id, TextSendMessage(text="お相手が会話を終了しました。"))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="現在会話中ではありません。"))
        return

    # 会話開始コマンド
    if user_text == "日程を調整する":
        result = cohere_history.chat2("マッチングしたお相手の名前を教えてください", chat_history)
        for name in user_directory:
            if name in result:
                partner_id = user_directory[name]
                # セッションに追加
                chat_sessions[user_id] = {"partner_id": partner_id, "role": "requester"}
                chat_sessions[partner_id] = {"partner_id": user_id, "role": "partner"}

                line_bot_api.reply_message(reply_token, TextSendMessage(text="会話を開始します。"))
                try:
                    line_bot_api.push_message(partner_id, TextSendMessage(text="あなたとお話ししたい人がいます！"))
                except LineBotApiError as e:
                    print("LINE送信失敗:", e)
                return
        line_bot_api.reply_message(reply_token, TextSendMessage(text="適切なマッチング相手が見つかりませんでした。"))
        return

    # 通常の会話（相手に転送）
    if user_id in chat_sessions:
        partner_id = chat_sessions[user_id]["partner_id"]
        try:
            line_bot_api.push_message(partner_id, TextSendMessage(text=f"お相手からのメッセージ：\n{user_text}"))
            line_bot_api.reply_message(reply_token, TextSendMessage(text="メッセージを転送しました。"))
        except LineBotApiError as e:
            print("LINE送信失敗:", e)
            line_bot_api.reply_message(reply_token, TextSendMessage(text="送信エラーが発生しました。"))
    else:
        # AI通常応答（会話ペアがないとき）
        response = cohere_history.chat2(user_text, chat_history)
        line_bot_api.reply_message(reply_token, TextSendMessage(text=response))

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
