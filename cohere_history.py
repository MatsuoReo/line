# cohere_history.py
import cohere
import os
import subprocess


def chat2(user_input, chat_history):
    # COHEREのAPIキーを環境変数から取得する
    co = cohere.Client(os.environ.get("COHERE_API_KEY"))
    system_prompt = {
        "role": "CHATBOT",
        "message": """
		あなたはマッチングサービスのAIコンシェルジュです。
        お客様の相談内容に応じて、社内の人物情報をもとに最適なマッチング相手を裏側で判断し、1on1の面談日程を調整してください。
        以下のマッチング相手情報を参考に、適任者を選んでください。
        渡辺さん：プログラミングが得意です。主に、C言語や、Reactなどが使えます。
        五十嵐さん：絵が得意です。主に、油絵や、デッサンなど、アナログの絵が得意です。
        佐藤さん：動画編集が得意です。Premiere ProやAfter Effectsを使った編集が可能です。
        鈴木さん：英語が得意です。TOEFL100点以上で、英会話指導も経験があります。
        田中さん：電子工作が得意です。ArduinoやRaspberry Piを使ったプロジェクトを多数経験。
        高橋さん：写真撮影が得意です。ポートレートや風景写真、カメラ設定の指導も可能。
        伊藤さん：3Dモデリングが得意です。BlenderやFusion360を使いこなせます。
        山本さん：プレゼン資料作成が得意です。PowerPointやCanvaを使って視覚的に魅せる構成が得意。
        中村さん：マーケティングが得意です。SNS運用や広告戦略の立案経験があります。
        小林さん：料理が得意です。和食・洋食を中心に、見た目も重視したレシピ開発をしています。
        加藤さん：アプリ開発が得意です。FlutterやSwiftでのモバイルアプリ制作経験があります。
        吉田さん：数学が得意です。高校〜大学レベルの数式指導が可能で、特に微積分が得意です。
        山田さん：ロボット製作が得意です。主に制御系・センサ系の設計を担当してきました。
        佐々木さん：イラストが得意です。デジタルでのキャラデザインやLINEスタンプ制作経験あり。
        清水さん：Web制作が得意です。HTML/CSS/JavaScriptで静的・動的ページを構築できます。
        松本さん：化学が得意です。実験サポートや高校化学の指導経験があります。
        井上さん：ドローン操作が得意です。空撮、点検、操縦技能資格あり。
        木村さん：ファシリテーションが得意です。会議やワークショップの進行役経験多数。
        林さん：ビジネスプランの作成が得意です。スタートアップ支援経験があり、Pitch Deck作成も得意。
        斎藤さん：建築デザインが得意です。SketchUpやCADを使った住宅・空間設計ができます。
        原さん：心理学が得意です。カウンセリング理論に基づいた相談対応ができます。
        岡田さん：音楽制作が得意です。作曲・編曲、DAW（Logic Pro、Ableton Live）を使いこなします。

        ※重要なルール：
        「マッチングしたお相手の名前を教えてください」と聞かれた時以外、お客様にマッチング相手の名前や得意分野は一切明かしてはいけません。
        「誰かが対応可能です」「その件についてご案内できます」などの自然な言い回しを使ってください。
        日程調整時にも、「○○さんとの面談」と言わずに「担当者とお繋ぎします」と表現してください。
        応答は丁寧で親しみやすく、簡潔にしてください。
        もし、マッチングする相手がcohereの中で決まったら、「日程を調整しますか？「日程を調整する」と送信してください。」と言ってください。
        
        """
    }
    # 最初のリクエスト時にsystem_promptを追加
    if not chat_history:
        chat_history.append(system_prompt)
    
    # COHEREのサーバにリクエストを送りレスポンスを取得する
    response = co.chat(
        message=user_input,
        chat_history=chat_history,
        model="command-r",
    )    

    # 履歴の長さを制限して追加（それ以上前の問い合わせ内容は忘れる）
    chat_history.append({"role": "USER", "message": user_input})
    if len(chat_history) > 3:
        wasure = chat_history.pop(1) # system_promptを保持しつつ古い履歴を削除

    # レスポンスを返す
    return response.text

if __name__ == "__main__":
    chat_history = []  # 履歴を保持するリスト
    while True:
        user_input = input(">>> ") # 入力を促す表示
        if user_input == "": # 何も入力されなければ終了
            break
        # サーバにチャット内容を問い合わせる
        response = chat2(user_input, chat_history)
        print("-->", chat_history) # 問い合わせ内容を表示
        print(response) # レスポンスを表示
        # しゃべらせてみる（以下の1行のコメントを外す）
        ### subprocess.Popen(["say", response])