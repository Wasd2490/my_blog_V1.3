"""璋佹殩浜嗗啲瀛ｄ釜浜虹珯 - Flask 鍚庣 V1.1"""
from flask import Flask, request, jsonify, send_from_directory, session, redirect

import sqlite3, hashlib, os, secrets, urllib.request, urllib.parse, json
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE, static_url_path='')
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB


# ===== GitHub OAuth 閰嶇疆锛堢敵璇峰畬濉繖閲岋級=====
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'Ov23liu9SSPzzokG7NmP')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '540d05e6edc9f2d526da53b4174a549d7ad9344c')
GITHUB_CALLBACK = os.environ.get('GITHUB_CALLBACK', 'http://106.52.34.17:5000/auth/github/callback')
# ===============================================

DB = os.path.join(BASE, 'site.db')

def init_db():
    c = sqlite3.connect(DB)
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      nick TEXT NOT NULL,
      pwd TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS posts(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      uid INTEGER NOT NULL,
      title TEXT NOT NULL,
      cat TEXT DEFAULT '榛樿',
      content TEXT NOT NULL,
      excerpt TEXT,
      date TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS moments(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      text TEXT,
      media TEXT,
      type TEXT,
      date TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS comments(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      target_type TEXT NOT NULL,
      target_id TEXT NOT NULL,
      nick TEXT NOT NULL,
      avatar TEXT,
      content TEXT NOT NULL,
      date TEXT NOT NULL
    );
    ''')
    # 兼容旧数据库：加 sort 列
    try: c.execute('ALTER TABLE posts ADD COLUMN sort INTEGER DEFAULT 0')
    except: pass
    c.commit(); c.close()

init_db()

def hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    d = request.json
    try:
        c = sqlite3.connect(DB)
        c.execute('INSERT INTO users(email,nick,pwd) VALUES(?,?,?)',
                  (d['email'], d.get('nick','寰厜'), hash_pwd(d['pwd'])))
        c.commit(); c.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, msg='用户名已存在' if 'UNIQUE' in str(e) else str(e)), 400

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    c = sqlite3.connect(DB)
    r = c.execute('SELECT id,nick FROM users WHERE email=? AND pwd=?',
                  (d['email'], hash_pwd(d['pwd']))).fetchone()
    c.close()
    if not r: return jsonify(ok=False, msg='账号或密码错误'), 401
    session['uid'] = r[0]; session['nick'] = r[1]
    return jsonify(ok=True, nick=r[1])

@app.route('/api/logout')
def logout(): session.clear(); return jsonify(ok=True)

@app.route('/api/me')
def me():
    if 'uid' not in session: return jsonify(ok=False)
    return jsonify(ok=True, nick=session.get('nick'), avatar=session.get('avatar',''))

# ===== GitHub OAuth =====
@app.route('/auth/github')
def github_login():
    p = urllib.parse.urlencode({'client_id':GITHUB_CLIENT_ID, 'redirect_uri':GITHUB_CALLBACK, 'scope':'read:user user:email'})
    return redirect('https://github.com/login/oauth/authorize?'+p)

@app.route('/auth/github/callback')
def github_callback():
    code = request.args.get('code')
    # 鎹?token
    data = urllib.parse.urlencode({'client_id':GITHUB_CLIENT_ID,'client_secret':GITHUB_CLIENT_SECRET,'code':code}).encode()
    req = urllib.request.Request('https://github.com/login/oauth/access_token', data=data, headers={'Accept':'application/json'})
    token = json.loads(urllib.request.urlopen(req).read())['access_token']
    # get user info
    req = urllib.request.Request('https://api.github.com/user', headers={'Authorization':'token '+token, 'User-Agent':'Wasd2490-blog'})
    u = json.loads(urllib.request.urlopen(req).read())
    # 鑷姩娉ㄥ唽/鐧诲綍
    c = sqlite3.connect(DB)
    email = u.get('email') or (u['login']+'@github.local')
    r = c.execute('SELECT id,nick FROM users WHERE email=?',(email,)).fetchone()
    if not r:
        c.execute('INSERT INTO users(email,nick,pwd) VALUES(?,?,?)',(email,u['login'],hash_pwd(secrets.token_hex(8))))
        c.commit()
        r = c.execute('SELECT id,nick FROM users WHERE email=?',(email,)).fetchone()
    c.close()
    session['uid']=r[0]; session['nick']=r[1]; session['avatar']=u.get('avatar_url','')
    return redirect('/')

# 鏂囩珷 CRUD
@app.route('/api/posts')
def list_posts():
    c = sqlite3.connect(DB)
    rows = c.execute('SELECT id,title,cat,excerpt,date,sort FROM posts ORDER BY sort DESC, id DESC').fetchall()
    c.close()
    return jsonify([{'id':r[0],'title':r[1],'cat':r[2],'excerpt':r[3],'date':r[4],'sort':r[5] or 0} for r in rows])

@app.route('/api/posts/<int:pid>')
def get_post(pid):
    c = sqlite3.connect(DB)
    r = c.execute('SELECT title,cat,content,date FROM posts WHERE id=?',(pid,)).fetchone()
    c.close()
    if not r: return jsonify(ok=False),404
    return jsonify({'id':pid,'title':r[0],'cat':r[1],'content':r[2],'date':r[3]})

@app.route('/api/posts', methods=['POST'])
def add_post():
    d = request.json
    c = sqlite3.connect(DB)
    c.execute('INSERT INTO posts(uid,title,cat,content,excerpt,date) VALUES(?,?,?,?,?,?)',
              (1,d['title'],d.get('cat','榛樿'),d['content'],d.get('excerpt',''),datetime.now().strftime('%Y-%m-%d')))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.route('/api/posts/<int:pid>', methods=['DELETE'])
def del_post(pid):
    c = sqlite3.connect(DB)
    c.execute('DELETE FROM posts WHERE id=?',(pid,))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.route('/api/posts/<int:pid>', methods=['PUT'])
def update_post(pid):
    d = request.json
    c = sqlite3.connect(DB)
    c.execute('UPDATE posts SET title=?,cat=?,content=?,excerpt=? WHERE id=?',
              (d['title'],d.get('cat','榛樿'),d['content'],d.get('excerpt',''),pid))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.route('/api/posts/<int:pid>/reorder', methods=['POST'])
def reorder_post(pid):
    d = request.json
    c = sqlite3.connect(DB)
    c.execute('UPDATE posts SET sort=? WHERE id=?',(d['sort'],pid))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.route('/api/moments')
def get_moments():
    c = sqlite3.connect(DB)
    rows = c.execute('SELECT id,text,media,type,date FROM moments ORDER BY id DESC').fetchall()
    c.close()
    return jsonify([{'id':r[0],'text':r[1],'media':r[2],'type':r[3],'date':r[4]} for r in rows])

@app.route('/api/moments', methods=['POST'])
def add_moment():
    d = request.json
    c = sqlite3.connect(DB)
    c.execute('INSERT INTO moments(text,media,type,date) VALUES(?,?,?,?)',
              (d.get('text',''),d.get('media',''),d.get('type',''),datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.route('/api/moments/<int:mid>', methods=['DELETE'])
def del_moment(mid):
    c = sqlite3.connect(DB)
    c.execute('DELETE FROM moments WHERE id=?',(mid,))
    c.commit(); c.close()
    return jsonify(ok=True)

# 璇勮
@app.route('/api/comments/<ttype>/<tid>')
def get_comments(ttype,tid):
    c = sqlite3.connect(DB)
    rows = c.execute('SELECT nick,avatar,content,date FROM comments WHERE target_type=? AND target_id=? ORDER BY id',(ttype,tid)).fetchall()
    c.close()
    return jsonify([{'nick':r[0],'avatar':r[1],'content':r[2],'date':r[3]} for r in rows])

@app.route('/api/comments', methods=['POST'])
def add_comment():
    if 'uid' not in session: return jsonify(ok=False,msg='请先登录'),401
    d = request.json
    c = sqlite3.connect(DB)
    c.execute('INSERT INTO comments(target_type,target_id,nick,avatar,content,date) VALUES(?,?,?,?,?,?)',
              (d['ttype'],d['tid'],session.get('nick','寰厜'),session.get('avatar',''),d['content'],datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()
    return jsonify(ok=True)

# 椤甸潰璺敱
# GitHub API proxy (CORS fix) - universal proxy
@app.route('/api/github-proxy')
def github_proxy():
    target = request.args.get('url', '')
    if not target.startswith('https://api.github.com/') and not target.startswith('https://raw.githubusercontent.com/'):
        return 'bad url', 400
    req = urllib.request.Request(target, headers={
        'User-Agent': 'Wasd2490-blog',
        'Accept': 'application/vnd.github.v3+json'
    })
    try:
        data = urllib.request.urlopen(req, timeout=15).read()
        return app.response_class(data, mimetype='application/json')
    except Exception as e:
        return jsonify(error=str(e)), 502

@app.route('/api/github/repos')
def github_repos():
    url = 'https://api.github.com/users/Wasd2490/repos?sort=updated&per_page=20'
    req = urllib.request.Request(url, headers={'User-Agent': 'Wasd2490-blog', 'Accept': 'application/vnd.github.v3+json'})
    try:
        data = urllib.request.urlopen(req, timeout=10).read()
        return app.response_class(data, mimetype='application/json')
    except Exception:
        return jsonify([]), 502

@app.route('/api/github/readme/<repo>')
def github_readme(repo):
    for branch in ['main', 'master']:
        url = f'https://raw.githubusercontent.com/Wasd2490/{repo}/{branch}/README.md'
        req = urllib.request.Request(url, headers={'User-Agent': 'Wasd2490-blog'})
        try:
            data = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            return app.response_class(data, mimetype='text/plain; charset=utf-8')
        except: pass
    return app.response_class('# no README', mimetype='text/plain; charset=utf-8')

@app.route('/')
def home(): return send_from_directory(BASE,'index.html')

if __name__ == '__main__':
    import subprocess, time, urllib.request, json, os
    if os.name == 'nt':
        ngrok_path = r'C:\ngrok\ngrok.exe'
        subprocess.Popen([ngrok_path, 'http', '5000'], creationflags=0x08000000)
        print('姝ｅ湪鍚姩 ngrok...')
        time.sleep(5)
        pub_url = ''
        for _ in range(5):
            try:
                with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels') as r:
                    data = json.loads(r.read())
                    pub_url = data['tunnels'][0]['public_url']
                    break
            except: time.sleep(1)
        print(f'鍏綉: {pub_url}')
    app.run(host='0.0.0.0', port=5000, debug=True)
