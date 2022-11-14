
import subprocess

import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
import tempfile

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True
app.secret_key = "MyUniqueSecret"


app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # print("this is the main test"+request.form.get("quality"))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            outputFile = filename.split(
                ".")[0]+"-compressed"+"."+filename.split(".")[1]
            inputfile = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            outputf = os.path.join(app.config['UPLOAD_FOLDER'], outputFile)
            compressImage(inputfile, outputf, request.form.get(
                "quality"), request.form.get("gsblur"), request.form.get("colorspace"))
            return render_template("index.html", msg="Image processed successfully", original_file=url_for('download_file', name=filename), filename=url_for('download_file', name=outputFile))
    return render_template("index.html", msg="Not processed", filename=None)


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


def compressImage(inputfile, outputfile, quality="85", gsblur="0.05", colorspace="RGB"):
    command = "convert %s -sampling-factor 4:2:0 -strip -quality %s -interlace Plane -gaussian-blur %s -colorspace %s %s" % (
        inputfile, quality, gsblur, colorspace, outputfile)
    subprocess.run(["convert",
                    inputfile,
                    "-sampling-factor",
                    "4:2:0",
                    "-strip",
                    "-quality",
                    quality,
                    "-interlace",
                    "Plane",
                    "-colorspace",
                    colorspace,
                    outputfile
                    ])
    return "yo"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
