from flask import Flask, flash, render_template, request, send_from_directory, redirect, url_for, Markup
from werkzeug import secure_filename
import os, uuid, json, sqlite3 as lite
from subprocess import call
import hashlib
from threading import Timer

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
dangerousExtensions = ['zip', 'rar', '7z', 'dll', 'exe', 'com', 'txt']
bannedExtensions = ['ade', 'adp', 'bat', 'chm', 'cmd', 'com', 'cpl', 'hta', 'ins', 'isp', 'jse', 'lib', 'lnk',
        'mde', 'msc', 'msp', 'mst', 'pif', 'scr', 'sct', 'shb', 'sys', 'vb', 'vbe', 'vbs', 'vxd', 'wsc',
        'wsf', 'wsh']
BANEXTENSIONS = True


def av_scan(fpath, new_fname):
    call(['clamscan', '--quiet', '--infected', '--remove', fpath])
    if not os.path.exists(fpath):
        print( 'Virus detected, file %s deleted...' % new_fname )
        con = lite.connect('files.db')
        with con:
            cur = con.cursor()
            cur.execute('INSERT INTO banned (md5hash, new_fname, orig_fname) VALUES'
                        '(?, ?, ?)', (fhash, new_fname, orig_fname))
        con.commit()


def get_fhash(f):
    h = hashlib.md5()
    buf = f.read()
    f.seek(0)
    h.update(buf)
    fhash = h.hexdigest()
    return fhash


def check_duplicate(fhash):
    con = lite.connect('files.db')
    with con:
        cur = con.cursor()
        cur.execute('SELECT * FROM files WHERE md5hash=?', (fhash,))
        data = cur.fetchone()
        return not data


def create_db():
    con = lite.connect('files.db')
    with con:
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS files'
                    '(md5hash TEXT, new_fname TEXT, orig_fname TEXT, '
                    'date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cur.execute('CREATE TABLE IF NOT EXISTS banned'
                    '(md5hash TEXT, new_fname TEXT, orig_fname TEXT, '
                    'date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        con.commit()


def db_entry(fhash, new_fname, orig_fname):
    con = lite.connect('files.db')
    with con:
        cur = con.cursor()
        cur.execute('INSERT INTO files (md5hash, new_fname, orig_fname) VALUES'
                    '(?, ?, ?)', (fhash, new_fname, orig_fname))
    con.commit()


def upload(f, js=True, api=False):
    value = ""
    json_dict = {}
    md5hash = get_fhash(f)
    if f.filename.rsplit('.', 1)[1] not in bannedExtensions or not BANEXTENSIONS:
        orig_fname = secure_filename(f.filename)
        new_fname = uuid.uuid4().hex + '.' + secure_filename(f.filename.rsplit('.', 1)[1])
        if check_duplicate(md5hash):
            db_entry(md5hash, new_fname, orig_fname)
            f.save('./uploads/' + new_fname)
            fpath = 'uploads/%s' % new_fname
            extension = f.filename.split('.', 1)[1]
            if (extension in dangerousExtensions):
                t = Timer(60, av_scan, [fpath, new_fname])
                t.daemon = True
                t.start()
            print('file uploaded ' + request.url_root + 'uploads/' + new_fname)
            url = url_for('send_js', path=new_fname)
            if not api:
                value = 'success:' + url
            else:
                value = request.url_root + 'uploads/' + new_fname
                json_dict['status'] = 'success'
                json_dict['new_fname'] = new_fname
                json_dict['url'] = value
            if not js:
                flash(request.url_root + 'uploads/' + new_fname, 'success')
        else:
            print(orig_fname + '[' + md5hash + ']' + ' already uploaded')
            url = url_for('send_js', path=new_fname)
            if not api:
                value = 'exists:' + url
            else:
                json_dict['status'] = 'error'
                json_dict['error'] = 'exists'
                json_dict['url'] = url
            if not js:
                message = 'File already exists <span>%s</span>'
                flash(Markup(message) % (orig_fname), 'error')
    else:
        value = 'error:filenameinvalid'
        if not js:
            flash('Unsupported filetype', 'error')
        if api:
            json_dict['status'] = 'error'
            json_dict['error'] = 'invalidFilename'
    if not api:
        return value
    else:
        return json_dict


@app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def post_index():
    flist = request.files.getlist('file')
    for f in flist:
        upload(f, js=False)
    return redirect(url_for('get_index'))


@app.route('/api/upload', methods=['POST'])
def post_indexapi():
    flist = request.files.getlist('file')
    res = []
    for f in flist:
        v = upload(f, js=False, api=True)
        res.append(v)
    return json.dumps(res)


@app.route('/js', methods=['POST'])
def get_indexjs():
    flist = request.files.getlist('file')
    value = []
    for f in flist:
        v = upload(f)
        value.append(v)
    return '\n'.join(value)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def fileNotFound(e):
    return render_template('404.html'), 404


@app.errorhandler(410)
def fileRemoved(e):
    return render_template('410.html'), 410


@app.route('/uploads/<path:path>')
def send_js(path):
    return send_from_directory('uploads', path)


if __name__ == '__main__':
    create_db()
    app.run(port=8666, debug=True, threaded=True)
