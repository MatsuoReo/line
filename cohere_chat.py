# cohere_chat.py
import cohere
import os
import subprocess

# ユーザー入力に応じてチャットする関数
def chat(user_input):
    # COHEREのAPIキーを環境変数から取得する
    co = cohere.Client(os.environ.get("COHERE_API_KEY"))

    # 会話の履歴（最初に初期設定のシステムプロンプトを書いておく）
    chat_history = [
        {
            "role": "CHATBOT",
            "message": "あなたはマッチングサービスです。お客様の要望に応じて、気の合う相手の名前を出力してください。"
        },
        {
            "role": "USER",
            "message": user_input
        },
    ]

    # COHEREのサーバにリクエストを送りレスポンスを取得する
    response = co.chat(
        message=user_input,
        chat_history=chat_history,
        model="command-r",
    )
    return response.text

# 簡単な対話ループ
if __name__ == "__main__":
    print("CHATBOTへようこそ！Enterで終了するやで。")
    while True:
        user_input = input("You: ") # 入力を促す表示
        if user_input == "": # 何も入力されなければ終了
            break
        response = chat(user_input)  # サーバに問い合わせ
        print("CHATBO T: ", response) # レスポンスを表示
        # しゃべらせてみる（以下の1行のコメントを外す）
        ### subprocess.Popen(["say", response])
