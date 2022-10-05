# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# this script was developed and tested 2021.3.1

from typing import List, Dict
import requests
#from cloudvision.cvlib import ActionFailed
# cvlib doesn't appear to be available in older versions of CVP.

# cvprac isn't available in CVP's python actions, so emulate it.
def requests_createToken(secondary_cluster, service_token, duration="24h", devices=["*"]):
    response = None
    if not isinstance(secondary_cluster, list):
        raise TypeError("secondary_cluster must be a list of nodes.")
    if len(secondary_cluster) == 0:
        raise TypeError("secondary_cluster node list must contain at least one node to attach to.")
    headers = { 
        'Accept': "application/json",
        'Authorization': f"Bearer { service_token }" }
    data = {
        "reenrollDevices": devices, 
        "duration": duration }
    for node in secondary_cluster:
        if not isinstance(node, str):
            continue
        url = f"https://{ node }/cvpservice/enroll/createToken"
        response = requests.post(url, json=data, headers=headers, timeout=10, verify = False)
        if response.ok:
            print("DEBUG: Status Code=", response.status_code)
            return response.json()['data']
        response = None
    raise ConnectionError('No response or service credential failure when connecting to secondary nodes in the cluster.')

service_token = ctx.action.args.get("auth")
filename = ctx.action.args.get("filename")
expiry = ctx.action.args.get("expiry") 
# expiry units are d, h, or m: for days hours or minutes respectively.

# only include nodes that aren't empty.
secondary_cluster = []
for node in [ 
    ctx.action.args.get("backup_cvp_1"), 
    ctx.action.args.get("backup_cvp_2"), 
    ctx.action.args.get("backup_cvp_3") ]:
    
    if len(node) > 0:
        secondary_cluster.append(node)
ctx.alog('connecting to secondary cluster at: ' + ', '.join(secondary_cluster))

# attempt to get an enrollment token from the secondary cluster
token = None
try:
    token = requests_createToken(secondary_cluster, service_token, duration=expiry)
    # create_enroll_token's first argument is the timeout
    # The create_enroll_token also takes a second argument containing a list of serial
    # numbers allowed to be enrolled with this token. A later iteration of this script
    # may attempt to gather one token per change control, but would need a way to hand 
    # off the token from one action to another or make a single call to the secondary 
    # cluster and then reuse that token on all subsequent calls in the same action. 
except Exception as e:
    raise UserWarning(e)
ctx.alog('token retrieved. Attempting to push to device. \n token: ' + token)

# if we successfully retrieved an enrollment token, attempt to install the token in
# the device. 
if token is not None:
    cmds = [
        "enable",
        {"cmd": f"copy terminal: file:{filename}", "input": token}
    ]
    cmdResponses: List[Dict] = ctx.runDeviceCmds(cmds)
    # Iterate through the list of responses for the commands, and if an error occurred in
    # any of the commands, raise an exception
    # Only consider the first error that is encountered as following commands require previous ones to succeed
    errs = [resp.get('error') for resp in cmdResponses if resp.get('error')]
    if errs:
        raise UserWarning(f"Copying of token to {filename} failed with: {errs[0]}")
ctx.alog('token push complete.')