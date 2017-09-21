#!/usr/bin/python3
#
# ipmon.py
#
# this program monitors the dynamic ip address of my router
#
# cron periodically (10 minute intervals) runs this program
# crontab -e
# */10 * * * * /usr/bin/python ~/dynip/ipmon.py >/dev/null 2>&1
#
# program auto constructs an email with new ip address and datetime stamp and sends to chosen addresses
# only if the ip address has changed since the last time the program was run

import re
import sys
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text


def main():

    # set up required variables for email
    # variable 'smtp_to' can be any number of email addresses comma seperated 
    smtp_from       = "xyz@hotmail.com"
    smtp_to         = "abc@hotmail.com, 123@gmail.com"
    smtp_server     = "smtp.live.com" 
    smtp_user       = "xyz@hotmail.com"
    smtp_pwd        = "@@@@@@@@@@@"
    smtp_subject    = "Dynamic IP Address "


    # make system calls
    messydate = str(subprocess.check_output("date"))
    messydynip = str(subprocess.check_output("curl ipinfo.io/ip", shell=True))
    
    # RegEx the formatting characters out of the string
    # messydate is in format  b'Sat  2 Sep 16:00:01 BST 2017\n'
    # messydynip is in format b'2.123.89.12\n'
    date = re.search(r'[A-Z].*2017', messydate).group(0)
    dynip = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', messydynip).group(0)
    
    # check if the new IP address has changed
    f = open("/root/dynip/dynip.txt", "r")
    read_ip = f.read()
    f.close()

    if read_ip != dynip:

        # replace variable with the new ip address
        f = open("/root/dynip/dynip.txt","w")
        f.write(dynip)
        f.close()

        # MIME STUFF
        # email.mime.multipart.MIMEMultipart(_subtype=’mixed’, boundary=None, _subparts=None, *, policy=compat32, **_params)
        # email.mime.text.MIMEText(_text, _subtype=’plain’, _charset=None, *, policy=compat32)
        msg = email.mime.multipart.MIMEMultipart()
        msg['From']     = smtp_from
        msg['To']       = smtp_to
        msg['Subject']  = smtp_subject

        # populate messge body with info and attach to the mime headers
        body = "Router IP Address on " + date  + " = " + dynip
        msg.attach(email.mime.text.MIMEText(body,'plain'))
        content = msg.as_string()

        # send the email !
        # create a TLS connection to encrypt session with the hotmail smtp server
        smtp_obj = smtplib.SMTP(smtp_server, 587)
        smtp_obj.connect (smtp_server, 587)

        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()

        # log into my account
        smtp_obj.login( smtp_user, smtp_pwd)
        smtp_obj.set_debuglevel(1)

        # send the mail
        # format is - x.sendmail(fromaddr, toaddrs, msg)
        smtp_obj.sendmail( smtp_from, smtp_to, content )
        smtp_obj.quit()

    

if __name__ == '__main__':
    main()

