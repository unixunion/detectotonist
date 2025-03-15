import os.path
import os.path
import pickle
import shutil
import subprocess
import time

from flask import Flask, render_template, request, send_file, jsonify
from loguru import logger

from sampler import INPUT_DIR

UNCLASSIFIED_DIR = os.path.join("data", "unclassified")
SAMPLES_DIR = os.path.join("data", "samples")

DEFAULT_TAGS = [
    # Object Types
    "coin",
    "ring",
    "jewelry",
    "ringpull",
    "nail",
    "foil",
    "bottlecap",
    "key",

    # Metals / Materials
    "gold",
    "silver",
    "aluminium",
    "copper",
    "iron",
    "hotrock",
    "utensil",
    "noise",
]

AVAILABLE_TAGS = DEFAULT_TAGS
TAGS_FILE = "tags.pkl"

try:
    with open(TAGS_FILE, 'rb') as f:
        AVAILABLE_TAGS = pickle.load(f)
except Exception as e:
    with open(TAGS_FILE, 'wb') as f:
        pickle.dump(AVAILABLE_TAGS, f)

app = Flask(__name__)


@app.route("/tags", methods=["GET"])
def get_tags():
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})

@app.route("/tags/add/<tag>", methods=["POST"])
def add_tag(tag):
    if tag in AVAILABLE_TAGS:
        AVAILABLE_TAGS.remove(tag)
    AVAILABLE_TAGS.append(tag)
    with open(TAGS_FILE, 'wb') as f:
        pickle.dump(AVAILABLE_TAGS, f)
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})

@app.route("/tags/del/<tag>", methods=["POST"])
def del_tag(tag):
    if tag in AVAILABLE_TAGS:
        AVAILABLE_TAGS.remove(tag)
        with open("tags.pkl", 'wb') as f:
            pickle.dump(AVAILABLE_TAGS, f)
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})



@app.route("/next_filter_file")
def next_filter_file():
    """Return the next file available for filtering."""
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".png"))
    if not files:
        return jsonify({"status": "no_files"})

    base, _ = os.path.splitext(files[0])
    return jsonify({
        "status": "ok",
        "spectrogram": f"/api/files/input/{files[0]}",
        "audio": f"/api/files/input/{base}.wav",
        "filename": files[0]
    })


@app.route("/next_classify_file")
def next_classify_file():
    """Return the next file available for classification."""
    files = sorted(f for f in os.listdir(UNCLASSIFIED_DIR) if f.endswith(".png"))
    if not files:
        return jsonify({"status": "no_files"})

    base, _ = os.path.splitext(files[0])
    return jsonify({
        "status": "ok",
        "spectrogram": f"/api/files/classify/{files[0]}",
        "audio": f"/api/files/classify/{base}.wav",
        "filename": files[0],
        "tags": AVAILABLE_TAGS
    })


@app.route("/samples")
def samples():
    """Return all the sample files."""
    files = sorted(f for f in os.listdir(SAMPLES_DIR) if f.endswith(".png"))
    if not files:
        return jsonify({"status": "no_files"})

    return jsonify({
        "status": "ok",
        "files": files
    })


@app.route("/files/input/<filename>")
def serve_input_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(INPUT_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)


@app.route("/files/classify/<filename>")
def serve_classify_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(UNCLASSIFIED_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)

@app.route("/files/samples/<filename>")
def serve_samples_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(SAMPLES_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)


@app.route("/shutdown", methods=["POST"])
def shutdown():
    try:
        subprocess.Popen(["sudo", "/sbin/shutdown", "-h", "now"])
        return "Shutting Down...", 200
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/filter", methods=["GET"])
def filter():
    """
    Displays samples in the first input / capture stage, where we decide which samples to keep
    or discard for later classifying
    """
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".png")])
    if not files:
        return """
            <h1 style='margin: 20px;'>No files left to classify: %s</h1>
            <script>
                setTimeout(function() {
                    location.reload();
                }, 5000);
            </script>
            <form action="/shutdown" method="post">
                <button type="submit">
                Shutdown
                </button>
            </form>
            """ % time.time()

    audio_file, _ = os.path.splitext(files[0])

    return render_template("index.html", filename=files[0], tags=AVAILABLE_TAGS, audiofile=f"{audio_file}.wav")


# **Capture Data View**
@app.route("/capture")
def capture():
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".png")])
    return render_template(
        "index.html",
        active_tab="capture",
        filename=files[0] if files else None,
        audiofile=f"{os.path.splitext(files[0])[0]}.wav" if files else None,
        capture_files=files
    )


@app.route("/filter", methods=["POST"])
def do_filter():
    """Process accepted/rejected files from filtering view."""
    data = request.json
    filename = data.get("filename")
    status = data.get("status")

    if not filename or not status:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    base, _ = os.path.splitext(filename)
    for ext in ["png", "npy", "wav"]:
        file_path = os.path.join(INPUT_DIR, f"{base}.{ext}")
        if os.path.exists(file_path):
            if status == "accept":
                shutil.move(file_path, os.path.join(UNCLASSIFIED_DIR, f"{base}.{ext}"))
            else:
                os.remove(file_path)

    return jsonify({"status": "ok", "message": "File filtered", "nextFileUrl": "/next_capture_file"})


@app.route("/classify", methods=["POST"])
def do_classify():
    """Process classification results and move file to training data."""
    logger.info("doing classify")
    data = request.json
    logger.info(f"Do classify: {data}")
    filename = data.get("filename")
    status = data.get("status")
    tags = data.get("tags", [])

    if not filename or not status or not tags:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    base, _ = os.path.splitext(filename)
    tag_prefix = "_".join(tags)
    new_filename = f"{status}_{tag_prefix}_{base}"

    for ext in ["png", "npy", "wav"]:
        old_path = os.path.join(UNCLASSIFIED_DIR, f"{base}.{ext}")
        new_path = os.path.join(SAMPLES_DIR, f"{new_filename}.{ext}")
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)

    return jsonify({"status": "ok", "message": "File classified", "nextFileUrl": "/next_classify_file"})


@app.route("/samples/delete/<filename>", methods=["POST"])
def delete_sample(filename):
    """delete sample."""
    logger.info(f"deleting sample: {filename}")

    if not filename:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    base, _ = os.path.splitext(filename)
    for ext in ["png", "npy", "wav"]:
        os.remove(os.path.join(SAMPLES_DIR, f"{base}.{ext}"))

    return jsonify({"status": "ok", "message": f"File deleted: {filename}"})



@app.route("/samples/reclassify/<filename>", methods=["POST"])
def reclassify_sample(filename):
    """Move a classified sample back to the unclassified directory for reclassification."""
    logger.info(f"Reclassifying sample: {filename}")

    if not filename:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    base, _ = os.path.splitext(filename)

    # Extract the original file ID (everything after the last underscore)
    parts = base.split("_")
    if len(parts) < 2:
        return jsonify({"status": "error", "message": "Invalid filename format"}), 400

    new_filename = parts[-1]  # The last part is the original unique file ID

    for ext in ["png", "npy", "wav"]:
        old_path = os.path.join(SAMPLES_DIR, f"{base}.{ext}")
        new_path = os.path.join(UNCLASSIFIED_DIR, f"{new_filename}.{ext}")
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)

    return jsonify({"status": "ok", "message": f"File moved back for reclassification: {new_filename}"})





if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
