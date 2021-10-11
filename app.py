import os

from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import secure_filename, redirect
from ai_stylist import references, find_deep_fashion_clothing_set_for_url_references, find_deep_fashion_clothing_set_for_path_references

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

references = ['https://i.pinimg.com/736x/b3/2e/42/b32e424d87006792d1eeea79423a2cf2.jpg']
paths = ["static/uploads/reference_1.jpg"]

              # 'https://onpointfresh.com/wp-content/uploads/2016/08/tumblr_o2hadekN0v1uceufyo1_500.jpg',
              # 'https://onpointfresh.com/wp-content/uploads/2016/08/tumblr_o9iygiboae1uceufyo1_1280.jpg',
              # 'https://i.pinimg.com/originals/6c/cf/18/6ccf181f6261dd2b290dc395ac1d9007.jpg',
              # 'https://i.pinimg.com/564x/a6/2a/d7/a62ad7f7be29074e486db6cdc32be8d7--smart-casual-work-casual-work-outfits.jpg',
              # 'https://i.pinimg.com/originals/85/7e/f3/857ef3f7b32fa62f26aa5bd909a4d4f8.jpg',
              # 'https://i.pinimg.com/originals/a1/15/5b/a1155b228226de5a12feea05f59e4d30.jpg',
              #'https://i.pinimg.com/originals/c9/2c/8d/c92c8d912696542de3f7771c16aebccb.jpg']
              # 'https://i.pinimg.com/originals/b2/ac/62/b2ac621b97e6999f2235ad4bba600ca4.jpg',
              # 'https://media.gq-magazine.co.uk/photos/5d1399512881cc9fe10a84a4/master/w_1280,h_1920,c_limit/Street-Style-06-27Nov17_Robert-Spangle_b.jpg',
              # 'https://i.pinimg.com/564x/1c/cc/be/1cccbe0ec79b484a367a704c8d08bfbf.jpg',
              # 'https://i.pinimg.com/originals/a4/43/57/a4435723c85e5a9f7d27f0ee19090aa7.jpg']

paths = ["static/uploads/reference_1.jpg"]
print(len(paths))
# references_2 = ['https://i.pinimg.com/564x/a6/2a/d7/a62ad7f7be29074e486db6cdc32be8d7--smart-casual-work-casual-work-outfits.jpg',
#                 'https://i.pinimg.com/originals/85/7e/f3/857ef3f7b32fa62f26aa5bd909a4d4f8.jpg',
#                 'https://i.pinimg.com/originals/a1/15/5b/a1155b228226de5a12feea05f59e4d30.jpg',
#                 'https://i.pinimg.com/originals/c9/2c/8d/c92c8d912696542de3f7771c16aebccb.jpg']
#                      'https://i.pinimg.com/564x/4e/e7/16/4ee716810c3c5d301a2169d0425b037a.jpg',
#                      'https://i.pinimg.com/originals/61/d2/b6/61d2b66fea7b355b2c01979bd85bac46.jpg',
#                      'https://i.pinimg.com/564x/cc/f8/ba/ccf8bae685ad1b8636e79bf5383e8f8c.jpg',
#                      'http://babd.wincenworks.com/wp-content/uploads/2019/11/e0ac335a23fd55de50396f22717167dd54bba9a9.png']

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
    <h1>Upload new file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.debug = True
    app.run()

# web: gunicorn test.wsgi
# web: gunicorn app:app --timeout 1000
# web: gunicorn run:app