# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# this script was developed and tested 2021.3.1

from typing import List, Dict

ctx.alog('Restarting TerminAttr.')
cmds = [
    "enable",
    "configure",
    "daemon TerminAttr",
    "shutdown",
    "no shutdown"
]
cmdResponses: List[Dict] = ctx.runDeviceCmds(cmds)
ctx.alog('Restarted.')