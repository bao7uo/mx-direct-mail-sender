#!/usr/bin/python3

# mx-direct-mail-sender
# Author: Paul Taylor bao7uo
# github.com/bao7uo
# originally written for https://serverfault.com/a/833900/333514

# Sends a direct email, with no relay required, by looking up the domain MX record and delivering the message to one of the resulting mail servers.

import subprocess
import sys
import smtplib

mx_records = []
mx_values = {'pref': 0, 'serv': ''}

if len(sys.argv) < 5:
    print("\nUsage:\nmx-direct-mail-sender.py recipient@domain.com " +
          "from@originator.com 'msg subject' $'msg body. Use \\n " +
          "to indicate a new line'\n")
    exit()

recipient = sys.argv[1]
domain = recipient.split("@")[1]
originator = sys.argv[2]
subject = sys.argv[3]
body = sys.argv[4]

print("From:   " + originator)
print("To:     " + recipient)
print("Subject " + subject)
print("Body    " + body)

p = subprocess.Popen(
                'nslookup -type=mx ' + domain + ' 8.8.8.8',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
for line in p.stdout.readlines():
    line = line.decode().lower()
    if line.find("mail exchanger") != -1:
        for char in line:
            if str(char) in "\r\n\t":
                line = line.replace(char, '')
        if line.find("mx preference") != -1:
            mx_parse = line.replace(' ', '').split(",")
            mx_values['pref'] = int(mx_parse[0].split("=")[1])
            mx_values['serv'] = mx_parse[1].split("=")[1]
        else:
            mx_parse = line.split(" = ")[1].split(" ")
            mx_values['pref'] = int(mx_parse[0])
            mx_values['serv'] = mx_parse[1]
        mx_records.append(mx_values.copy())

retval = p.wait()


def mx_pref_sortvalue(record):
    return record['pref']


mx_records = sorted(mx_records, key=mx_pref_sortvalue)

server = mx_records[0]['serv']

print("\nSending mail to: " + recipient +
      " via first priority MX server: " + server)

smtp_send = smtplib.SMTP(server, 25)
smtp_send.sendmail(
            originator,
            recipient,
            "From: " + originator + "\nTo: " +
            recipient + "\nSubject:" + subject + "\n\n" + body
        )
smtp_send.quit()

