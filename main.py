# -*- coding: cp1255 -*-
#!! -*- coding: utf-8 -*-
"""
Created on 20/09/19

@author: Symbiomatrix

Todo:
- Navigation function: Simple A* bfs without costs. 

Features:
Given a graph of possible movements, values, and 'specials' per node,
and dictionary of good / bad words,
constructs a trie or two from the dicts, and traverses the graph to 
find all paths leading to a viable word. 
In this game, it's hexagonal which is +-a 2d array with diagonals.
- Trie class conversion of the base dicts including search and modification.
- Graph class of connected nodes for storing game grid, hexagon tailoring.
  Contains one main dict, node key (tup), node has value + power + tup of refs. 

Future:
 

Notes:

Bugs:

Version log:
21/09/19 V0.6 Added trie and graph with input for both (mostly complete). 
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
# import Design_FT # Main - once interfaces are added.
# import Design2_FT # Query.
import time
import datetime
from pathlib import Path # v
from itertools import product # v
import hashlib
import pandas as pd
import numpy as np
import pickle
import re

import inspect
from collections import OrderedDict # v

# import requests
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import WebDriverException
# from PyQt5 import QtCore, QtGui, QtWidgets # v

# BM! Constants
FMAIN = 1 # 1 = Location list. 2 = Employee range list. 3 = Unfiltered.
Deb_Prtlog = lambda x,y = logging.ERROR:uti.Deb_Prtlog(x,y,logger)
LSTPH = uti.LSTPH
REGDELIM = "[, ]" # Delims for free input.
REINPEND = "end|fin|quit|\." # Keywords which end input.
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
RSPTMO = 999
BCKSLS = "\\"
SLSH = "/"
APOS = "\'"
QUOS = "\""
NLN = "\n"
BRKTEER = "[{}]" 
SPRTXT = """char(13) || '---' || char(13)"""
#QUOTSCP = (r"""������""","""\'\'\'\"\"\"""")
HASHDEF = 8 # Number of digits.
DEFDT = datetime.datetime(1971,1,1)
TILEGOLD = "=" # These are faster to type than +*.
TILECURSE = "-"
TILEADD = "+"
TILEREM = "/"
TILECHG = "*"
# I'm using regex based string replacements.
# Others aren't list based either, cept magicrep which needs a dict.
RETILEPOS = BRKTEER.format(TILEADD + TILEREM + TILECHG)
RETILEVAL = BRKTEER.format(TILEGOLD + TILECURSE) 

LOGMSG = uti.LOGMSG
LOGMSG.update({
"loger": "Unknown error in log encoding.\n {} {}",
"mainok": "Run completed.",
"mainer": "Run crashed, check log.",
"lfrmter1": "Insufficient parameters sent to format.",
"lfrmter2": "Excessive parameters sent to format.",
"dconvok": "Conversion completed in {} .",
"dloadok": "Load completed in {} .",
"grpinpmsg": """Please write down values for graph: columnwise l2r,
                space separate values and denote +/* for gold / cursed.""",
"grpprtmsg": "Current graph state:",
"null": "This is the end my friend."
})
METHCODES = uti.METHCODES
METHCODES.update({
"ok": (0,""),
})
REVMETHCD = {v[0]: (k,v[1]) for (k,v) in METHCODES.items()}

# BM! Defs

def ckbnd(lst1,idx):
    """Checks if the index is within bounds of an array or nested list.
    
    Index should be a list per dim, betwixt 0-len of each."""
    l1 = lst1
    i = 0
    for i in idx:
        if i < 0 or i >= len(l1):
            return False
        else:
            l1 = l1[i]
    return True

class BNtrie():
    """Trie = prefix search tree.
    
    Partially implemented: Init, search, batch add / deactivate."""
    def __init__(self,pptr = None):
        """Init."""
        self.indvalid = False
        self.refs = dict()
        self.parent = pptr
    
    def build_dict(self,lsrc,indvalid = True):
        """Adds to trie from an iterable of words. 
        
        Each word creates new nodes as needed, and finally marks validity.
        Can also cancel out existing validity."""
        for wrd1 in lsrc:
            self.search(wrd1,indvalid)
        
        return self
    
    def search(self,str1,indvalid = None):
        """Search whether string is valid in trie.
        
        Doubles as a creation function if indvalid is not null.
        Delete is currently simplified - only avoid creating nodes,
        don't cascade prune the trie."""
        indstop = False
        i = 0
        cnode = self
        while not indstop: # Traverse the trie with current word, char by char.
            chr1 = str1[i] 
            if chr1 not in cnode.refs: # Create new node if nonexistent.
                if indvalid is None: # Search is read only.
                    indstop = True
                    return False
                elif not indvalid:
                    cnode.refs[chr1] = BNtrie(cnode)
                else: # In negation mode will not create anything either.
                    indstop = True
                    return False # Freeing nodes is trickier.
            cnode = cnode.refs[chr1]
            i = i + 1
            if i >= len(str1):
                indstop = True
        if indvalid is not None: # Set value.
            cnode.indvalid = indvalid
        else:
            return cnode.indvalid
        
        return None

class BNgraph():
    """Graphs = nodes connected to one another (foregoing the edges).
    
    Since I'm lazy, should create an empty root ref for the graph.
    Partially implemented: Init, hexagonal creation."""
    root = dict()
    def __init__(self,newid,newval = None):
        """Init."""
        self.id = newid
        self.root[self.id] = self
        self.value = newval
        self.refs = dict()
    
    def addcon(self,cid):
        """Add a connection from this node to another id.
        
        Both nodes must exist - defer connecting until they're all created."""
        self.refs[cid] = self.root[cid]
    
    def build_hex(self,lsrc,indconvex = False):
        """Creates a hexagonally connected graph.
        
        Basically, it's a 2d array with alternating number of rows per column,
        which is connected in orthogonal directions and one diagonal,
        based on whether it's convex / concave, ie top left node is the highest;
        convex => even cols connected to both vals one row above (-1)
        and odd to below (+1), concave is vice versa.
        Please supply the list of values columnwise - it's the easiest to view."""
        idxr = 0
        idxc = 0
        if indconvex:
            conbase = 1
        else:
            conbase = -1
        
        # Create nodes.
        for idxc,_ in enumerate(lsrc):
            for idxr,_ in enumerate(lsrc[idxc]):
                BNgraph((idxc,idxr),lsrc[idxc][idxr])
                
        # Add their connections - orthogonal and one sided diag.
        for idxc,_ in enumerate(lsrc):
            # Due to the 0-idx setting, even and odd are reversed.
            conmod = int(((idxc % 2) * 2 - 1) * conbase)
            for idxr,_ in enumerate(lsrc[idxc]):
                if ckbnd(lsrc,(idxc,idxr - 1)):
                    self.root[(idxc,idxr)].addcon((idxc,idxr - 1))
                if ckbnd(lsrc,(idxc,idxr + 1)):
                    self.root[(idxc,idxr)].addcon((idxc,idxr + 1))
                if ckbnd(lsrc,(idxc - 1,idxr)):
                    self.root[(idxc,idxr)].addcon((idxc - 1,idxr))
                if ckbnd(lsrc,(idxc + 1,idxr)):
                    self.root[(idxc,idxr)].addcon((idxc + 1,idxr))
                if ckbnd(lsrc,(idxc - 1,idxr + conmod)):
                    self.root[(idxc,idxr)].addcon((idxc - 1,idxr + conmod))
                if ckbnd(lsrc,(idxc + 1,idxr + conmod)):
                    self.root[(idxc,idxr)].addcon((idxc + 1,idxr + conmod))
        
        return self
    
    def trieverse(self,tri1,tri2):
        """Seeks dictionary words connected uniquely in the graph.
        
        Gives 2 scores, one for longevity (clearing deep cursed tiles)
        and one for extra gold tiles."""
    

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

def Convert_Dict(indfrc = False,indsave = True):
    """Builds counter arr from raw dict, all saved to file.  
    
    If forced, will not negate "bad" dict.
    With saving, takes 1.5s for 50k words."""
    Deb_Prtlog("Start convert dict",logging.DEBUG)
    uti.St_Timer("TConvert")
    from inpdict import goodd1, goodd2, badd1, badd2 # v
    
    tri1 = BNtrie()
    tri2 = BNtrie()
    tri1.build_dict(goodd1,True)
    tri2.build_dict(goodd2,True)
    if not indfrc:
        tri1.build_dict(badd1,False)
        tri2.build_dict(badd2,False)
    
    if indsave:
        with open(BRANCH + BCKSLS + "tri1.pkl","wb") as flw:
            pickle.dump(tri1,flw)
        with open(BRANCH + BCKSLS + "tri2.pkl","wb") as flw:
            pickle.dump(tri2,flw)
    tdiff = uti.Ed_Timer("TConvert")
    Deb_Prtlog(LOGMSG["dconvok"].format(tdiff),logging.DEBUG)
    return (tri1,tri2)          

def Load_Dict():
    """Loads dictionaries from respective folders - files.
    
    Pick el pickle pickle."""
    Deb_Prtlog("Start load dict",logging.DEBUG)
    uti.St_Timer("TDload")
    
    with open(BRANCH + BCKSLS + "tri1.pkl","rb") as flr:
        tri1 = pickle.load(flr)
    with open(BRANCH + BCKSLS + "tri2.pkl","rb") as flr:
        tri2 = pickle.load(flr)
    tdiff = uti.Ed_Timer("TDload")
    Deb_Prtlog(LOGMSG["dloadok"].format(tdiff),logging.DEBUG)
    return (tri1,tri2)

def Graph_Input():
    """Graph input.
    
    Currently tailored for the game: 6/7x9 grid and value modifiers.
    Prior input can be corrected using this format: *20 g,
    with the actions + to add, / to remove, * to change.
    Note - remove also grabs a placeholder parm.
    Terminate with fin, end, quit or period.
    Creep: Make generic by passing the print function parms (dict)."""
    indstop = False
    prmchg = None
    tinp = []
    while not indstop:
        ursp = uti.Timed_Input(False,LOGMSG["grpinpmsg"],RSPTMO)
        if len(re.findall(REINPEND,ursp.lower())) > 0: # Terminate after reading.
            indstop = True
            ursp = re.sub(REINPEND,"",ursp.lower())
        cinp = re.split("[, ]",ursp)
        cedit = []
        for i,_ in enumerate(cinp):
            if len(re.findall(RETILEPOS,cinp[i])) > 0:
                # Loop could prolly be done a bit more elegantly.
                if TILEADD in cinp[i]:
                    prmchg = [1]
                if TILEREM in cinp[i]:
                    prmchg = [2]
                if TILECHG in cinp[i]:
                    prmchg = [3]
                prmchg.append(int(re.sub(RETILEPOS,"",cinp[i])))
            else:
                if TILECURSE in cinp[i]:
                    vtile = 1
                elif TILEGOLD in cinp[i]:
                    vtile = 2
                else:
                    vtile = 0
                ctile = re.sub(RETILEVAL,"",cinp[i])
                if prmchg is not None: # Alter a prior tile.
                    if prmchg[0] == 1:
                        tinp.insert(prmchg[1],(ctile,vtile))
                    elif prmchg[0] == 2:
                        tinp.pop(prmchg[1])
                    elif prmchg[0] == 3:
                        tinp[prmchg[1]] = (ctile,vtile)
                else:
                    cedit.append((ctile,vtile)) 
        tinp.extend(cedit)
        print(LOGMSG["grpprtmsg"])
        Print_Hexagrid(tinp)
            
    return tinp

def Print_Hexagrid(lval,rcnt = 6,ccnt = 9,indconvex = False):
    """Print a 2 value list on a full hexagrid of some length.
    
    The colcount is normal, row count for leftmost col,
    if convex will drop on even rows.
    Visually fitted currently in a checkered pattern.
    If the list is partially filled, prints column-row wise from top left."""
    for ridx in range(rcnt):
        for cidx in range(ccnt):
            pass
            #CONT

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
            # Trie.
            #tstrie = BNtrie()
            #tstrie.build_dict(np.array(("ziggy","wino")))
            #Convert_Dict()
            #(tri1,tri2) = Load_Dict()
            #print(list(tri1.refs["a"].refs["a"].refs["h"].refs["s"].refs.keys()))
            #print(tri1.search("aardvark"))
            
            # Graph.
            #groot = BNgraph(None)
            #groot.build_hex([[10,20,30],[11,21,31,41],[12,22,32]])
            Graph_Input()
            
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
    