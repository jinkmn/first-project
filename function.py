import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key) 
model = genai.GenerativeModel('gemini-1.5-flash-latest')


def classify_comments(comments: list[str] | pd.Series) -> dict:

    if not isinstance(comments, list):
        comments = comments.to_list()

    if not comments:
        print("分析対象のコメントがありません。")
        return None
    
    # プロンプトのテンプレート
    prompt_template = """
あなたは、講義アンケートのコメントを分析する専門のアナリストです。
これからJSON形式で渡されるコメントのリストを分析し、以下のルールに従って結果を一つのJSONオブジェクトとして出力してください。

# 全体のルール
- あなたの応答は、解説や前置きなしに、指定されたJSONフォーマットのコードブロックのみにしてください。
- 入力されたコメントのインデックス番号は0から始まります。

# 分類ルール
各コメントに対して、以下の2つの分類を行ってください。
1.  **sentiment**: コメントの感情を分析し、以下のいずれかの数値を割り当ててください。
    - `0`: ポジティブ
    - `1`: ネガティブ
    - `2`: どちらでもない
2.  **topic**: コメントが何についての言及か、以下のカテゴリに分類してください。
    - `0`: 講義内容について
    - `1`: 講義資料について
    - `2`: 運営について
    - `3`: 講師について
    - `4`:チャットボットについて
    - `5`:その他

# 重要コメントの抽出ルール
コメント全体をレビューし、以下の基準の**いずれか1つ以上に合致する**コメントを「重要コメント」と判断し、そのインデックス番号（0から始まる番号）をリストにまとめてください。
- 複数回（目安として3回以上）言及されている共通の改善点が含まれている。
- 緊急の対応が必要と思われる内容（例：システム障害、重大な誤り）が含まれている。
- 具体的な改善案が含まれている。

# 危険コメントの抽出ルール
コメント全体をレビューし、以下の基準に合致するコメントのインデックス番号を特定し、リストに追加してください。
- **dangerous**: 誹謗中傷、人格攻撃、違法行為を示唆するような不適切な内容を含むコメントのインデックス。

# 出力フォーマット
以下のJSON構造を厳守してください。"important_comments"と"dangerous_comments"の値は、インデックス番号の配列（リスト）です。

{
  "classifications": [
    {
      "comment_index": 0,
      "sentiment": 0,
      "topic": "1"
    },
    {
      "comment_index": 1,
      "sentiment": 1,
      "topic": "3"
    }
  ],
  "important_comments": [15, 22, 28],
  "dangerous_comments": [45]
}

---
それでは、以下のコメントリストを分析してください。

【入力コメントリスト】
"""

    comment_list_str = json.dumps(comments, ensure_ascii=False)
    prompt = prompt_template + comment_list_str
    
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        analysis_result = json.loads(clean_response)
        return analysis_result
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


def summarize_comments(positive_list: list, negative_list: list) -> dict | None:
    """
    ポジティブとネガティブのコメントリストを要約する関数
    """
    
    # プロンプトのテンプレート
    prompt_template = """
あなたは、顧客からのフィードバックを分析し、要点を簡潔にまとめるプロのテキストアナリストです。
これからポジティブなコメントのリストとネガティブなコメントのリストをJSON形式で渡します。

それぞれのリストについて、似たような意見をグループ化し、内容を要約してください。
要約は、それぞれの感情カテゴリ（ポジティブ・ネガティブ）ごとに、最大5個の箇条書きにまとめてください。

# 指示
1.  `positive_comments` のリストを読み込み、主な意見や感想を要約してください。
2.  `negative_comments` のリストを読み込み、主な不満点や改善要望を要約してください。
3.  要約は、具体的かつ簡潔にしてください。
4.  全体の意見を網羅し、特に多く言及されている点を優先してください。
5.  以下のJSONフォーマットを厳守し、解説や前置きなしにJSONオブジェクトのみを出力してください。

# 出力フォーマット
{
  "positive_summary": [
    "箇条書きの要約1",
    "箇条書きの要約2",
    "..."
  ],
  "negative_summary": [
    "箇条書きの要約1",
    "箇条書きの要約2",
    "..."
  ]
}

---
それでは、以下のコメントリストを分析してください。
"""

    positive_comment_list_str = json.dumps(positive_list, ensure_ascii=False)
    negative_comment_list_str = json.dumps(negative_list, ensure_ascii=False)


    prompt = prompt_template + 'positive_comments:' + positive_comment_list_str + \
    ', negative_comments:' + negative_comment_list_str

    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        summary = json.loads(clean_response)
        return summary
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def summarize_important_comments(comments: list[dict]) -> dict | None:
    """
    重要コメントのリストを受け取り、優先順位付けされた要約を返す関数
    """
    if not comments:
        print("要約する重要コメントがありません。")
        return None

    prompt_template = """
    あなたは、大量の顧客フィードバックを分析し、改善のためのアクションアイテムを優先順位付けする、経験豊富なプロダクトマネージャーです。

これから、重要だと判断されたコメントのリストをJSON形式で受け取ります。あなたのタスクは、これらのコメントを総合的にレビューし、最も対応すべき優先度の高い課題をトップ5まで特定し、要約してランキング形式で出力することです。

# 分析と優先順位付けのルール
1.  **内容の理解とグルーピング**: まず、全てのコメントを読み、内容の似ているもの（例：「音声が途切れる」「音が聞こえない」）を心の中でグループ化します。
2.  **優先度の決定**: 以下の基準に従って、各グループの優先度を決定してください。
    * **優先度1 (最高)**: **緊急性の高い問題**。サービスの利用を妨げる致命的な障害や、重大な間違いの指摘（例：「動画が再生できない」「ログインできない」）。
    * **優先度2 (高)**: **頻出の意見・要望**。複数のユーザーから繰り返し指摘されている問題や改善案（例：「もっと演習時間が欲しい」という声が多数）。
    * **優先度3 (中)**: **具体的な改善提案**。たとえ一人からの意見でも、具体的で実行可能な改善案（例：「各章の最後にまとめのスライドを追加してほしい」）。
    * **優先度4 (低)**: 上記以外の一般的な意見。

# 出力フォーマット
- 分析結果を以下のJSONフォーマットで出力してください。
- `priority`は1から始まる整数、`summary`はその課題や提案を簡潔にまとめた一文です。
- `indices`には、その要約の根拠となった元のコメントのインデックス番号をリストで含めてください。
- 全体で最大5つの項目を、優先度の高い順に並べてください。
- あなたの応答は、解説や前置きなしに、JSONオブジェクトのみにしてください。

{
  "ranked_summary": [
    {
      "priority": 1,
      "summary": "動画の再生に関する技術的な問題が発生しており、緊急の対応が必要です。",
      "indices": [2, 18, 45]
    },
    {
      "priority": 2,
      "summary": "講義の進行速度が速すぎるため、ついていけないという意見が多数寄せられています。",
      "indices": [6, 11, 23, 31]
    },
    {
      "priority": 3,
      "summary": "演習問題の解答例を提供してほしいという具体的な要望があります。",
      "indices": [22]
    }
  ]
}

---
それでは、以下の重要コメントリストを分析し、優先順位をつけて要約してください。
【本番】
"""
    comment_list_str = json.dumps(comments, ensure_ascii=False)

    # プレースホルダーを置換
    # f-stringを使うと{}のエスケープが面倒なので、ここでは .format() を使います
    # プロンプト内の例示JSONの { と } は {{ }} にエスケープしておく必要があります
    prompt = prompt_template + comment_list_str

    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        summary = json.loads(clean_response)
        return summary
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None