#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmltodict
import os
from datetime import datetime as dt
import pandas as pd

version = "1.03"        #  23/07/19
appdir = os.path.dirname(os.path.abspath(__file__))
datafile = appdir + "./sample.xml"
outfile = appdir + "./itlist.htm"
templatefile = appdir + "./template.htm"
conffile = appdir + "./itlist.conf"
out = ""
df = ""
df_s = ""
index_table = {}   #  キー  作曲者  値   作曲者先頭曲のindex
index_list  = []    #  作曲者先頭曲のindex のリスト

def main_proc():
    read_config()
    read_music_xml()
    create_index_table()
    parse_template()

def read_config() :
    global datafile
    if not os.path.isfile(conffile) :
        return
    conf = open(conffile,'r', encoding='utf-8')
    datafile = conf.readline().strip()    

def read_music_xml() :
    global df,df_s
    with open(datafile, encoding='utf-8') as f:
        doc = xmltodict.parse(f.read())

    n = len(doc['plist']['dict']['dict']['dict'])
    compcate = [] 
    mtitle = []
    player = []
    filepath = []
    totaltime = []
    playdate = []
    adddate = []
    trackid = []
    pcount = []
    for i in range(0,n) :
        item = doc['plist']['dict']['dict']['dict'][i]
        
        trackid.append(item['integer'][0])
        compcate.append(item['string'][3])
        mtitle.append(item['string'][2])
        if 'Album' in item['key'] :       # player   Album キーがない場合があるので
            if 'Composer' in item['key'] :
                playername = item['string'][5]
            else :
                playername = item['string'][4]
        else :
            playername = ""
        player.append(playername)
        n = omitted_string_key(item['key'])
        k = add_string_key(item['key'])
        filepath.append(item['string'][8-n+k])
        #print("=> " + item['string'][8-n+k])
        totaltime.append(item['integer'][2])
        if 'Play Date UTC' in item['key'] :
            playdate.append(item['date'][2])
        else :
            playdate.append("")
        adddate.append(item['date'][1])
        n = omitted_interger_key(item['key'])
        pcount.append(item['integer'][10-n])

    df = pd.DataFrame(list(zip(compcate,mtitle,player,totaltime,playdate,adddate,filepath,trackid,pcount))
        , columns = ['compc','title','player','time','playdate','adddate','path','trackid','pcount'])
    df_s = df.sort_values(by=['compc','trackid'])

def create_index_table():
    global index_table,comp_table

    old = ""
    i = 0 
    for _,row in df_s.iterrows() :
        i = i + 1
        comp = row.compc
        if comp[-1].isdigit() :     # 最後の文字が数字ならそれを取る  数字はジャンルコード
            comp = comp[:-1]
        if comp != old :
            index_table[comp] = i
            index_list.append(i)
            old = comp
        
def dislpay_index_part() :
    for comp , i in index_table.items() :
        out.write(f'<a href="#{i}">{comp}</a><br>\n')


def mlist_table():
    i = 0 
    for index,row in df_s.iterrows() :
        i = i+1
        mmss = int(row.time) / 1000
        min = int(mmss / 60 )
        sec = int(mmss % 60)
        pdate = str(row.playdate)
        playcount = row.pcount
        if pdate != "" :
            pdate = pdate[2:10].replace('-','/')
        else :
            playcount = 0
        adate = str(row.adddate)
        adate = adate[2:10].replace('-','/')
        comp = row.compc
        if comp[-1].isdigit() :     # 最後の文字が数字ならそれを取る  数字はジャンルコード
            comp = comp[:-1]
        linkid = ""
        if i in index_list :
            linkid = f'id="{i}"'


        out.write(f'<tr><td align="right" {linkid}>{i}</td><td>{comp}</td>'
                  f'<td><a href="{row.path}" target="_blank">{row.title}</a></td>'
                  f'<td>{row.player}</td><td align="right">{min}:{sec:02}</td>'
                  f'<td align="right">{playcount}</td>'
                  f'<td align="right">{pdate}</td>'
                  f'<td align="right">{adate}</td></tr>\n')

# 以下のキーを含まないものは file path のインデックスがずれる(減少)のでその分、プラスする
def  omitted_string_key(keylist) :
    all_key = ['Composer','Album','Genre','Kind']
    n = 0 
    for k in all_key :
        if k not in keylist :
            n = n + 1
    return(n)

#  以下のキーを含むものは file path のインデックスがずれる(増加)のでその分、マイナスする
def  add_string_key(keylist) :
    all_key = ['Sort Name','Sort Album','Sort Artist','Sort Album Artist']
    n = 0 
    for k in all_key :
        if k in keylist :
            n = n + 1
    return(n)

def  omitted_interger_key(keylist) :
    all_key = ['Disc Number','Disc Count','Track Number','Track Count','Year','Bit Rate','Sample Rate']
    n = 0 
    for k in all_key :
        if k not in keylist :
            n = n + 1
    return(n)

def parse_template() :
    global out 
    f = open(templatefile , 'r', encoding='utf-8')
    out = open(outfile,'w' ,  encoding='utf-8')
    for line in f :
        if "%mlist_table%" in line :
            mlist_table()
            continue
        if "%index_table%" in line :
            dislpay_index_part()
            continue

        out.write(line)

    f.close()
    out.close()
# ----------------------------------------------------------
main_proc()

