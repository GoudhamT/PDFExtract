import os
from pathlib import Path
# import tempfile
from flask import Flask,render_template , request
# from flask import 
import pdf2image
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
from PIL import Image
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploadFolder/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
port = int(os.environ.get('PORT', 3000))
uaa_service = environ.get_service(name='pyuaa').credentials

@app.route('/')
def hello():
    if 'authorization' not in request.headers:
        abort(403)
    access_token = request.headers.get('authorization')[7:]
    security_context = xssec.create_security_context(access_token, uaa_service)
    isAuthorized = security_context.check_scope('openid')
    if not isAuthorized:
        abort(403)
    return render_template("index.html") 

@app.route('/extract', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        words = request.form.get('kwords')
        def get_words(x):
            if len(x) > 1:
                return set(x.split(','))
        words = get_words(words)
        if not f.filename:
            return {"message": "No upload file sent"}
        elif not f.filename.endswith(".pdf"):
            return {"message": "Only pdf file upload allowed!"}
        else:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)            
            try:
                words_count = dict()
                l = []
                image = pdf2image.convert_from_path(filepath)
                for pagenumber, page in enumerate(image):
                    detected_text = pytesseract.image_to_string(page)
                    l.append(detected_text)              
                else:
                    clean_extract = "".join(l).replace("\n", " ").strip()
                    if words:
                        for w in words:
                            try:
                                w = w.lower()
                                if words_count[w]:
                                    words_count[w] += clean_extract.lower().count(w.lower())
                            except Exception as e:
                                words_count[w] = clean_extract.lower().count(w.lower())
                        return words_count
                    else:
                        return clean_extract
            except Exception as e:
                return e
            finally:
                os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)