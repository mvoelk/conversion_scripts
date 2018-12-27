#!/usr/bin/python

# Converts phone contacts from Wammu/Gammu to CSV so they can be imported 
# under Android.
#
# usage: ./wammubackup2csv.py K800i_2012-01-05.backup > contacts_20120105.vcf
#
# author: Markus Völk
# date: 2012-01-07


import os
import sys
import locale
import configparser
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
    if i.startswith('SIMPBK'):
        cname = ''
        cnumber = ''
        
        for j in config[i]:
            #if j.startswith('entry') and j.endswith('type'):
            if re.match(r"^entry\d\dtype$", j):
                entrytype = config[i][j]
                entrytext = config[i][re.sub(r"type$", 'text', j)][1:-1]    # TODO
                
                if entrytype == 'Name':
                    cname = entrytext
                elif entrytype == 'NumberGeneral':
                    cnumber = entrytext
        
        cname = re.sub(r"/.$", '', cname)
        
        res = re.split(r" (?=[^ ]*$)", cname)
        if len(res) == 2:
            cfname = res[0]
            clname = res[1]
        else:
            cfname = cname
            clname = ''
            
        print('BEGIN:VCARD\nVERSION:3.0\nN:'+clname+';'+cfname+';;;\nFN:'+cname+'\nTEL;TYPE=VOICE;TYPE=PREF:'+cnumber+'\nEND:VCARD')


