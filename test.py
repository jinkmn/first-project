import google.generativeai as genai
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
# このコードを実行するためには、python-dotenvライブラリが必要です
# pip install python-dotenv
load_dotenv()

try:
    # 環境変数からAPIキーを読み込む
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("APIキーが設定されていません。'.env'ファイルを確認してください。")

    genai.configure(api_key=api_key)

    # 使用するモデルを選択
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Geminiにプロンプトを送信
    prompt = "VS CodeでGeminiのAPIキーを使う方法を簡潔に教えて"
    response = model.generate_content(prompt)

    # 結果を出力
    print(response.text)

except Exception as e:
    print(f"エラーが発生しました: {e}")