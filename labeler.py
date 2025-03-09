import os.path
import shutil
from loguru import logger
from flask import Flask, render_template, request, redirect, url_for, send_file

from sampler import INPUT_DIR

OUTPUT_DIR = os.path.join("data", "train")
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
]
app = Flask(__name__)


@app.route("/files/<filename>")
def serve_file(filename):
    # Validate / sanitize 'filename' to prevent security issues
    file_path = os.path.join(INPUT_DIR, filename)
    return send_file(file_path)


@app.route("/", methods=["GET"])
def index():
    """
    Displays the first file in INPUT_DIR so the user can classify it.
    """
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".png")])
    if not files:
        return "<h1 style='margin: 20px;'>No files left to classify!</h1>"

    audio_file, _ = os.path.splitext(files[0])

    return render_template("index.html", filename=files[0], tags=AVAILABLE_TAGS, audiofile=f"{audio_file}.wav")


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

            old_path = os.path.join(INPUT_DIR, source_file)
            new_path = os.path.join(OUTPUT_DIR, dest_file)

            # Move (rename) the file from INPUT_DIR to OUTPUT_DIR
            shutil.move(old_path, new_path)

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
