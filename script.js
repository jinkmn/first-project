// script.js

// --- 1. HTML要素の取得 ---
const csvFileInput = document.getElementById("csvFileInput");
const analyzeButton = document.getElementById("analyzeButton");
const loading = document.getElementById("loading");
const resultArea = document.getElementById("resultArea");
const positiveCommentsUl = document.getElementById("positiveComments");
const negativeCommentsUl = document.getElementById("negativeComments");
const dangerCommentsUl = document.getElementById("dangerComments");
const importanceCommentsUl = document.getElementById("importanceComments");
const chartImageElement = document.getElementById("analysisChart");

// --- 2. 「分析開始」ボタンのクリック処理 ---
analyzeButton.addEventListener("click", async () => {
  const file = csvFileInput.files[0];
  if (!file) {
    alert("分析するCSVファイルを選択してください。");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  // UIを「分析中」の状態にする
  loading.style.display = "block";
  resultArea.style.display = "none";

  try {
    // --- 3. サーバーへデータを送信 ---
    const response = await fetch("http://localhost:8080/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`サーバーエラー: ${response.status} ${errorText}`);
    }

    // --- 4. サーバーからのJSON応答を変換 ---
    const results = await response.json();

    // --- 5. 結果を画面に表示 ---
    displayResults(results);
  } catch (error) {
    console.error("分析処理中にエラーが発生しました:", error);
    alert("分析に失敗しました。詳細はコンソールを確認してください。");
  } finally {
    // --- 6. UIの状態を元に戻す ---
    loading.style.display = "none";
    resultArea.style.display = "block";
  }
});

/**
 * サーバーから受け取った分析結果をHTMLに反映させる関数
 * @param {object} results - サーバーから返されたJSONデータ
 */
function displayResults(results) {
  positiveCommentsUl.innerHTML = "";
  negativeCommentsUl.innerHTML = "";
  dangerCommentsUl.innerHTML = "";
  importanceCommentsUl.innerHTML = "";

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
