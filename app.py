import os
import re
import uuid
from flask import Flask, request, render_template, send_file
from analyzer.core import generate_argx_and_heatmap

UPLOAD_FOLDER = "/tmp/uploads"
MAX_PDFS = 5

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def format_pdf_display_name(filename): match = re.search(r"(\d{4}-\d{2}-\d{2})", filename) date_str = match.group(1) if match else "Unknown" return f"ARG_{date_str}.pdf", filename

@app.route("/", methods=["GET", "POST"]) def index(): # === List recent PDFs === recent_pdfs_raw = sorted( [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")], key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True )[:MAX_PDFS] recent_pdfs = [format_pdf_display_name(f) for f in recent_pdfs_raw]

if request.method == "POST":
    uploaded_files = request.files.getlist("pdfs")
    existing_files = request.form.getlist("existing_pdfs")

    all_files = []

    # === Handle new uploads ===
    for file in uploaded_files:
        if file.filename.endswith(".pdf"):
            display_name, _ = format_pdf_display_name(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, display_name)
            if not os.path.exists(save_path):
                file.save(save_path)
            all_files.append(save_path)

    # === Handle existing file selections ===
    for f in existing_files:
        path = os.path.join(UPLOAD_FOLDER, f)
        if os.path.exists(path) and path.endswith(".pdf"):
            all_files.append(path)

    if not all_files:
        return render_template("index.html", error="No valid PDFs selected or uploaded.", recent_pdfs=recent_pdfs)

    # === Generate report ===
    output_files, stats = generate_argx_and_heatmap(all_files)

    if output_files:
        filenames = [os.path.basename(p) for p in output_files]
        return render_template("result.html", filenames=filenames, stats=stats)
    else:
        return render_template("index.html", error="Failed to generate report.", recent_pdfs=recent_pdfs)

return render_template("index.html", recent_pdfs=recent_pdfs)

@app.route("/download/<filename>") def download(filename): file_path = os.path.join("/tmp", filename) if os.path.exists(file_path): return send_file(file_path, as_attachment=True) return "File not found", 404

if __name__ == "__main__": app.run(debug=True)

