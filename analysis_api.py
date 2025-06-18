# analysis_api.py
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib  # matplotlibの日本語文字化けを防ぐためにインポート

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

# FastAPIアプリケーションを初期化
app = FastAPI()

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """
    script.jsからのリクエストを受け取り、CSVを分析し、
    結果（コメントリストとグラフ画像のBase64文字列）をJSONで返す。
    """
    try:
        # --- 1. CSVファイルの読み込みと分析 ---
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if 'comment' not in df.columns:
            return JSONResponse(status_code=400, content={"message": "CSVに 'comment' 列がありません。"})
        
        all_comments = df['comment'].dropna().tolist()
        
        positive_keywords = ['楽しかった', '分かりやすい', '面白い', '満足']
        negative_keywords = ['難しい', '不満', '分からない', '残念']

        positive_comments = [c for c in all_comments if any(key in c for key in positive_keywords)]
        negative_comments = [c for c in all_comments if any(key in c for key in negative_keywords)]

        # --- 2. matplotlibでグラフを生成 ---
        
        # グラフの描画領域を準備
        fig, ax = plt.subplots()

        x = [1,2,3,4,5]
        y = [2,4,6,8,10]

        plt.plot(x,y)
        plt.xlabel("x")
        plt.ylabel("Y")
        plt.title("title")



        # 【重要】グラフをファイルに保存する代わりに、メモリ上のバッファに保存する
        # io.BytesIO() は、メモリ上に一時的なバイナリファイルを作成するようなものです。
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig) # メモリリークを防ぐために、描画した図を明示的に閉じます。

        # --- 3. グラフ画像をBase64形式の文字列にエンコード ---

        # バッファの先頭にポインタを戻し、Base64エンコードを実行
        buf.seek(0)
        # b64encodeはバイトデータを返すので、それをさらにUTF-8の文字列にデコードします。
        # これでJSONに含められる「ただの長い文字列」になります。
        chart_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        positive_comments = "ありがとう"
        negative_comments = "ごめんなさい"


        # --- 4. script.jsが期待する形式でJSONデータを作成 ---
        # JavaScript側でアクセスしたキー名（'positiveComments'など）と完全に一致させる必要があります。
        results = {
            "positiveComments": positive_comments,
            "negativeComments": negative_comments,
            "chartImage": chart_image_base64  # ここにBase64文字列を入れる
        }
        
        return JSONResponse(status_code=200, content=results)

    except Exception as e:
        print(f"エラー発生: {e}") # サーバー側のログに詳細なエラーを出力
        return JSONResponse(status_code=500, content={"message": f"分析中にサーバーでエラーが発生しました: {str(e)}"})