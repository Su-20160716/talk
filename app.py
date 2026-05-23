from flask import Flask, request, jsonify, render_template_string, session,send_from_directory
import json
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "123456789"

# 上传配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "mp3", "wav", "mp4", "avi", "mov", "mkv",
    "zip", "rar", "7z"
}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists("data.json"):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({
            "users": {},
            "friends": {},
            "rooms": {"1001": []},
            "private": {}
        }, f)

def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(d):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)

ADMIN_USER = "Adminmanager"
ADMIN_PASS = "su-22gf"

def is_baozi(uid):
    if len(uid) != 8:
        return False
    for i in range(6):
        if uid[i] == uid[i+1] == uid[i+2]:
            return True
    return False

def generate_id():
    while True:
        newid = str(uuid.uuid4().int)[:8]
        db = load_data()
        if newid not in db["users"] and not is_baozi(newid):
            return newid

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def root():
    return '<script>location.href="/project26"</script>'

@app.route("/project26")
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Project26</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Microsoft YaHei", sans-serif;
}
#app {
    width: 900px;
    height: 700px;
    border: 1px solid #ccc;
    display: flex;
    margin: 20px auto;
}
.left {
    width: 260px;
    background: #f8f8f8;
    padding: 15px;
}
.right {
    flex: 1;
    display: flex;
    flex-direction: column;
}
/* 统一输入框和按钮高度 */
input, button {
    width: 100%;
    padding: 10px;
    margin: 6px 0;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button {
    background: #06c167;
    color: #fff;
    border: none;
    cursor: pointer;
}
button:hover {
    background: #05a85a;
}
#title {
    height: 50px;
    line-height: 50px;
    padding-left: 15px;
    border-bottom: 1px solid #ddd;
    font-size: 16px;
}
#msg {
    flex: 1;
    padding: 15px;
    overflow: auto;
    background: #fdfdfd;
}
/* 发送区：输入框+按钮同一行，输入框大、按钮小 */
#send {
    display: flex;
    align-items: center;
    padding: 10px;
    gap: 10px;
}
#send input[type="text"] {
    flex: 1;
    margin: 0;
}
#send button {
    width: 100px;
    margin: 0;
}
/* 文件上传区 */
#upload_area {
    display: flex;
    align-items: center;
    padding: 0 10px 10px;
    gap: 10px;
}
#upload_area input[type="file"] {
    flex: 1;
    margin: 0;
}
#upload_area button {
    width: 100px;
    margin: 0;
}
.item {
    padding: 10px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
}
.item:hover {
    background: #eee;
}
.av {
    width: 32px;
    height: 32px;
    background: #06c167;
    color: white;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.row {
    display: flex;
    margin: 8px 0;
    align-items: center;
}
.my {
    flex-direction: row-reverse;
}
.bubble {
    padding: 8px 12px;
    background: #fff;
    border-radius: 6px;
    margin: 0 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.my .bubble {
    background: #d4f8e4;
}
.bubble a {
    color: #06c167;
    text-decoration: none;
}
.hide {
    display: none !important;
}
h4 {
    margin-bottom: 10px;
}
</style>
</head>
<body>
<div id="app">
<div class="left">
<div id="login_box">
<h4>注册 / 登录</h4>
<input id="nick" placeholder="输入昵称">
<input id="pwd" type="password" placeholder="输入密码">
<button id="reg_btn">注册</button>
<button id="login_btn">登录</button>
</div>

<div id="user_box" class="hide">
<p>专属号：<span id="my_id"></span></p>
<button id="logout_btn">退出登录</button>
<button id="qun_btn">群聊</button>
<button id="friend_btn">好友</button>
<button id="add_btn">加好友</button>
</div>

<div id="qun_list">
<div class="item" data-id="1001">1001 大厅</div>
</div>

<div id="friend_list" class="hide"></div>
<div id="add_box" class="hide">
<input id="f_id" placeholder="输入对方专属号">
<button id="add_friend_btn">添加好友</button>
</div>
</div>

<div class="right">
<div id="title">请登录</div>
<div id="msg"></div>
<!-- 文件上传区 -->
<div id="upload_area" class="hide">
    <input type="file" id="file_input">
    <button id="upload_btn">上传文件</button>
</div>
<!-- 发送区 -->
<div id="send">
    <input id="text" placeholder="输入消息">
    <button id="send_btn">发送</button>
</div>
</div>
</div>

<script>
// 关键：token 存在内存里，登录状态靠 token 判断
let token = "";
let mode = "qun";
let target = "1001";

// 绑定按钮
document.getElementById("reg_btn").addEventListener("click", reg);
document.getElementById("login_btn").addEventListener("click", login);
document.getElementById("logout_btn").addEventListener("click", logout);
document.getElementById("qun_btn").addEventListener("click", show_qun);
document.getElementById("friend_btn").addEventListener("click", show_friend);
document.getElementById("add_btn").addEventListener("click", show_add);
document.getElementById("add_friend_btn").addEventListener("click", add_friend);
document.getElementById("send_btn").addEventListener("click", send);
document.getElementById("upload_btn").addEventListener("click", upload_file);

// 群列表点击
document.querySelectorAll("#qun_list .item").forEach(item=>{
    item.addEventListener("click", function(){
        go_qun(this.dataset.id);
    });
});

// 注册
function reg(){
    let n = document.getElementById("nick").value.trim();
    let p = document.getElementById("pwd").value.trim();
    if(!n || !p){
        alert("昵称和密码不能为空");
        return;
    }
    fetch("/project26/reg",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({nick:n,pwd:p})
    })
    .then(r=>r.json())
    .then(d=>{
        console.log("reg:", d);
        if(d.ok){
            token = d.token;
            show_user(d);
        }else{
            alert("注册失败，昵称已存在");
        }
    })
    .catch(e=>console.error(e));
}

// 登录
function login(){
    let n = document.getElementById("nick").value.trim();
    let p = document.getElementById("pwd").value.trim();
    if(!n || !p){
        alert("昵称和密码不能为空");
        return;
    }
    fetch("/project26/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({nick:n,pwd:p})
    })
    .then(r=>r.json())
    .then(d=>{
        console.log("login:", d);
        if(d.ok){
            token = d.token;
            show_user(d);
        }else{
            alert("登录失败，昵称或密码错误");
        }
    })
    .catch(e=>console.error(e));
}

// 退出
function logout(){
    token = "";
    document.getElementById("login_box").classList.remove("hide");
    document.getElementById("user_box").classList.add("hide");
    document.getElementById("upload_area").classList.add("hide");
    document.getElementById("title").innerText = "请登录";
    document.getElementById("msg").innerHTML = "";
}

// 显示用户界面（登录成功后调用）
function show_user(d){
    document.getElementById("login_box").classList.add("hide");
    document.getElementById("user_box").classList.remove("hide");
    document.getElementById("upload_area").classList.remove("hide"); // 显示上传区
    document.getElementById("my_id").innerText = d.id;
    document.getElementById("title").innerText = "已登录 - 群聊大厅";
}

function show_qun(){
    mode="qun";
    document.getElementById("qun_list").classList.remove("hide");
    document.getElementById("friend_list").classList.add("hide");
    document.getElementById("add_box").classList.add("hide");
}

function show_friend(){
    mode="friend";
    document.getElementById("qun_list").classList.add("hide");
    document.getElementById("friend_list").classList.remove("hide");
    document.getElementById("add_box").classList.add("hide");
    load_friend();
}

function show_add(){
    document.getElementById("qun_list").classList.add("hide");
    document.getElementById("friend_list").classList.add("hide");
    document.getElementById("add_box").classList.remove("hide");
}

function go_qun(id){
    target=id;
    document.getElementById("title").innerText="群聊 " + id;
}

function go_friend(id,name){
    target=id;
    document.getElementById("title").innerText="私聊 " + name;
}

function add_friend(){
    let to = document.getElementById("f_id").value.trim();
    if(!to) return;
    fetch("/project26/add_friend",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({token,to})
    })
    .then(r=>r.json())
    .then(d=>{
        alert(d.msg);
    });
}

function load_friend(){
    fetch("/project26/friend_list",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({token})
    })
    .then(r=>r.json())
    .then(d=>{
        let html = "";
        d.list.forEach(f=>{
            html+=`<div class="item" onclick="go_friend('${f.id}','${f.nick}')">${f.nick} (${f.id})</div>`;
        });
        document.getElementById("friend_list").innerHTML = html;
    });
}

// 发送文字消息
function send(){
    let t = document.getElementById("text").value;
    if(!t || !token) return;
    fetch("/project26/send",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({token,mode,target,text:t})
    });
    document.getElementById("text").value = "";
}

// 上传文件
function upload_file(){
    let fileInput = document.getElementById("file_input");
    let file = fileInput.files[0];
    if(!file || !token){
        alert("请先登录并选择文件");
        return;
    }
    let formData = new FormData();
    formData.append("token", token);
    formData.append("mode", mode);
    formData.append("target", target);
    formData.append("file", file);

    fetch("/project26/upload",{
        method:"POST",
        body:formData
    })
    .then(r=>r.json())
    .then(d=>{
        if(d.ok){
            alert("上传成功");
        }else{
            alert("上传失败：" + d.msg);
        }
        fileInput.value = "";
    });
}

// 加载消息（关键：有 token 才加载，否则显示请登录）
function load_msg(){
    if(!token){
        document.getElementById("title").innerText = "请登录";
        return;
    }
    fetch("/project26/get_msg",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({token,mode,target})
    })
    .then(r=>r.json())
    .then(d=>{
        let h = "";
        d.list.forEach(m=>{
            let cls = m.me ? "row my" : "row";
            if(m.type === "file"){
                h+=`<div class="${cls}">
                        <div class="av">${m.name[0]}</div>
                        <div class="bubble"><a href="${m.url}" target="_blank">📎 ${m.filename}</a></div>
                     </div>`;
            }else{
                h+=`<div class="${cls}">
                        <div class="av">${m.name[0]}</div>
                        <div class="bubble">${m.text}</div>
                     </div>`;
            }
        });
        document.getElementById("msg").innerHTML = h;
        document.getElementById("msg").scrollTop = document.getElementById("msg").scrollHeight;
    });
}

setInterval(load_msg,1000);
</script>
</body>
</html>
''')

@app.route("/project26/reg", methods=["POST"])
def reg():
    j = request.get_json()
    nick = j.get("nick", "").strip()
    pwd = j.get("pwd", "").strip()
    db = load_data()
    for u in db["users"].values():
        if u["nick"] == nick:
            return jsonify({"ok":0})
    uid = generate_id()
    token = str(uuid.uuid4())
    db["users"][uid] = {"nick":nick, "pwd":pwd, "token":token}
    db["friends"][uid] = []
    save_data(db)
    return jsonify({"ok":1, "token":token, "id":uid})

@app.route("/project26/login", methods=["POST"])
def login():
    j = request.get_json()
    nick = j.get("nick", "").strip()
    pwd = j.get("pwd", "").strip()
    db = load_data()
    for k,u in db["users"].items():
        if u["nick"] == nick and u["pwd"] == pwd:
            token = str(uuid.uuid4())
            u["token"] = token
            save_data(db)
            return jsonify({"ok":1, "token":token, "id":k})
    return jsonify({"ok":0})

@app.route("/project26/info", methods=["POST"])
def info():
    token = request.get_json().get("token")
    db = load_data()
    for k,u in db["users"].items():
        if u.get("token") == token:
            return jsonify({"ok":1, "id":k, "nick":u["nick"]})
    return jsonify({"ok":0})

@app.route("/project26/add_friend", methods=["POST"])
def add_friend():
    j = request.get_json()
    token = j.get("token")
    to = j.get("to")
    db = load_data()
    me = None
    for k,u in db["users"].items():
        if u.get("token") == token:
            me = k
            break
    if not me or to not in db["users"] or me == to:
        return jsonify({"msg":"添加失败"})
    if to not in db["friends"][me]:
        db["friends"][me].append(to)
        db["friends"][to].append(me)
        save_data(db)
    return jsonify({"msg":"添加成功"})

@app.route("/project26/friend_list", methods=["POST"])
def friend_list():
    token = request.get_json().get("token")
    db = load_data()
    me = None
    for k,u in db["users"].items():
        if u.get("token") == token:
            me = k
            break
    res = []
    for f in db["friends"].get(me, []):
        if f in db["users"]:
            res.append({"id":f, "nick":db["users"][f]["nick"]})
    return jsonify({"list":res})

@app.route("/project26/send", methods=["POST"])
def send():
    j = request.get_json()
    token = j.get("token")
    mode = j.get("mode")
    target = j.get("target")
    text = j.get("text")
    db = load_data()
    me = None
    name = ""
    for k,u in db["users"].items():
        if u.get("token") == token:
            me = k
            name = u["nick"]
            break
    if not me:
        return jsonify({})
    msg = {"name":name, "text":text, "from":me, "type":"text"}
    if mode == "qun":
        if target not in db["rooms"]:
            db["rooms"][target] = []
        db["rooms"][target].append(msg)
    else:
        key = "_".join(sorted([me, target]))
        if key not in db["private"]:
            db["private"][key] = []
        db["private"][key].append(msg)
    save_data(db)
    return jsonify({})

@app.route("/project26/upload", methods=["POST"])
def upload():
    token = request.form.get("token")
    mode = request.form.get("mode")
    target = request.form.get("target")
    file = request.files.get("file")

    db = load_data()
    me = None
    name = ""
    for k,u in db["users"].items():
        if u.get("token") == token:
            me = k
            name = u["nick"]
            break
    if not me:
        return jsonify({"ok":False, "msg":"未登录"})

    if not file or file.filename == "":
        return jsonify({"ok":False, "msg":"未选择文件"})

    if not allowed_file(file.filename):
        return jsonify({"ok":False, "msg":"不支持的文件格式"})

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)

    msg = {
        "name": name,
        "from": me,
        "type": "file",
        "filename": filename,
        "url": f"/project26/uploads/{unique_name}"
    }
    if mode == "qun":
        if target not in db["rooms"]:
            db["rooms"][target] = []
        db["rooms"][target].append(msg)
    else:
        key = "_".join(sorted([me, target]))
        if key not in db["private"]:
            db["private"][key] = []
        db["private"][key].append(msg)
    save_data(db)
    return jsonify({"ok":True})

@app.route("/project26/uploads/<path:filename>")
def serve_upload(filename):
    return (
        send_from_directory(app.config["UPLOAD_FOLDER"], filename))

@app.route("/project26/get_msg", methods=["POST"])
def get_msg():
    j = request.get_json()
    token = j.get("token")
    mode = j.get("mode")
    target = j.get("target")
    db = load_data()
    me = None
    for k,u in db["users"].items():
        if u.get("token") == token:
            me = k
            break
    if not me:
        return jsonify({"list":[]})
    res = []
    if mode == "qun":
        ms = db["rooms"].get(target, [])
    else:
        key = "_".join(sorted([me, target]))
        ms = db["private"].get(key, [])
    for m in ms:
        res.append({
            "name": m["name"],
            "me": m["from"] == me,
            "type": m.get("type", "text"),
            "text": m.get("text", ""),
            "filename": m.get("filename", ""),
            "url": m.get("url", "")
        })
    return jsonify({"list":res})

@app.route("/project26/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        u = request.form.get("u")
        p = request.form.get("p")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = 1
            return "登录成功 <a href='/project26/admin_panel'>管理面板</a>"
    return '''<form method="post">
账号：<input name="u"><br>
密码：<input type="password" name="p"><br>
<button>登录</button></form>'''

@app.route("/project26/admin_panel")
def admin_panel():
    if not session.get("admin"):
        return "无权限"
    db = load_data()
    users = []
    for k,u in db["users"].items():
        users.append({"id":k, "nick":u["nick"], "bao":is_baozi(k)})
    return render_template_string('''
<h3>用户列表</h3>
{%for u in users%}
<p>{{u.id}} - {{u.nick}} {%if u.bao%}<b style="color:red">豹子号</b>{%endif%}</p>
{%endfor%}
<hr>
<h3>分配豹子号</h3>
<form action="/project26/set_bao" method="post">
新号码：<input name="lid"><br>
用户昵称：<input name="nick"><br>
<button>分配</button>
</form>
''', users=users)

@app.route("/project26/set_bao", methods=["POST"])
def set_bao():
    if not session.get("admin"):
        return "无权限"
    lid = request.form.get("lid").strip()
    nick = request.form.get("nick").strip()
    db = load_data()
    if len(lid)!=8 or not is_baozi(lid) or lid in db["users"]:
        return "无效号码"
    old = None
    for k,u in db["users"].items():
        if u["nick"] == nick:
            old = k
            break
    if not old:
        return "未找到用户"
    db["users"][lid] = db["users"].pop(old)
    for k,fl in db["friends"].items():
        if old in fl:
            fl[fl.index(old)] = lid
    db["friends"][lid] = db["friends"].pop(old, [])
    save_data(db)
    return "分配成功！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)