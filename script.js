// script.js

// --- 1. HTML要素を取得し、変数に格納 ---
// ボタンやファイル入力、結果表示エリアなど、操作したいHTML要素をあらかじめ取得しておく
const csvFileInput = document.getElementById("csvFileInput");
const analyzeButton = document.getElementById("analyzeButton");
const loading = document.getElementById("loading");
const resultArea = document.getElementById("resultArea");
const positiveCommentsUl = document.getElementById("positiveComments");
const negativeCommentsUl = document.getElementById("negativeComments");
const dangerCommentsUl = document.getElementById("dangerComments");
const importanceCommentsUl = document.getElementById("importanceComments");
const chartImageElement = document.getElementById("analysisChart"); // <img>タグを取得

// --- 2. 「分析開始」ボタンがクリックされたときの処理を登録 ---
analyzeButton.addEventListener("click", async () => {
  // ユーザーが選択したファイルを取得
  const file = csvFileInput.files[0];
  if (!file) {
    alert("分析するCSVファイルを選択してください。");
    return; // ファイルが選択されていなければ処理を中断
  }

  // FormDataオブジェクトを作成し、ファイルを追加
  // これがサーバーに送るデータのかたまりになる
  const formData = new FormData();
  formData.append("file", file); // 'file'というキー名でファイルを設定（Java側で受け取るキー名）

  // UIを「分析中」の状態にする
  loading.style.display = "block";
  resultArea.style.display = "none";

  try {
    // --- 3. fetch APIを使って、Javaサーバーにデータを送信 ---
    // 'http://localhost:8080/api/analyze' はJavaサーバーのエンドポイント（窓口）
    const response = await fetch("http://localhost:8080/api/analyze", {
      method: "POST", // データを送信するのでPOSTメソッドを指定
      body: formData, // 送信するデータ本体
    });

    // サーバーからの応答が成功でなければエラーを投げる
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`サーバーエラー: ${response.status} ${errorText}`);
    }

    // --- 4. サーバーからのJSON応答をJavaScriptオブジェクトに変換 ---
    const results = await response.json();

    // --- 5. 受け取った結果を画面に表示する ---
    displayResults(results);
  } catch (error) {
    // 通信中や処理中にエラーが発生した場合の処理
    console.error("分析処理中にエラーが発生しました:", error);
    alert("分析に失敗しました。詳細はコンソールを確認してください。");
  } finally {
    // --- 6. 成功・失敗にかかわらず、UIの状態を元に戻す ---
    loading.style.display = "none";
    resultArea.style.display = "block";
  }
});

/**
 * サーバーから受け取った分析結果をHTMLに反映させる関数
 * @param {object} results - サーバーから返されたJSONデータ
 */
function displayResults(results) {
  // 以前の結果が残っている可能性があるので、リストを空にする
  positiveCommentsUl.innerHTML = "";
  negativeCommentsUl.innerHTML = "";
  dangerCommentsUl.innerHTML = "";
  importanceCommentsUl.innerHTML = "";

  // 【改善点】リスト表示の処理を共通の関数にまとめる
  const populateList = (ulElement, comments) => {
    if (comments && comments.length > 0) {
      comments.forEach((comment) => {
        const li = document.createElement("li");
        li.textContent = comment;
        ulElement.appendChild(li);
      });
    } else {
      // 該当コメントがない場合のメッセージ
      const li = document.createElement("li");
      li.textContent = "該当するコメントはありませんでした。";
      ulElement.appendChild(li);
    }
  };

  // 作成した関数を使って、各リストをデータで埋める
  populateList(positiveCommentsUl, results.positiveComments);
  populateList(negativeCommentsUl, results.negativeComments);
  // 【修正点】危険度・重要度リストの表示処理を追加
  populateList(dangerCommentsUl, results.dangerComments);
  populateList(importanceCommentsUl, results.importanceComments);

  // グラフ画像を表示
  if (results.chartImage) {
    chartImageElement.src = "data:image/png;base64," + results.chartImage;
    chartImageElement.style.display = "block";
  } else {
    chartImageElement.style.display = "none";
  }
}
