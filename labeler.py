import os.path
import shutil
from loguru import logger
from flask import Flask, render_template, request, redirect, url_for, send_file
import time
import subprocess

from sampler import INPUT_DIR


READY_FOR_CLASSIFICATION_DIR = os.path.join("data", "samples")
READY_FOR_TRAINING_DIR = os.path.join("data", "train")

AVAILABLE_TAGS = [
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
app = Flask(__name__)


@app.route("/files/input/<filename>")
def serve_input_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(INPUT_DIR, filename)
    return send_file(file_path)


@app.route("/files/classify/<filename>")
def serve_classify_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(READY_FOR_CLASSIFICATION_DIR, filename)
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


@app.route("/")
def classify():
    files = sorted([f for f in os.listdir(READY_FOR_CLASSIFICATION_DIR) if f.lower().endswith(".png")])
    return render_template(
        "index.html",
        active_tab="classify",
        filename=files[0] if files else None,
        audiofile=f"{os.path.splitext(files[0])[0]}.wav" if files else None,
        classify_files=files,
        tags=AVAILABLE_TAGS
    )

@app.route("/system")
def system():
    return render_template("index.html", active_tab="system")

@app.route("/classify", methods=["POST"])
def do_classify():
    """Handles the form submission to classify a file, moves and renames the file"""

    selected_status = request.form.get("status")
    selected_tags = request.form.getlist("tags")
    original_file = request.form.get("filename")

    if not original_file or not selected_status or not selected_tags:
        return redirect(url_for("index"))

    logger.info(f"Classify {original_file} as {selected_status} with tags: {selected_tags}")

    base, _ = os.path.splitext(original_file)

    if selected_tags:
        tag_prefix = "_".join(selected_tags)
        new_filename = f"{selected_status}_{tag_prefix}_{base}"

        for ext in "png", "npy", "wav":
            # Full paths to move from / to
            source_file = f"{base}.{ext}"
            dest_file = f"{new_filename}.{ext}"

            old_path = os.path.join(READY_FOR_CLASSIFICATION_DIR, source_file)
            new_path = os.path.join(READY_FOR_TRAINING_DIR, dest_file)

            # Move (rename) the file from INPUT_DIR to OUTPUT_DIR
            shutil.move(old_path, new_path)

    return redirect(url_for("classify"))



@app.route("/filter", methods=["POST"])
def do_filter():
    """Handles the form submission to classify a file, moves and renames the file"""

    selected_status = request.form.get("status")
    original_file = request.form.get("filename")

    if not original_file or not selected_status:
        return redirect(url_for("filter"))

    logger.info(f"Classify {original_file} as {selected_status}")

    base, _ = os.path.splitext(original_file)

    if selected_status:
        new_filename = f"{base}"

        for ext in "png", "npy", "wav":
            # Full paths to move from / to
            source_file = f"{base}.{ext}"
            dest_file = f"{new_filename}.{ext}"

            old_path = os.path.join(INPUT_DIR, source_file)
            new_path = os.path.join(READY_FOR_CLASSIFICATION_DIR, dest_file)

            # Move (rename) the file from INPUT_DIR to OUTPUT_DIR
            if selected_status == "accept":
                logger.info(f"Moving {old_path} to {new_path}")
                shutil.move(old_path, new_path)
            else:
                logger.info(f"Deleting: {old_path}")
                os.remove(old_path)

    return redirect(url_for("capture"))



if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
