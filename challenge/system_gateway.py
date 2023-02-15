import time
import pickle
import hashlib
import waitress
import random
import os
import base64
import uuid
import socket
import sys
import logging
import subprocess

from collections import defaultdict
from datetime import date
from flask import Flask, request, render_template, redirect, url_for, flash, Response
from werkzeug.security import check_password_hash, generate_password_hash

def serial_number() -> str:
    b = hashlib.md5(socket.gethostname().encode()).digest()
    return str(uuid.UUID(bytes=b))

SERIAL_NUMBER = serial_number()
LOG_FILE = os.getenv("LOG_FILE", "system_gateway.log")
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", 80))

FAILED_LOGIN_COUNT = defaultdict(int)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

class Grid(object):
    def __init__(self):
        # All power nodes are online
        self.core = True
        self.grid = [
            [True] * 5,
            [True] * 10
        ]

    def toggleNode(self, grid, node):
        """Turn a power node on or off"""
        if grid > len(self.grid):
            raise ValueError(f"unknown grid '{grid}'")
        if node > len(self.grid[grid]):
            raise ValueError(f"unknown node on grid '{grid}': no node '{node}'")
        self.grid[grid][node] = not self.grid[grid][node]

        # This grid has too many failures, power it off
        if sum(self.grid[grid]) <= len(self.grid[grid])//2:
            self.grid[grid] = [False] * len(self.grid[grid])
            raise ValueError(f"grid {grid} has failed")
        return

    def getJson(self):
        # see if each grid has failed
        failCount = 0
        res = {
            "core": self.core,
            "grid_1": True,
            "grid_0": True,
        }

        for grid in range(len(self.grid)):
            if sum(self.grid[grid]) <= len(self.grid[grid])//2:
                self.grid[grid] = [False] * len(self.grid[grid])
                failCount += 1
                res[f"grid_{grid}"] = False
        
        # If all grids have failed, turn off the core
        if failCount == len(self.grid):
            res["core"] = False
            self.core = False
        
        for i, grid in enumerate(self.grid):
            for j, node in enumerate(grid):
                res[f"node_{i}_{j}"] = node
        return res
            
class Session(object):
    def __init__(self, username):
        timeHex = hex(int(time.time()))[2:]
        rand = hex(int(random.randint(0, 1000000)))[2:]
        rand = timeHex + username.encode('utf-8').hex() + rand
        self.user = username
        m = hashlib.md5(rand.encode("utf-8"))
        self.token = timeHex + "-" + m.digest().hex()
        self.login = time.time()
        self.expires = time.time() + 60*60 # 1 hour
    
    def isExpired(self):
        return time.time() > self.expires
    
    def __repr__(self):
        return f"{self.user}: {self.token}"

app = Flask(__name__)
app.secret_key = b'oops i forgot to update this'
grid = Grid()
sessions = {} # Global sessions
users = {} # Global users

@app.after_request
def log_request(r: Response):
    if r.status_code == 304 and request.path.startswith("/static"):
        return r
    s = get_session()
    remote = request.remote_addr
    if s and s.user:
        remote += " " + s.user
    elif request.form.get("username"):
        remote += " " + request.form.get("username")
    
    logging.log(logging.INFO, "%s %s %s - %i", request.method, request.url, remote, r.status_code)
    return r

def new_session(user, roles=[]):
    s = Session(user)
    global sessions
    sessions[s.token] = s
    return base64.b64encode(pickle.dumps(s)).decode("utf-8")

def get_session() -> Session:
    try:
        if not sessions:
            return False
        session = request.cookies.get('auth_token', None)
        if not session:
            return None
        mySess = pickle.loads(base64.b64decode(session))
        sess = sessions.get(mySess.token, None)
        if not sess or sess.isExpired():
            return None
        return sess
    except Exception as E:
        print(E)
        return None

@app.route('/')
def index():
    sess = get_session()
    if not sess:
        return redirect(url_for('login'))
    return render_template("index.html", user=sess, grid=grid.getJson())

@app.route('/logout', methods=('GET',))
def logout():
    sess = get_session()
    if sess:
        global sessions
        del sessions[sess.token]
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        global FAILED_LOGIN_COUNT
        # Brute force protection
        if username and FAILED_LOGIN_COUNT.get(username, 0) >= 5:
            logging.warning("User %s has been banned", username)
            return render_template('login.html'), 403
        
        passwordHash = users.get(username, None)
        if passwordHash is None or not check_password_hash(passwordHash, password):
            FAILED_LOGIN_COUNT[username] += 1
            return render_template('login.html'), 401
        
        sess = new_session(username)
        resp = redirect(url_for('index'))
        resp.set_cookie("auth_token", sess)
        return resp
    return render_template('login.html')

def ping(cmd):
    if not cmd or not cmd.strip():
        return ""
    if not cmd.startswith("ping"):
        return "not a ping command"

    host = cmd.split()
    if len(host) < 2:
        return "not a valid ping command"
    host = host[1]
    ping_results = f"> {cmd}\nPinging {host} [127.0.0.1] with 32 bytes of data:\n"
    for i in range(random.randrange(1,6)):
        ping_results += f"Reply from 127.0.0.1: bytes=32 time={random.randrange(5,15)}ms\n"
    return ping_results

@app.route('/debug')
def debug():
    data = {
        "date": date.today(),
        "software": "3.6.122",
        "hardware": os.getenv("FIRMWARE_VERSION", "v01-09"),
        "serial": SERIAL_NUMBER,
        "ping": ping(request.args.get("cmd")),
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data["logs"] = f.read()
    data["build"] = hashlib.md5(data.get("software").encode()).hexdigest()
    return render_template('debug.html', **data)

@app.route("/api/toggle", methods=["GET"])
def grid_status():
    try:
        _, g, n = request.args.get("id").split("_")
        g = int(g)
        n = int(n)
        grid.toggleNode(g, n)
    except ValueError as E:
        flash({"err": str(E)})
        print(E)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with open("shadow") as fil:
        for line in fil.readlines():
            line = line.strip()
            user, pwd = line.split(" ")
            users[user] = pwd
    logging.log(logging.INFO, "Loaded %i users from local 'shadow' file", len(users))
    waitress.serve(app, host=HTTP_HOST, port=HTTP_PORT)