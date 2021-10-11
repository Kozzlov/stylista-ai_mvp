import os

from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import secure_filename, redirect
from ai_stylist import find_deep_fashion_clothing_set_for_url_references, find_deep_fashion_clothing_set_for_path_references

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

references = ['https://i.pinimg.com/736x/b3/2e/42/b32e424d87006792d1eeea79423a2cf2.jpg']
paths = ["static/uploads/reference_1.jpg"]

@app.route('/', methods=['POST', 'GET'])
def display_references_with_matches():
    # for references
    matches_links = find_deep_fashion_clothing_set_for_url_references(references=references)
    matches_paths = find_deep_fashion_clothing_set_for_path_references(paths=paths)
    # for local pictures
    # return render_template('index.html', reference=reference, matches=matches, reference_2=reference_2, matches_2=matches_2)
    print('running on %s' % request.host)
    return render_template('index.html', match_set=matches_links, path_set=matches_paths)

# @app.route('/find_match', methods=['GET', 'POST'])
# def display_references_with_match():
#     if request.method == 'GET':
#         return render_template('upload.html')
#     if request.method == 'POST':
#         reference = request.args.get("reference_url")
#         references.append(reference)
#         return render_template('/')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods=['GET', 'POST'])
def upload_reference_url():
    if request.method == 'POST':
        # f = request.files['file']
        # f.save(secure_filename(f.filename))
        link = request.values['reference_link']
        references.insert(0, link)
        return redirect('/')
    if request.method == 'GET':
        return render_template('upload.html')

@app.route('/uploader_image', methods=['GET', 'POST'])
def upload_reference_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join('static/uploads/', filename)
            paths.insert(0, file_path)
            print(filename)
            return redirect('/')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.debug = True
    app.run()
