from werkzeug.security import generate_password_hash
import os
import uuid
import string
import hashlib
import random
import socket


def serial_number() -> str:
    b = hashlib.md5(socket.gethostname().encode()).digest()
    return str(uuid.UUID(bytes=b))

SERIAL_NUMBER = serial_number()
users = {}

def load_users(fil) -> dict:
    global users
    with open(fil) as f:
        for line in f.readlines():
            line = line.strip()
            user, pwd = line.replace(" ",":").split(":")
            users[user] = pwd

def add_user(username, password):
    global users
    username = input("Enter username: ")
    password = input("Enter password: ")
    users[username] = generate_password_hash(password)

def del_user(username):
    global users
    username = input("Enter username: ")
    if username in users:
        del users[username]

def add_admin_user():
    # Generate the admin password
    sn_bytes = SERIAL_NUMBER.encode("utf-8")
    password = hashlib.sha1(sn_bytes).hexdigest().upper()[:10]
    print(f"admin {password}")
    global users
    users["admin"] = generate_password_hash(password)

def dump():
    with open('shadow', 'w') as f:
        for u, p in users.items():
            f.write(f"{u} {p}\n")

def main():
    print("System Serial Number:", SERIAL_NUMBER)
    print("Creating default users:")
    add_admin_user()
    global users
    for i in ["bob", "alice", "eve", "dandy"]:
        rand = "".join(random.choices(string.ascii_letters+string.digits, k=25))
        print(i, rand)
        users[i] = generate_password_hash(rand)
    dump()

if __name__ == '__main__':
    main()