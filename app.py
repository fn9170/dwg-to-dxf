from flask import Flask, request, jsonify, send_file
import os, uuid, subprocess

UPLOAD_FOLDER = "/tmp/uploads"
OUTPUT_FOLDER = "/tmp/outputs"
ODA_APP = "/opt/ODAFileConverter.appimage"

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".dwg"):
        return jsonify({"error": "请上传 .dwg 文件"}), 400

    task_id = str(uuid.uuid4())
    input_dir = os.path.join(UPLOAD_FOLDER, task_id)
    output_dir = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(input_dir)
    os.makedirs(output_dir)

    input_path = os.path.join(input_dir, file.filename)
    file.save(input_path)

    cmd = [ODA_APP, input_dir, output_dir, "DXF", "R2013", "0"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "转换失败", "details": str(e)}), 500

    base = os.path.splitext(file.filename)[0]
    dxf_path = os.path.join(output_dir, base + ".dxf")
    if not os.path.exists(dxf_path):
        return jsonify({"error": "未找到 DXF 输出文件"}), 500

    return send_file(dxf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)