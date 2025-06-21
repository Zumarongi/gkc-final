function switchAlgo(algo) {
  document.querySelectorAll('.section').forEach(div => div.classList.remove('active-section'));
  document.getElementById(algo + '-section').classList.add('active-section');

  document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
  document.querySelector('.nav-link[href="#"][onclick*="' + algo + '"]').classList.add('active');
}

function runAttack(algo) {
  const btn = document.getElementById("run-btn-" + algo);
  const logBox = document.getElementById("logBox-" + algo);
  const examplesImage = document.getElementById("examplesImage-" + algo);
  const effectImage = document.getElementById("effectImage-" + algo);

  btn.disabled = true;
  btn.innerHTML = `
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    运行中...
  `;

  logBox.textContent = "";
  examplesImage.src = "";
  effectImage.src = "";

  const source = new EventSource(`/stream/${algo}`);

  source.onmessage = function(e) {
    logBox.textContent += e.data + "\n";
    logBox.scrollTop = logBox.scrollHeight;
  };

  source.addEventListener("done", function(e) {
    source.close();
    btn.disabled = false;
    btn.innerHTML = `▶️ 运行 ${algo} 算法`;
    examplesImage.src = `/static/img/${algo}/${algo}_examples.png?t=${Date.now()}`;
    effectImage.src = `/static/img/${algo}/${algo}_effect.png?t=${Date.now()}`;
  });
}