import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import shutil
import zipfile
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from generator import generate_diagram

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

# Configurable paths
UPLOAD_BASE = "uploads"
OUTPUT_BASE = "outputs"

# Ensure folders exist
os.makedirs(UPLOAD_BASE, exist_ok=True)
os.makedirs(OUTPUT_BASE, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'files' not in request.files:
            flash('No files part in request.')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        if not files or files[0].filename == "":
            flash('No selected files.')
            return redirect(request.url)

        # ✅ Get requested image format from form
        image_format = request.form.get('format', 'png').lower()
        if image_format not in ["png", "svg"]:
            image_format = "png"

        # ✅ Get requested scale factor from form
        scale_factor = request.form.get('scale', '2').strip()
        if not scale_factor.isdigit() or int(scale_factor) < 1:
            scale_factor = "2"

        # ✅ Create new upload folder for this request
        upload_folder = os.path.join(UPLOAD_BASE, "input")
        if os.path.exists(upload_folder):
            shutil.rmtree(upload_folder)
        os.makedirs(upload_folder)

        # ✅ Handle ZIP vs multiple JSON files
        if len(files) == 1 and files[0].filename.lower().endswith('.zip'):
            print("✅ Detected ZIP file upload.")
            try:
                with zipfile.ZipFile(files[0]) as zf:
                    zf.extractall(upload_folder)
                print(f"✅ Extracted ZIP to: {upload_folder}")
            except zipfile.BadZipFile:
                flash('Uploaded file is not a valid ZIP archive.')
                return redirect(request.url)
        else:
            print("✅ Detected multiple JSON files upload.")
            for f in files:
                filename = secure_filename(f.filename)
                f.save(os.path.join(upload_folder, filename))

        # ✅ Call generator
        try:
            result_folder = generate_diagram(
                input_dir=upload_folder,
                output_base_dir=OUTPUT_BASE,
                image_format=image_format,
                scale=scale_factor
            )
        except Exception as e:
            flash(f"Error generating diagram: {e}")
            return redirect(request.url)

        # ✅ Find generated image
        generated_files = os.listdir(result_folder)
        image_file = next((f for f in generated_files if f.endswith(f".{image_format}")), None)

        if not image_file:
            flash(f"No diagram image was generated in {image_format} format.")
            return redirect(request.url)
        
        # ✅ Build URL-safe download path
        download_path = f"{os.path.basename(result_folder)}/{image_file}"
        return redirect(url_for('download_file', path=download_path))

    return render_template("index.html")

@app.route("/download/<path:path>")
def download_file(path):
    directory = os.path.join(OUTPUT_BASE)
    return send_from_directory(directory, path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

