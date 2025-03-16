import os.path
import os.path
import pickle
import shutil
import subprocess
import threading

from flask import Flask, render_template, request, send_file, jsonify
from loguru import logger

from sampler import AudioClassifierApp

INPUT_DIR = os.path.join("data", "input")
UNCLASSIFIED_DIR = os.path.join("data", "unclassified")
SAMPLES_DIR = os.path.join("data", "samples")
API_PREFIX="/api" # when testing, this should be just "" since dont have a rewrite rule yet
# API_PREFIX="" # when testing, this should be just "" since dont have a rewrite rule yet
LATEST_X_FILES=8

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

sampler = AudioClassifierApp()

def run_sampler():
    """Runs the sampler in a separate thread."""
    sampler.run()

# Start sampler in a separate thread when the script starts
sampler_thread = threading.Thread(target=run_sampler, daemon=True)
sampler_thread.start()

@app.route(f"{API_PREFIX}/sampler/toggle", methods=["POST"])
def toggle_sampling():
    """Toggle audio sampling without stopping the app."""
    data = request.json
    state = data.get("active")

    if state is None or not isinstance(state, bool):
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    sampler.sampling_active = state
    logger.info(f"Sampling {'activated' if state else 'paused'}.")

    return jsonify({"status": "ok", "message": f"Sampling {'activated' if state else 'paused'}"})


@app.route(f"{API_PREFIX}/recalibrate", methods=["POST"])
def recalibrate():
    """recalibrate"""
    global sampler
    sampler.calibrated = False
    sampler.calibrating = False
    sampler.calibration_start_time = None
    sampler.calibration_data = []
    logger.info(f"Recalibrating")
    return jsonify({"status": "ok"})


@app.route(f"{API_PREFIX}/calibration", methods=["GET"])
def recalibrate():
    """recalibrate"""
    global sampler
    logger.info(f"Returning calibration data")
    return jsonify({"status": "ok", "noise_threshold": sampler.calibrated_noise_threshold, "silence_threshold": sampler.calibrated_silence_threshold})




@app.route(f"{API_PREFIX}/sampler/status", methods=["GET"])
def sampler_status():
    global sampler_thread
    """Check if sampler is running and if sampling is active."""
    return jsonify({
        "status": "running" if sampler_thread and sampler_thread.is_alive() else "stopped",
        "sampling_active": sampler.sampling_active
    })


@app.route(f"{API_PREFIX}/tags", methods=["GET"])
def get_tags():
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})

@app.route(f"{API_PREFIX}/tags/add/<tag>", methods=["POST"])
def add_tag(tag):
    if tag in AVAILABLE_TAGS:
        AVAILABLE_TAGS.remove(tag)
    AVAILABLE_TAGS.append(tag)
    with open(TAGS_FILE, 'wb') as f:
        pickle.dump(AVAILABLE_TAGS, f)
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})

@app.route(f"{API_PREFIX}/tags/del/<tag>", methods=["POST"])
def del_tag(tag):
    if tag in AVAILABLE_TAGS:
        AVAILABLE_TAGS.remove(tag)
        with open("tags.pkl", 'wb') as f:
            pickle.dump(AVAILABLE_TAGS, f)
    return jsonify({"status": "ok", "tags": AVAILABLE_TAGS})



@app.route(f"{API_PREFIX}/next_filter_file")
def next_filter_file():
    """Return the next file available for filtering."""
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".png"))
    if not files:
        return jsonify({"status": "no_files"})

    base, _ = os.path.splitext(files[0])
    return jsonify({
        "status": "ok",
        "spectrogram": f"/api/files/input/{base}.png",
        "audio": f"/api/files/input/{base}.wav",
        "filename": files[0]
    })


@app.route(f"{API_PREFIX}/next_classify_file")
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


@app.route(f"{API_PREFIX}/samples")
def samples():
    """Return all the sample files."""
    # List all .png files and sort them by modified time (latest first)
    files = sorted(
        (f for f in os.listdir(SAMPLES_DIR) if f.endswith(".png")),
        key=lambda f: os.path.getmtime(os.path.join(SAMPLES_DIR, f)),
        reverse=True  # Latest files first
    )[:LATEST_X_FILES]  # Get only the latest X files

    if not files:
        return jsonify({"status": "no_files"})

    return jsonify({
        "status": "ok",
        "files": files
    })


@app.route(f"{API_PREFIX}/files/input/<filename>")
def serve_input_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(INPUT_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)


@app.route(f"{API_PREFIX}/files/classify/<filename>")
def serve_classify_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(UNCLASSIFIED_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)

@app.route(f"{API_PREFIX}/files/samples/<filename>")
def serve_samples_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(SAMPLES_DIR, filename)
    logger.info(f"accessing file: {file_path}")
    return send_file(file_path)


@app.route(f"{API_PREFIX}/shutdown", methods=["POST"])
def shutdown():
    try:
        subprocess.Popen(["sudo", "/sbin/shutdown", "-h", "now"])
        return "Shutting Down...", 200
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route(f"{API_PREFIX}/filter", methods=["POST"])
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


@app.route(f"{API_PREFIX}/classify", methods=["POST"])
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


@app.route(f"{API_PREFIX}/samples/delete/<filename>", methods=["POST"])
def delete_sample(filename):
    """delete sample."""
    logger.info(f"deleting sample: {filename}")

    if not filename:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    base, _ = os.path.splitext(filename)
    for ext in ["png", "npy", "wav"]:
        os.remove(os.path.join(SAMPLES_DIR, f"{base}.{ext}"))

    return jsonify({"status": "ok", "message": f"File deleted: {filename}"})



@app.route(f"{API_PREFIX}/samples/reclassify/<filename>", methods=["POST"])
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
    app.run(debug=True, use_reloader=False, port=8080, host='0.0.0.0')
