import datetime
from flask import *
import mysql.connector
import time
import hasher
import os


UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'mp3', 'doc', 'docx'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def update_database(f):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="nocopy"
    )
    file_name=f.filename
    ext = f.filename.split(".")[-1]
    mycursor = mydb.cursor()
    timestamp = time.time()
    ts = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    sql = ''
    val = ''
    path = "static/" + file_name
    if ext == 'txt':
        sql = "INSERT INTO docs (path, time, hashval, type) VALUES (%s, %s,%s,%s)"
        val = (path, ts, hasher.txt_hash(path), ext)
    elif ext == 'docx' or ext == 'doc':
        sql = "INSERT INTO docs (path, time, hashval, type) VALUES (%s, %s,%s,%s)"
        val = (path, ts, hasher.word_hash(path), ext)
    elif ext == 'mp3':
        sql = "INSERT INTO music (path, time, hashval) VALUES (%s, %s,%s)"
        val = (path, ts, hasher.audio_hash(path))
    elif ext == 'jpg' or ext == 'png':
        sql = "INSERT INTO pics (path, time, hashval) VALUES (%s, %s,%s)"
        val = (path, ts, hasher.image_hash(path))
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        file = request.files['uploaded-file']

        if file.filename == '':
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_database(file)
            return render_template('success.html', filename=filename)
        else:
            return redirect('/failure')
    else:
        return redirect('/upload')


@app.route('/upload')
def upload():
    return render_template("upload.html")


@app.route('/failure')
def failure():
    return render_template("failure.html")


@app.route('/pics')
def pics():
    db = mysql.connector.connect(user='root', password='',
                                 host='localhost',
                                 database='nocopy')
    cursor = db.cursor()
    sql = 'select path from pics'
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return render_template("pics.html", data=data)


@app.route('/music')
def music():
    db = mysql.connector.connect(user='root', password='',
                                 host='localhost',
                                 database='nocopy')
    cursor = db.cursor()
    sql = "select path from music"
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return render_template("music.html", data=data)


@app.route('/text')
def text():
    db = mysql.connector.connect(user='root', password='',
                                 host='localhost',
                                 database='nocopy')
    cursor = db.cursor()
    sql = "select path from docs where type='txt'"
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return render_template("text.html", data=data)


@app.route('/word')
def word():
    db = mysql.connector.connect(user='root', password='',
                                 host='localhost',
                                 database='nocopy')
    cursor = db.cursor()
    sql = "select path from docs where type='doc' or type='docx'"
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return render_template("word.html", data=data)


if __name__ == '__main__':
    app.secret_key = 'nocopykey'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
