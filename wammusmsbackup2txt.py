#!/usr/bin/python

# Converts SMS messages from Wammu/Gammu to text files so they can be 
# imported under android via "SMS to Text" app by SMeiTi.
#
# usage: ./wammusmsbackup2txt.py K800i_2012-01-05.smsbackup > sms_20120105.txt
#
# author: Markus Völk
# date: 2012-01-07


import os
import sys
import locale
import configparser
import time
import re

encoding = 'utf-8-sig'
#encoding = locale.getpreferredencoding()

if len(sys.argv) < 2:
    exit('usage: ' + sys.argv[0] + ' <inputfile>')

file_name = str(sys.argv[1])

if not os.path.isfile(file_name):
    exit('file not found')


config = configparser.ConfigParser()
config.read(file_name, encoding)

dataencoding = 'utf-16-be'

for i in config.sections():
    if i.startswith('SMSBackup'):
        mtext = ''
        mnumber = ''
        mdatetime = time.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        mstate = ''
        mname = ''
        
        for j in config[i]:
            if j.startswith('text'):
                mtext = mtext + bytes.fromhex(config[i][j]).decode(dataencoding)
            elif j == 'numberunicode':
                mnumber = bytes.fromhex(config[i][j]).decode(dataencoding)
            elif j == 'datetime':
                mdatetime = time.strptime(config[i][j], "%Y%m%dT%H%M%SZ")
            elif j == 'state':
                mstate = config[i][j]
            elif j == 'name':
                mname = config[i][j]
        
        mtext = re.sub(r"\n", ' ', mtext)
        
        mdate = time.strftime("%Y-%m-%d", mdatetime)
        mtime = time.strftime("%H:%M:%S", mdatetime)
        
        if mstate == 'Read' or mstate == 'UnRead':
            mstate = 'in'
        elif mstate == 'Sent' or mstate == 'UnSent':
            mstate = 'out'
        else:
            mstate = ''
        
        if mname == '""':
            mname = mnumber
        
        print(mdate+'\t'+mtime+'\t'+mstate+'\t'+mnumber+'\t'+mname+'\t'+mtext)

