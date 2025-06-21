function switchAlgo(algo) {
  document.querySelectorAll('.section').forEach(div => div.classList.remove('active-section'));
  document.getElementById(algo + '-section').classList.add('active-section');

  document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
  document.querySelector('.nav-link[href="#"][onclick*="' + algo + '"]').classList.add('active');
}

function runAttack(algo) {
  const logBox = document.getElementById("logBox-" + algo);
  const resultImage = document.getElementById("resultImage-" + algo);

  logBox.textContent = "运行中...\n";
  resultImage.src = "";

  fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm: algo })
  })
  .then(res => res.json())
  .then(data => {
    logBox.textContent += data.output;
    if (data.image) {
      resultImage.src = data.image + "?t=" + Date.now();  // 防缓存
    }
  })
  .catch(err => {
    logBox.textContent += "\n❌ 运行出错: " + err;
  });
}