from flask import Flask, request, jsonify, render_template, send_from_directory
import subprocess
import shutil
import os

app = Flask(__name__)
app.config['STATIC_FOLDER'] = "static"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_algorithm():
    data = request.get_json()
    algo = data.get("algorithm")

    if algo not in ["PGD", "PGD_L2", "FGSM", "CW", "MIM", "RFGSM"]:
        return jsonify({"output": "无效算法", "image": None})

    script = f"algorithms/{algo}.py"

    try:
        # 运行脚本并捕获终端输出
        result = subprocess.run(
            ["python", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            timeout=60
        )
        output = result.stdout
    except Exception as e:
        output = f"运行出错: {str(e)}"
        return jsonify({"output": output, "image": None})

    # 假设图片保存在 outputs/fgsm_result.png
    img_name = f"{algo}_result.png"
    src_img_path = os.path.join("outputs", img_name)
    dst_img_path = os.path.join(app.config['STATIC_FOLDER'], "result.png")

    if os.path.exists(src_img_path):
        shutil.copyfile(src_img_path, dst_img_path)
        img_url = "/static/result.png"
    else:
        img_url = None

    return jsonify({"output": output, "image": img_url})

if __name__ == "__main__":
    app.run(debug=True)
