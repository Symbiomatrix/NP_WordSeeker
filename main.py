# -*- coding: cp1255 -*-
#!! -*- coding: utf-8 -*-
"""
Created on 20/09/19

@author: Symbiomatrix

Todo:
- Trie class: Most basic, indword + dict of letters to other tries.
- Graph class: One main dict, node key (tup), node has value + power + tup of refs.
- Navigation function: Simple A* bfs without costs. 

Features:
Given a graph of possible movements, values, and 'specials' per node,
and dictionary of good / bad words,
constructs a trie or two from the dicts, and traverses the graph to 
find all paths leading to a viable word. 
In this game, it's hexagonal which is +-a 2d array with diagonals.  

Future:
 

Notes:

Bugs:

Version log:
20/09/19 V0.1 General structure initiated. 
20/09/19 V0.0 New.

"""

#BM! Devmode
DEVMODE = True
if DEVMODE: # DEV
#     import Lite_CC_Exp # Using "import as" in optional clause shows warning in eclipse.
#     ldb = Lite_CC_Exp
    BRANCH = "Dev\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "RTMain"
    DBFLD = BRANCH + "DBFiles"
    BADLOG = BRANCH + "Devlog-d{}.txt" 
    LOADDUM = True # Load from dum function or web. # TEMP
    RUNSELEN = True # Force selena load.
    DUMN1 = 101 # List dum.
    NAVN1 = 7220184 # Replaces pend conds, use a real one (from nav).
    TSTCOL = 4 # For a test query.
    TSTWROW = 1 
else: # PROD
#     import Lite_CC
#     ldb = Lite_CC
    BRANCH = "Prd\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "CCMain"
    DBFLD = BRANCH + "DBFiles" # Cannot use none because dbset is fixed. 
    BADLOG = BRANCH + "Logfail-d{}.txt"
    LOADDUM = False
    RUNSELEN = True # Preferable conduct to prevent detection.
    TSTCOL = 1
    TSTWROW = 1


# BM! Imports
import sys
import os
#sys.stdout = open('PrintRedir.txt', 'w')
import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    # When seeking all module logs, change bsconf to debug.
    # logging.basicConfig(stream=sys.stderr,
    #                     level=logging.ERROR, # Prints to the console.
    #                     format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    logging.basicConfig(filename=LOGFLD,
                        level=logging.WARN, # Prints to a file. Should be utf. #.warn
                        format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    logger.setLevel(logging.DEBUG)
SYSENC = "cp1255" # System default encoding for safe logging.

import utils as uti
import pdwan as pdu
BmxFrame = pdu.BmxFrame
# import Design_FT # Main - once interfaces are added.
# import Design2_FT # Query.
import time
import datetime
from pathlib import Path # v
from itertools import product # v
import hashlib
import pandas as pd
import numpy as np

import inspect
from collections import OrderedDict # v

pd.set_option("display.width",140)
pd.set_option("display.max_columns",8)

# import requests
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import WebDriverException
# from PyQt5 import QtCore, QtGui, QtWidgets # v

# BM! Constants
FMAIN = 1 # 1 = Location list. 2 = Employee range list. 3 = Unfiltered.
Deb_Prtlog = lambda x,y = logging.ERROR:uti.Deb_Prtlog(x,y,logger)
LSTPH = uti.LSTPH
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
BCKSLS = "\\"
SLSH = "/"
APOS = "\'"
QUOS = "\""
NLN = "\n"
SPRTXT = """char(13) || '---' || char(13)"""
#QUOTSCP = (r"""‘’‚“”„""","""\'\'\'\"\"\"""")
HASHDEF = 8 # Number of digits.
DEFDT = datetime.datetime(1971,1,1)
TSTMON = pd.date_range("2019-01-01","2019-02-01",closed="left")
NARCOLEPSY = 0.5 * pdu.HOUR # Max time for rest / wake (uniform distro).
INSOMNIA = pdu.HOUR # They may still be merged to a longer period.
GENRULER2 = ["pid","day","sylladex","ostatus","ostart","oend","rdur"]

LOGMSG = uti.LOGMSG
LOGMSG.update({
"null": "This is the end my friend."
})
METHCODES = uti.METHCODES
METHCODES.update({
"ok": (0,""),
})
REVMETHCD = {v[0]: (k,v[1]) for (k,v) in METHCODES.items()}
uti.FDEFS.update({
"Gensmp":{"cntid":10,"prvid":None,"dfpid":None,
          "dfdays":TSTMON,"tmday":"07:00","tmngt":"22:00","uvar":4,
          "sttday":4,"sttngt":2},
})

# BM! Defs

def DebP_Curbod(curbod,htmlbod,windlen = 30):
    """Short segment for print around list markers in long text.
     
    For debug."""
    for i,_ in enumerate(curbod):
        if curbod[i] != 0:
            st = max(curbod[i] - round(windlen / 2),0)
            ed = curbod[i] + round(windlen / 2)
            print(i,curbod[i],": ",repr(htmlbod[st:ed]))
            
def DebP_Select(seldb,ftc = 1000):
    """Fetches in iterations, prints to console with timers in log.
    
    Spam."""
    scur = "DO"
    pwid = None
    i = 0
    while scur is not None: # Make sure scur is sent back, otherwise generating inf loop.
        uti.St_Timer("Dbprint")
        if len(scur) == 2: # Comparison is bothersome.
            scur = None
        (lrecs,scur,heads) = seldb.Select_Recs(ftc,oldrun = scur)
        if pwid is not None: # Start indicator.
            heads = None
        edind = scur is None # No need for additional ind.
        pwid = seldb.Print_Sel(lrecs,heads,edind,pstwid = pwid)
        i = i + 1
        tdiff = uti.Ed_Timer("Dbprint")
        logger.debug("Batch {} time: {}".format(i,tdiff))
        
def Status_Times(vtyp,df,kday):
    """Create status start + end along the day.
    
    1 = narcolepsy from morn to night.
    2 = insomnia from night to next morn."""
    if vtyp == 1:
        kcnt = "sttday"
        kfrom = "twake"
        kto = "tsleep"
        nstat = 4
        mxdur = NARCOLEPSY
    elif vtyp == 2:
        kcnt = "sttngt"
        kfrom = "tsleep"
        kto = "tnwake"
        nstat = 5
        mxdur = INSOMNIA
    df["newrow"] = df[kcnt] + 1
    dfst = df.Expandong("newrow")
    # Multiindex is inconvenient as hell. There's groupby level,
    # but it's more statistical. Cannot seem to shift it directly.
    dfst["twake"] = df["twake"]
    dfst["tnwake"] = df["tnwake"]
    dfst["tsleep"] = df["tsleep"]
    dfst.reset_index(inplace = True)
    dfst["firstrec2"] = ((dfst["pid"] != dfst["pid"].shift(1)) |
                         (dfst[kday] != dfst[kday].shift(1)))
    dfst["lastrec2"] = ((dfst["pid"] != dfst["pid"].shift(-1)) |
                         (dfst[kday] != dfst[kday].shift(-1)))
    dfst["grp2"] = dfst["firstrec2"].cumsum()
    dfst["raindeer"] = dfst.Rand_DirichletG(group = "grp2")
    dfst["crane"] = dfst.groupby(dfst["grp2"])["raindeer"].cumsum()
    dfst["tdiff"] = dfst[kto] - dfst[kfrom]
    dfst["ostart"] = dfst[kfrom] + dfst["crane"] * dfst["tdiff"]
    dfst["ostatus"] = nstat
    dfst["rdur"] = dfst.Rand_Time(ubnd = mxdur)
    dfst["oend"] = dfst["ostart"] + dfst["rdur"]
    return dfst

def Generate_Samples(vtyp = 1,**parms):
    """Creates a frame of ids, statuses or vitals.
    
    Ids = 1, stat = 2, vit = 3.
    For stat / vit, send ids for which to generate data,
    and optionally dates."""
    vret = None
    rund = uti.Default_Dict("Gensmp",parms)
    if vtyp == 1: # Pid.
        df = BmxFrame(rcnt = rund["cntid"])
        if not rund["prvid"]: # Creates new patients randomly.
            df.Hash_Ids(kout = "pid",indrnd = True)
        else: # Series of ids for 'guaranteed' randomness.
            df.index = df.index + rund["prvid"] + 1
            df.Hash_Ids(kout = "pid",indrnd = False)
        vret = df
    elif vtyp == 2: # Status.
        if rund["dfpid"] is not None: # Currently necessary.
            dfdays = rund["dfdays"] # Pid should not be a key.
            if not isinstance(dfdays,BmxFrame):
                kday = "day"
                dfdays = BmxFrame(dfdays,columns = [kday])
            else:
                kday = dfdays.columns[0]
            df = rund["dfpid"].Cross_Join(dfdays)
            df["sttday"] = df.Rand_Norm(vstd = rund["sttday"],indint = True)
            df["sttngt"] = df.Rand_Norm(vstd = rund["sttngt"],indint = True)
            # Select entry & exit time at edges.
            # Creep: Chance of none.
            df["seed"] = df.Rand_Norm(indint = False) # Hours added or negated.
            df["twake"] = (df[kday] +
                            df.To_Time(rund["tmday"]) +
                            df.Rand_Time(rund["uvar"]) -
                            df.To_Time(rund["uvar"]) / 2)
            df["tsleep"] = (df[kday] +
                           df.To_Time(rund["tmngt"]) +
                           df.Rand_Time(rund["uvar"]) -
                           df.To_Time(rund["uvar"]) / 2)
            df["lastrec"] = df["pid"] != df["pid"].shift(-1)
            df["tnwake"] = df["twake"].shift(-1) # Used in random later.
            df.loc[df["lastrec"],"tnwake"] = df["twake"] + pdu.DAY # Estimated.
            # Periods in between ought to occupy a small fraction of the day.
            # Method to get the exact quantity - diri distro with n + 1 items,
            # such that the first n items represent start times (cumulative),
            # and the +1 is the sleep / wake; then randomly set the break lengths.
            # Crossjoin resets (wipes) keys, have to prepare them for expansion.
            df.set_index(["pid",kday],inplace = True)
            df["newrow"] = df["sttday"] + 1 
            dfst1 = Status_Times(1,df,kday)
            dfst2 = Status_Times(2,df,kday)
            dfstat = pd.concat([dfst1,dfst2])
            dfstat.sort_values(["pid",kday,"ostart"],inplace = True)
            dfstat["lastrec"] = (dfstat["pid"] != dfstat["pid"].shift(-1))
            # Day's end / beginning is expanded, up to next record.
            # Inner wakings / rests still need to be filled with more records.
            # Bools don't work with shift due to nans.
            dfstat["nstart"] = dfstat["ostart"].shift(-1)
            dfstat.loc[dfstat["lastrec2"],"oend"] = (
                dfstat.loc[dfstat["lastrec2"],"nstart"])
            dfstat.loc[dfstat["lastrec"],"oend"] = (
                dfstat.loc[dfstat["lastrec"],"tnwake"])
            dfstat.loc[dfstat["lastrec2"],"rdur"] = (
                dfstat.loc[dfstat["lastrec2"],"oend"] -
                dfstat.loc[dfstat["lastrec2"],"ostart"])
            dfstat = dfstat.Period_Overlap(id = ["pid","ostatus"],tstart = "ostart",
                                           tend = "oend",rdur = "rdur")
                        
            vret = BmxFrame(dfstat[GENRULER2])
    return vret

# BM! MAIN()
def Main_Test():
    """Short activation.
    
    Spam."""
    global galena
    Deb_Prtlog("Start main TEST",logging.DEBUG)
    uti.St_Timer("Main")
    
#     dbrefs = Init_Parms()
#     (cmpdb,infdb,dbini) = dbrefs
    indstop = False
    verr = 0
    btc = 100 # dbini["Main"][INIBTC]
#     ddl = ldb.Date_Conv(dbini["Main"][INIDDL])
#    from Rawdt_LDL import lwin
#    lfail = [("Crystal_Babyface-2000-11-27.jpg","19-Sep-2001 19:44 ","7.9K"),
#             ("Crystal_Babyface.jpg","19-Sep-2001 19:44 ","7.9K"),
#             ("abreik_meerca-.jpg","01-Apr-2018 22:43 ","65K")]
#    tstdl = "http://upload.neopets.com/beauty/images/winners/silkmon-2012-05-11.jpg"
    while not indstop:
        if 1 != 0:
            dfpid = Generate_Samples(1)
            dfpid.Save_Frame("test_pid.csv")
            dfstat = Generate_Samples(2,dfpid = dfpid)
            dfstat.Save_Frame("test_stat.csv")
#             imgdb.Kill_Cur(pendtop[1],False) # Locks db for update.
# Compare req-selena.
#             tsturl = r"https://archive.help-qa.com/history/few-replies//8"
#             (verr,tmpbrw) = Req_Page(tsturl)
#             htmlbod1 = tmpbrw.text
#             uti.Write_UTF(BADHTML.format(1,1),htmlbod1,True)
#             (verr,tmpbrw) = Selen_Page(tsturl,tslp=180)
#             galena = tmpbrw
#             htmlbod2 = tmpbrw.page_source
#             uti.Write_UTF(BADHTML.format(1,2),htmlbod2,True)
#             galena.quit()
# Find test.
#             tstt = Find_Loop_Repl("""One of you, "ladies'""","s{punc}",1, False, 0)
#             print(tstt)
# Dummy.
#            verr = Build_Crawl(dbrefs,btc,ddl)
#            verr = Build_List(dbrefs,lwin,ddl)
#            verr = Build_List(dbrefs,lfail,ddl)
#            verr = Grab_Webfile(tstdl)
#            verr = Seize_Links(dbrefs)
#             verr = Mine_Yeda(dbrefs,1)
#             verr = Mine_List(dbrefs)
#             verr = Build_Crawl(dbrefs,922,10)
#             verr = Close_Dupe_Topics(dbrefs)
#             verr = Read_All_Topics(dbrefs,pendtop)
# Selects.
#             verr = Review_Dbs(dbrefs,[1,2,3])
            print(verr)
            indstop = True # TEST
        else:
            indstop = True # All done.
            
    
    tdiff = uti.Ed_Timer("Main")
    print("\nFin.")
    # Remember that timestamp is automatic in logger.
    logger.debug("End main {}".format(tdiff))
    
    return verr

def Main():
    """Activates function calls.
    
    Main."""
    Deb_Prtlog("Start main",logging.DEBUG)
    uti.St_Timer("Main")
    
    verr = 0
#     dbrefs = Init_Parms()
    if FMAIN in (1,2,3,9):
#         verr = Mine_Yeda(dbrefs,FMAIN)
        verr = 0
    elif FMAIN == 8:
#         verr = Mine_List(dbrefs)
        verr = 0
    elif FMAIN == 11:
#         verr = Review_Dbs(dbrefs,QUERYLIST)
        verr = 0
    
    tdiff = uti.Ed_Timer("Main")
    print("\nFin.")
    # Remember that timestamp is automatic in logger.
    logger.debug("End main {}".format(tdiff))
    if verr == 0:
        uti.Msgbox(LOGMSG["mainok"],"Good morning chrono")
    else:
        uti.Msgbox(LOGMSG["mainer"],"Wake up")
    
    return verr
    
if __name__ == "__main__":
    if DEVMODE:
        Main_Test()
    else:
        Main()
    
