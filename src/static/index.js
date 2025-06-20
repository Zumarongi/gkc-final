function runAttack() {
  const algo = document.getElementById("algorithm").value;
  document.getElementById("logBox").textContent = "运行中...\n";
  document.getElementById("resultImage").src = "";

  fetch("/run", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ algorithm: algo })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("logBox").textContent += data.output;
    if (data.image) {
      document.getElementById("resultImage").src = data.image + "?t=" + Date.now();  // 防缓存
    }
  });
}