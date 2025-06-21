from flask import Flask, request, jsonify, render_template, Response, stream_with_context
import subprocess
import shutil
import os

app = Flask(__name__)
app.config['STATIC_FOLDER'] = "static"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream/<string:algo>")
def stream(algo):
    def generate():
        script = f"algorithms/{algo}.py"
        proc = subprocess.Popen(
            ["python", '-u', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in proc.stdout:
            yield f"data: {line.rstrip()}\n\n"
        yield "event: done\ndata: end\n\n"

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
