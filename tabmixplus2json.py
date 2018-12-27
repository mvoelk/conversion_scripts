#!/usr/bin/python

# Converts browser sessions from RDF (Tab Mix Plus by onemen) to 
# JSON (Tab Session Manager by sienori).
#
# usage: ./tabmixplus2tabsessionmanager.py session.rdf
# output: session.json
#
# author: Markus Völk
# date: 2017-12-25


import rdflib
import json
import urllib
import os
import sys
from datetime import datetime

NC = rdflib.Namespace("http://home.netscape.com/NC-rdf#")


class IDCounter(object):
    def __init__(self):
        self.current_id = 0
    
    def new_id(self):
        self.current_id += 1
        return self.current_id


if len(sys.argv) < 2:
    exit('usage: ' + sys.argv[0] + ' <inputfile>')

file_name = str(sys.argv[1])

if not os.path.isfile(file_name):
    exit('file not found')


with open(file_name, 'r') as f:
    data = f.read()

data = data.replace(' NC:parseType=', ' RDF:parseType=')

g = rdflib.Graph()
g.parse(data=data, format="xml")


counter = IDCounter()

sessions = []

# sessions
for s in g.seq(rdflib.URIRef('rdf://tabmix/windows')):
    if g.seq(s) is None: continue # for minimal test RDF
    #print(g.value(s, NC.name))
    #print(g.value(s, NC.nameExt))
    
    windows = {}
    windows_info = {}
    
    num_windows = 0
    num_tabs = 0
    
    name_ext = str(g.value(s, NC.nameExt))
    dt = datetime.strptime(name_ext[-20:-1], '%Y/%m/%d %H:%M:%S')
    time_stamp = int(dt.timestamp() * 1000)
    
    # windows
    for w in g.seq(s):
        #print(g.value(w, NC.SSi))
        #print(g.value(w, NC.status))
        #print(g.value(w, NC.tabs))
        #print(g.value(w, NC.closedtabs))
        #print(g.value(w, NC.selectedIndex))
        
        window_id = counter.new_id()
        num_windows += 1
        tabs = {}
        
        # tabs
        for t in g.seq(g.value(w, NC.tabs)):
            if g.value(t, NC.properties) is None: continue # for minimal test RDF
            #print(g.value(t, NC.image))
            #print(g.value(t, NC.properties))
            #print(g.value(t, NC.history))
            #print(g.value(t, NC.historyData))
            #print(g.value(t, NC.scroll))
            #print(g.value(t, NC.tabPos))
            #print(g.value(t, NC['index']))
            
            tab_id = counter.new_id()
            num_tabs += 1
            
            history = g.value(t, NC.historyData)
            if history is None:
                history = g.value(t, NC.history)
                history = urllib.parse.unquote(history)
                history_split = history[5:].split('][')
                history = []
                for i in range(len(history_split)//3):
                    history.append({
                        'title': history_split[i*3+0],
                        'url': history_split[i*3+1],
                        'scroll': history_split[i*3+2],
                        'triggeringPrincipal_base64': None
                    })
            else:
                history = json.loads(urllib.parse.unquote(history))
            tab = history[int(g.value(t, NC['index']))]
            
            tabs[tab_id] = {
                    "id": tab_id,
                    "index": int(g.value(t, NC.tabPos)),
                    "windowId": window_id,
                    "highlighted": False,
                    "active": False,
                    "attention": False,
                    "pinned": False,
                    "status": "complete",
                    "hidden": False,
                    "discarded": False,
                    "incognito": False,
                    "width": 1434,
                    "height": 904,
                    "lastAccessed": time_stamp,
                    "audible": False,
                    "mutedInfo": {
                        "muted": False
                    },
                    "isArticle": False,
                    "isInReaderMode": False,
                    "sharingState": {
                        "camera": False,
                        "microphone": False
                    },
                    "cookieStoreId": "firefox-default",
                    "url": tab['url'],
                    "title": tab['title'],
                    "favIconUrl": str(g.value(t, NC.image))
                }

        windows[window_id] = tabs
        
        windows_info[window_id] = {
                "id": window_id,
                "focused": False,
                "top": 0,
                "left": 0,
                "width": 1680,
                "height": 995,
                "incognito": False,
                "type": "normal",
                "state": "maximized",
                "alwaysOnTop": False,
                "title": str(g.value(w, NC.SSi))
            }
        
    session_id = counter.new_id()
    
    session = {
        "windows": windows,
        "windowsNumber": num_windows,
        "windowsInfo": windows_info,
        "tabsNumber": num_tabs,
        "name": urllib.parse.unquote(str(g.value(s, NC.name))),
        "date": time_stamp,
        "tag": [],
        "sessionStartTime": time_stamp,
        #"id": session_id
        }
    
    sessions.append(session)

with open(file_name[:-4]+'.json', 'w+') as f:
    f.write(json.dumps(sessions))



# reverse engineering of tab properties
# 
# NC:properties="0011111 hidden=false"
# 
# # binary
# 1 protected
# 2 locked
# 3 
# 4 
# 5 
# 6 
# 7 
# 
# # string
# tabgroups-data=
# faviconized=
# pinned=
# hidden=
# ctreadonly=
# tabClr=
# treestyletab-=
