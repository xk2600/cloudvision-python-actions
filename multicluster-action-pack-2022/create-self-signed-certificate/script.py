# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# This action will generate a self-signed certificate and an associate key that can be used
# in an SSL profile.
# Example of configuration using the generated certificate and key on EOS:

# management security
#   ssl profile SSL_profile
#     tls versions 1.2
#     certificate self-signed.crt key self-signed.key
# management api http-commands
#   protocol https ssl profile SSL_profile

#from cloudvision.cvlib import ActionFailed

# 1. Setup:
device = ctx.getDevice()
ctx.info(f"device_id: [{device.id}] - ip: [{device.ip}] - hostname: [{device.hostName}]")
cmdResponse = ctx.runDeviceCmds(["enable", "show hostname"])
hostname = cmdResponse[1]['response']['hostname']
fqdn = cmdResponse[1]['response']['fqdn']
ctx.info(f"Creating self-signed certificate for device with fqdn: {fqdn} - hostname: {hostname}")

# 2. Commands creation:
args = ctx.changeControl.args
steps = [
    (
        "Key Generation",
        f"security pki key generate rsa {args['key_length']} {args['key_file']}"
    ),
    (
        "Certification Generation",
        f"security pki certificate generate self-signed {args['cert_file']} " +
        f" key {args['key_file']} " +
        f" validity {args['validity']} " +
        f" parameters common-name {hostname} " +
        f" country \"{args['country']}\" " +
        f" state \"{args['state']}\" " +
        f" locality \"{args['locality']}\" " +
        f" organization \"{args['organization']}\" " +
        f" organization-unit \"{args['organization_unit']}\" " +
        f" email {args['email']} " +
        f" subject-alternative-name dns {fqdn} email {args['email']} ip {device.ip}")
]

output_cmd_list = []
for step, cmd in steps:
    ctx.info(f"{step}: {cmd}")
    # 3. Run the commands on the device:
    output_cmd_list.append(ctx.runDeviceCmds(['enable', cmd])[1])

# check for errors
for index, cmdOutput in enumerate(output_cmd_list):
    if 'error' in cmdOutput.keys() and cmdOutput['error'] != '':
        raise UserWarning(f"Error: switch {fqdn} - '{steps[index][0]}' \n Command: '{steps[index][1]}' \n Error: {cmdOutput}")

# 4. Verification step:
cert_dir_output = ctx.runDeviceCmds(["enable", f"dir certificate:/{args['cert_file']}"])
cert_file_response = cert_dir_output[1]['response']['messages'][0].split("\n")[2]
key_dir_output = ctx.runDeviceCmds(["enable", f"dir sslkey:/{args['key_file']}"])
key_file_response = key_dir_output[1]['response']['messages'][0].split("\n")[2]
ctx.info(f"Verification - Generated certificate file: {cert_file_response}")
ctx.info(f"Verification - Generated key file: {key_file_response}")