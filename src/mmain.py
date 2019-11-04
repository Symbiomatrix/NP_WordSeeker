# -*- coding: cp1255 -*-
#!! -*- coding: utf-8 -*-
"""
Created on 20/09/19

@author: Symbiomatrix

Todo: 
- Finishing touches to main. Make it more robust to bad input.

Features:
Given a graph of possible movements, values, and 'specials' per node,
and dictionary of good / bad words,
constructs a trie or two from the dicts, and traverses the graph to 
find all paths leading to a viable word. 
In this game, it's hexagonal which is +-a 2d array with diagonals.
- Trie class conversion of the base dicts including search and modification.
- Graph class of connected nodes for storing game grid, hexagon tailoring.
  Contains one main dict, node key (tup), node has value + power + tup of refs.
- Navigation function: Prolly based on dijkstra, checks all graph routes 
    available on the dict tries.
- In number mode (via main func or gui), matches digits of variable difference.
- Select combo and drop next layer. Consists of combo removal,
  curse dig (if not over a chain link), singular transposition (unpredictable).
GUI - Persistent state of the grid, colouration of special tiles,
commit / rollback with single undo, dynamic alloc of tiles (per the same funcs),
free mode swap, drop.

Future:
- Improve ui - modifier on left side by def (even when sequential);
  kinda unnecessary with the gui being much better, but not in new boards.
- Numverse is very intense in simple grids.
  The optimal plan of culling nodes is ideal, but picking maximal results may work.

Notes:
- Chain formula: score = clength * (1 + 3 * [gold tiles]) * base
  Base is 100 for symbols, 300 for digits (prolly an oversight), varies per letters.
  The letter value is semi dependent on the letter (eg X seems to be 300 always),
  but may vary within the same grid. The tiny yellow dots in each tile show it.
  Possibly useful to create a general guidelines, but it's negligible.
  I'm 95% certain the reason for discrepancies is that shuffle doesn't alter tvalue.
- Annoyingly, py and regexr alternation operators (|) seem to agree on picking the first,
  rather than LONGEST match, despite documentation.
  This make prefix override suffix, splitting the modifier away,
  unless prevented somehow. This I did by negative lookahead of the suffix,
  in the special case of single tile (eg 5-$), otherwise next tile takes prefix.
  Of course, 5-5- breaks it (first mod to second tile and second mod standalone),
  but that's technically correct - prefix overrides suffix.
  # RETILEPREF = ([=-]?.)|(.[=-]?) # Simple version, 5- -> (5,-).

Bugs:
Yes please.

Version log:
04/11/19 V2.4 Upgraded graph inp to handle sequential tiles (both ints and mods),
                1X tiles and to use valconv. It is quite robust now.
03/11/19 V2.3 Numverse's max iters reduced to 10% for simple (123) grids (100k).
                Added further culling of chains by length to 50% (41.3k).
                Together, these prevent the gui from freezing 20s+.
                Redesigned valconv to flatten any format correctly.  
03/11/19 V2.2 Added tile move (combo selection only). - ALPHA RELEASE
01/11/19 V2.1 Number mode complete, gui mostly done,
                including selection colour gradients and conveniences.
                Rearranged package structure somewhat. It's not great.
29/10/19 V2.0 Beginning number mode, drop and new gui.
21/09/19 V1.2 Added clear keyword.
                Enabled singular string input (split to single chars).
21/09/19 V1.1 Changed to prod, created main functions.
                Major bugfix in create trie.
                Added much needed reprint of input for copypastaing,
                and minimised print during input to request (via qm keyword). 
21/09/19 V1.0 Added trieversal, print hexagrid, score sort & print.
                HANDLE WITH CARE.
21/09/19 V0.6 Added trie and graph with input for both (mostly complete). 
20/09/19 V0.1 General structure initiated. 
20/09/19 V0.0 New.

"""

#BM! Devmode
DEVMODE = True
if DEVMODE: # DEV
#     import Lite_CC_Exp # Using "import as" in optional clause shows warning in eclipse.
#     ldb = Lite_CC_Exp
    import loadgui
    mgui = loadgui
    BRANCH = "Dev\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "IniMain"
    DBFLD = BRANCH + "DBFiles"
    BADLOG = BRANCH + "Devlog-d{}.txt" 
    #INDGUI = True # Set in main func since it covers all modes.
    LOADDUM = True # Load from dum function or web. # TEMP
    RUNSELEN = True # Force selena load.
    DUMN1 = 101 # List dum.
    NAVN1 = 7220184 # Replaces pend conds, use a real one (from nav).
    TSTCOL = 4 # For a test query.
    TSTWROW = 1 
else: # PROD
#     import Lite_CC
#     ldb = Lite_CC
    import loadgui
    mgui = loadgui
    BRANCH = "Prd\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "IniMain"
    DBFLD = BRANCH + "DBFiles" # Cannot use none because dbset is fixed. 
    BADLOG = BRANCH + "Logfail-d{}.txt"
    #INDGUI = True
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
from collections import deque # v

# import requests
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import WebDriverException
# from PyQt5 import QtCore, QtGui, QtWidgets # v

# BM! Constants
FMAIN = 11 # 1 = Create dict trie. 2 = Looped word search.
# 3 = Number series search, 11 = gui (multipurpose).
Deb_Prtlog = lambda x,y = logging.ERROR:uti.Deb_Prtlog(x,y,logger)
LSTPH = uti.LSTPH
REDELIM = "[, \n]" # Delims for free input.
REINPEND = ";end|;fin|;quit|\." # Keywords which end input.
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
#QUOTSCP = (r"""‘’‚“”„""","""\'\'\'\"\"\"""")
HASHDEF = 8 # Number of digits.
DEFDT = datetime.datetime(1971,1,1)
MINCHAIN = 3
TILEGOLD = "=" # These are faster to type than +*.
TILECURSE = "-"
TILEQM = "?"
TILECLR = "$"
TILEADD = "+"
TILEREM = "/"
TILECHG = "*"
# I'm using regex based string replacements.
# Others aren't list based either, cept magicrep which needs a dict.
RETILEPOS = BRKTEER.format(TILEADD + TILEREM + TILECHG)
RETILEACT = BRKTEER.format(TILEQM + TILECLR)
RETILEVAL = BRKTEER.format(TILEGOLD + TILECURSE)
# Single char only, mod always prefix other than single tile.
RETILEPREF = "([=-]?.(?![=-]$))|(.[=-]?)"
RETILEDIG2 = "([=-]?1\d)|(1\d[=-]?)" # Potential double digit.
#RETILEPREF = "[=-]?(1\d|(.))" # Single char or 10-19, but confused by single digits.
TILENORM2 = 0
TILECURSE2 = 1
TILEGOLD2 = 2
TILEVAL2 = (" " + TILECURSE + TILEGOLD,
            str(TILENORM2) + str(TILECURSE2) + str(TILEGOLD2))
SCLET = [("ADEGHILNORSTU".lower(),100),
         ("BCFKMPQVWY".lower(),200),
         ("JXZ".lower(),300),
         ("0123456789".lower(),300) # Slightly lazy approach.
         ]
MAXCLR = 255
MINCLR = 20
MAXCLR2 = 200 # In combos only.
DCOLOUR = {"gold":(2,(MAXCLR,MAXCLR,0,MAXCLR)),
           "curse":(1,(0,MAXCLR,0,MAXCLR)),
           "normal":(0,(None,None,None,None)),
           "combo":(-1,(LSTPH,LSTPH,LSTPH,LSTPH)),
           "step":(-2,(MAXCLR,0,0,MAXCLR)),
           "parti":(-3,(0,0,MAXCLR,MAXCLR)),
           "error":(-9,(MAXCLR,0,0,MAXCLR))}
MAXCHAIN = 41300
MAXCMB = 10

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
"trievrok": "Completed trieversal in {} .",
"numvrok": "Completed numversal with {} chains in {} .",
"numvrprog": "Numverse {}% exhaustion in {} .",
"cullchok": "Number of chains after culling {} in {} .",
"wordscprog":"Scoring ~{}% complete in {}.",
"wordscok":"Completed scoring in {}.",
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
                elif indvalid:
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
        and one for max score with extra gold tiles.
        Observe the score formula - a single gold tile outweighs
        pretty much any chain length.
        Queue format: Chain (list of ids),current graph node,
        current tri1 / tri2 nodes (separate checks)."""
        logger.debug("Start trieverse")
        uti.St_Timer("trieverse")
        vque = deque()
        # Start from any letter and no match.
        for k in self.root.keys():
            if k is not None:
                nnode = self.root[k]
                vque.append(([k],nnode,
                             tri1.refs[nnode.value[0]]))
                vque.append(([k],nnode,
                             tri2.refs[nnode.value[0]]))
        
        # In a dfs loop, check if any adjacent gns have trie depth,
        # and any valid results along the way are stored for later.
        # Do not repeat routes - skip neighbour if on the chain.
        stopme = 1000000 # 10000 in 0.021s, so speed is no issue at all.
        cntstop = 0
        lres = []
        while vque:
            (lchain,cnode,ctri) = vque.pop()
            if ctri.indvalid:
                lres.append(lchain)
            for k in cnode.refs.keys():
                if not k in lchain:
                    nnode = cnode.refs[k]
                    nchain = lchain[:]
                    nchain.append(k)
                    if nnode.value[0] in ctri.refs:
                        vque.append((nchain,nnode,
                                     ctri.refs[nnode.value[0]]))
            
            cntstop = cntstop + 1
            if cntstop >= stopme:
                vque = None   
            
        tdiff = uti.Ed_Timer("trieverse")
        Deb_Prtlog(LOGMSG["trievrok"].format(tdiff),logging.DEBUG)
        return lres
    
    def numverse(self,srdiff = 1):
        """Seeks relevant geometric series connected uniquely in the graph.
        
        Gives 2 scores, one for longevity (clearing deep cursed tiles)
        and one for max score with extra gold tiles.
        Observe the score formula - a single gold tile outweighs
        pretty much any chain length.
        Queue format: Chain (list of ids), current graph node."""
        logger.debug("Start numverse")
        uti.St_Timer("numverse")
        vque = deque()
        # Start from any letter and no match.
        for k in self.root.keys():
            if k is not None:
                nnode = self.root[k]
                vque.append(([k],nnode))
        
        # In a dfs loop, check if any adjacent gns have trie depth,
        # and any valid results along the way are stored for later.
        # Do not repeat routes - skip neighbour if on the chain.
        # Numverse actually has many more options;
        # Optimisation involves finding the least connected nodes
        # for starting points in every subgraph (all of them),
        # but I'm not sure that's a perfect cover.
        # Relying on past chains is difficult due to uniqueness cond.
        # Mayhap the best method is filtering all irrelevant cons prematurely. 
        stopme = 1000000
        cntstop = 0
        lres = []
        while vque:
            (lchain,cnode) = vque.pop()
            if len(lchain) > MINCHAIN:
                lres.append(lchain)
            for k in cnode.refs.keys():
                if not k in lchain:
                    nnode = cnode.refs[k]
                    nchain = lchain[:]
                    nchain.append(k)
                    if abs(int(nnode.value[0]) -
                           int(cnode.value[0])) == srdiff:
                        vque.append((nchain,nnode))
            
            cntstop = cntstop + 1
            if cntstop % (stopme // 10) == 0:
                tdiff = uti.Ed_Timer("numverse")
                Deb_Prtlog(LOGMSG["numvrprog"].format(
                            cntstop // (stopme // 100),tdiff),logging.DEBUG)
            if cntstop >= stopme:
                vque = None   
            
        tdiff = uti.Ed_Timer("numverse")
        Deb_Prtlog(LOGMSG["numvrok"].format(len(lres),tdiff),logging.DEBUG)
        return lres
    
    def Cull_Chains(self,lres,ncull = MAXCHAIN):
        """When there are too many chains, removes a percentage by len.
        
        Creep: Counting the gold / curse prematurely may improve or obviate this,
        wordscore would be O(1) and score based culling. Bit extra memory though."""
        uti.St_Timer("cullchain")
        if len(lres) <= ncull:
            return lres
        dlen = dict()
        for lchain in lres:
            len1 = len(lchain)
            dlen[len1] = dlen.get(len1,0) + 1
        tcnt = 0
        maxcull = None
        for len1 in sorted(dlen.keys(),reverse = True):
            tcnt = tcnt + dlen[len1]
            if tcnt > ncull and maxcull is None:
                maxcull = len1
        lres = [lchain for lchain in lres if len(lchain) >= maxcull]
        
        tdiff = uti.Ed_Timer("cullchain")
        Deb_Prtlog(LOGMSG["cullchok"].format(len(lres),tdiff),logging.DEBUG)
        return lres
    
    def Word_Score(self,lres):
        """Grades word combos based on danger and value.
        
        See score formula above.
        As for danger, whilst removing 2+ tiles below cursed is bad,
        it's most important to rank depth exponentially (game over at bottom).
        Don't actually measure depth precisely, but the exp should suffice."""
        uti.St_Timer("wordscore")
        lsort = []
        lres = self.Cull_Chains(lres)
        for lchain in lres:
            vscore1 = 0
            vscore2 = 0
            gcnt = 0
            for cid in lchain:
                try:
                    (cchr,ctyp) = self.root[cid].value
                except Exception as err:
                    print(err)
                    raise
                if ctyp == TILECURSE2: # Cursed penalty is heavier by row.
                    vscore2 = vscore2 + 100 * (4 ** cid[1])
                elif ctyp == TILEGOLD2:
                    gcnt = gcnt + 1
                # Letter value check. Dict should be equivalent.
                for chksc in SCLET: 
                    if str(cchr) in chksc[0]:
                        cmod = chksc[1]
                vscore1 = vscore1 + cmod
                vscore2 = vscore2 + cmod
            vscore1 = vscore1 * (1 + gcnt * 3)
            vscore2 = vscore2 * (1 + gcnt * 3)
            lsort.append((lchain,vscore1,vscore2))

            if len(lres) >= MAXCHAIN:
                tdiff = uti.Ed_Timer("wordscore")
                if len(lsort) % (MAXCHAIN // 10) == 0:
                    Deb_Prtlog(LOGMSG["wordscprog"].format(
                                len(lsort) // (MAXCHAIN // 100),tdiff),logging.DEBUG)
        
        lsort1 = sorted(lsort,key=lambda x:x[1],reverse = True)
        lsort2 = sorted(lsort,key=lambda x:x[2],reverse = True)
        
        tdiff = uti.Ed_Timer("wordscore")
        Deb_Prtlog(LOGMSG["wordscok"].format(tdiff),logging.DEBUG)
        return (lsort1,lsort2)

    def Print_Scores(self,lscore,maxvals = MAXCMB):
        """Prints the most lucrative chains.
        
        Lscore is as output from scoring function - chain and 1+ score cols,
        though only the first is shown (call the function with each sort). 
        Includes the word itself, score, and then full chain details if needed."""
        if len(lscore) == 0:
            print("No combos available. Something went wrong.")
            return
        idx = 0
        indstop = False
        while not indstop:
            combo1 = lscore[idx]
            # Str is a bit of a hack.
            wrd1 = "".join([str(self.root[k].value[0]) for k in combo1[0]])
            print(wrd1,combo1[1],"|",combo1[0])
            idx = idx + 1
            if idx >= maxvals or idx >= len(lscore):
                indstop = True
                
    def Route_Text(self,lscore,maxvals = MAXCMB):
        """Creates list of top route strings from the map.
        
        Spam."""
        if len(lscore) == 0:
            print("No combos available. Something went wrong.")
            return []
        idx = 0
        indstop = False
        lroute = []
        while not indstop:
            combo1 = lscore[idx]
            # Str is a bit of a hack.
            wrd1 = "".join([str(self.root[k].value[0]) for k in combo1[0]])
            lroute.append(wrd1)
            idx = idx + 1
            if idx >= maxvals or idx >= len(lscore):
                indstop = True
        return lroute
    
    def Tile_Move(self,lchain):
        """Breaks tiles in chain and under curse tiles.
        
        Loops from the lower left corner to the lower right,
        with an inner loop that goes upwards per col and picks 'living' tiles only.
        The curse corruption effect is overridden if the chain is directly under,
        as such not completely separable to a func without additional notetaking."""
        # Step 1: Find the left corner by traversing ld from the root.
        # Highly presumptive of the graph structure, but that's the func's rules.
        # Recall that id[0] = col, id[1] = row.
        cnode = self.root[(0,0)] # No actual reference to 'first' nonnull node.
        indstop = False
        while not indstop:
            if (cnode.id[0] - 1,cnode.id[1]) in cnode.refs: # Go left.
                cnode = cnode.refs[(cnode.id[0] - 1,cnode.id[1])]
            elif (cnode.id[0],cnode.id[1] + 1) in cnode.refs: # Go down.
                cnode = cnode.refs[(cnode.id[0],cnode.id[1] + 1)]
            else:
                indstop = True
        
        # Step 2: Go up and copy vals not chained or cursed, leave out all the rest.
        # Loop this for adjacent cols / bottom nodes. 
        indstop = False
        while not indstop: # Loop through cols.
            cnode2 = cnode
            cnode3 = cnode2
            indstop2 = False
            indclear = False
            while not indstop2: # Loop up the col's rows (target tile).
                indstop3 = False
                while not indstop3: # Extra loop for source living tiles.
                    if indclear: # No more living tiles left, clear content.
                        indstop3 = True
                        nval = None # Or empty string?
                    else:
                        indlive = True
                        pidx = (cnode3.id[0],cnode3.id[1] - 1) 
                        if cnode3.id in lchain:
                            indlive = False
                        # Normal / gold tiles under curse are destroyed.
                        # Mind, ignoring chains under curse is implicit.
                        if (cnode3.value[1] != TILECURSE2):
                            if pidx in cnode3.refs:
                                if (cnode3.refs[pidx].value[1] == TILECURSE2):
                                    # Above exists and is cursed.
                                    indlive = False
                                    # All else - def alive.
                        
                        if indlive: # Found live tile, copy and continue.
                            indstop3 = True
                            nval = cnode3.value
                        if pidx in cnode3.refs:
                            cnode3 = cnode3.refs[pidx]
                        else: # Got all the way up, start handing out nulls.
                            # The loop will terminate next iter if cleared and dead.
                            # Otherwise, sends one last val and the rest cleared.
                            indclear = True
                    
                # Value obtained, copy it and continue upwards. 
                pidx = (cnode2.id[0],cnode2.id[1] - 1)
                cnode2.value = nval
                if pidx in cnode2.refs:
                    cnode2 = cnode2.refs[pidx]
                else: # All sources overwritten, may continue to next col. 
                    indstop2 = True
                
            if (cnode.id[0] + 1,cnode.id[1] + 1) in cnode.refs: # Hexgrid alternates in length.
                cnode = cnode.refs[cnode.id[0] + 1,cnode.id[1] + 1]
            elif (cnode.id[0] + 1,cnode.id[1] - 1) in cnode.refs:
                cnode = cnode.refs[cnode.id[0] + 1,cnode.id[1] - 1]
            else:
                indstop = True
        
        return self

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

def Graph_Input(iliner = None,inddig2 = True):
    """Graph input.
    
    Accepts either cmd like repeating input (until period or end keywords),
    or a single line of text (from gui).
    Each tile can contain up to one modifier (=/-) as a prefix (preferred) or suffix,
    and one alphanumeric char or digit; with the exception of 1X,
    if inddig2 is activated and it is separate from other tiles.
    By def, this ind is on for completeness, but it should be off for convenience
    in most boards which don't reach higher numbers.
    Currently tailored for the game: 6/7x9 grid and value modifiers.
    Prior input can be corrected using this format: *20 g,
    with the actions + to add, / to remove, * to change.
    Note - remove also grabs a placeholder parm.
    Terminate with fin, end, quit or period.
    Will automatically split sequential input to single char + prefixed modifier,
    save for the special case of single 2 char number (eg =10, 12).
    Creep: Make generic by passing the print function parms (dict)."""
    indstop = False
    prmchg = None
    tinp = []
    if iliner is None:
        print(LOGMSG["grpinpmsg"])
    while not indstop:
        if iliner is None:
            ursp = uti.Timed_Input(False,"",RSPTMO)
        else:
            ursp = iliner[:]
            indstop = True
        if len(re.findall(REINPEND,ursp.lower())) > 0: # Terminate after reading.
            indstop = True
            ursp = re.sub(REINPEND,"",ursp.lower())
        cinp = re.split(REDELIM,ursp)
        cedit = []
        for i,_ in enumerate(cinp):
            cinp1 = None
            if len(re.findall(RETILEPOS,cinp[i])) > 0:
                # Loop could prolly be done a bit more elegantly.
                if TILEADD in cinp[i]:
                    prmchg = [1]
                if TILEREM in cinp[i]:
                    prmchg = [2]
                if TILECHG in cinp[i]:
                    prmchg = [3]
                prmchg.append(int(re.sub(RETILEPOS,"",cinp[i])))
            elif len(re.findall(RETILEACT,cinp[i])) > 0:
                if TILEQM in cinp[i]: # Print current values.
                    print(LOGMSG["grpinpmsg"])
                    print(LOGMSG["grpprtmsg"])
                    Print_Hexagrid(tinp)
                elif TILECLR in cinp[i]: # Clear.
                    # Creep: Range clear, could use /20 30 format.
                    tinp.clear()
                    cedit.clear()
            elif prmchg is None: # Modifiers intentionally expect singular elems.
                # Fsr, findall gets confused by multiple groups,
                # so opted to be explicit with iter.
                #cedit.extend((c,0) for c in cinp[i])
                if (len(cinp[i]) <= 3
                and any(re.findall(RETILEDIG2,cinp[i],uti.REIS))
                and inddig2): # 10 - 19 with mod and no other tiles.
                    cinp1 = [cinp[i]]
                else: # Split to one char prefix tiles.
                    # Could prolly convert gold / curse to values with clever manipulation,
                    # but it'd be unreadable so I won't.
                    lrefs = re.finditer(RETILEPREF,cinp[i],uti.REIS)
                    cinp1 = []
                    for cref in lrefs:
                        tspn = (cref.span(0)[0],cref.span(0)[1])
                        tmptile = cinp[i][tspn[0]:tspn[1]]
                        cinp1.append(tmptile) 
            else: # The debugger is confused for no reason here.
                cinp1 = cinp[i]
            
            # Convert tiles and apply changer funcs.
            if cinp1 is not None:
                # Should be in legible format, list of strings.
                cinp2 = Val_Conv(cinp1,False) 
                if prmchg is not None: # Alter a prior tile.
                    if prmchg[0] == 1:
                        tinp.insert(prmchg[1],cinp2)
                    elif prmchg[0] == 2:
                        tinp.pop(prmchg[1])
                    elif prmchg[0] == 3:
                        tinp[prmchg[1]] = cinp2
                else:
                    if len(cinp2) == 0: # Empty.
                        pass
                    elif not uti.islstup(cinp2[0]): # Single tup gets broken.
                        cedit.append(cinp2)
                    else:
                        cedit.extend(cinp2) 
        tinp.extend(cedit)
            
    return tinp

def Val_Conv(val,tostr = True):
    """Converts a value or list to str or tup. 
    
    Save for variable format string - send those to ginp.
    Used in gui / backend integration.
    Assumed format of single values: string, tuple(2), list(tuple(2)).
    L2 can be a small to large board, L1 of 2+ elems is unhexed.
    
    Bug: As of V2.4/5, it has been tested for all cases;
    its only error is *list of 2 strs + tostr* with any number of wrappers,
    which val1 must interpret as a tup and thus fuse to one tile.
    There are currently no such use cases,
    as raw input always goes through graphinp before valconv -> str."""
    lcnv = None
    ltype = None
    if not uti.islstup(val): # String.
        ltype = 0
    elif len(val) == 0:
        lcnv = []
    elif len(val) > 2: # Big L1 of strings / L2.
        ltype = 1
    elif not uti.islstup(val[0]): # Tuple(2 or str).
        ltype = 0
    elif len(val[0]) > 2: # Small L2 of strings.
        ltype = 1
    elif not uti.islstup(val[0][0]): # list(tup(2) or two), or L2(str)
        ltype = 1
    else: # Small L2 of converted vals.
        ltype = 1
    if ltype == 1:
        # Alt: A better specific test might be existence of ints.
        if len(Flatten1(val)[0]) > 2: # Full grid size of strings.
            lcnv = [Val_Conv1(v,tostr) for v in Flatten(val)]
        else: # Flattened to tups.
            lcnv = [Val_Conv1(v,tostr) for v in Flatten1(val)]
    elif ltype == 0:
        lcnv = Val_Conv1(val,tostr)
        
    return lcnv

def Val_Conv1(val,tostr = True):
    """Guaranteed single val conversion.
    
    Spam.""" 
    if uti.islstup(val) and tostr: # To gui.
        indconv = True
        if len(val) != 2:
            indconv = False # List(str), just throw away the wrapper.
            val = val[0]
        if indconv:
            vcnv = str(val[0])
            if val[1] == TILECURSE2:
                vcnv = TILECURSE + str(vcnv)
            elif val[1] == TILEGOLD2:
                vcnv = TILEGOLD + str(vcnv)
        else:
            vcnv = val
    elif not tostr: # To backend list.
        indconv = True
        if uti.islstup(val):
            if len(val) == 2:
                indconv = False # Tuple(2)
            else: # Otherwise likely list(str), which is confusing.
                val = val[0]
        if indconv:
            if TILECURSE in val:
                vtile = TILECURSE2
            elif TILEGOLD in val:
                vtile = TILEGOLD2
            else:
                vtile = TILENORM2
            ctile = re.sub(RETILEVAL,"",val)
            vcnv = (ctile,vtile)
        else:
            vcnv = val
    else:
        vcnv = val
    
    return vcnv

def Colour_Decision(val,indmark = 0):
    """Colours gold, cursed and marked combo tiles.
    
    Returns a list of colour tups rgba.
    Joint effort with gui.
    The serial combo colour gradient is made of interwoven colours for clarity.
    This is not perfect (min 4 colours in a 2d map), but may suffice with alpha."""
    if indmark == 1:
        if len(val) == 1: # Unrealistic edge case.
            lclr = [(uti.List_Format(DCOLOUR["combo"][1],LSTPH,MAXCLR,MAXCLR))]
        else:
            # Selection goes from light blue to STRONG teal. Seems visible.
            vfactor = (MAXCLR2 - MINCLR) / (len(val) - 1)
            vclr = [(MAXCLR,0,MAXCLR),(0,MAXCLR,MAXCLR)]
            lclr = [(uti.List_Format(DCOLOUR["combo"][1],LSTPH,
                                     *vclr[i % 2],20 + i * vfactor))
                    for i,_ in enumerate(val)]
    elif indmark == 2: # Step detection. Gui keeps track in this case.
        lclr = [DCOLOUR["step"][1]]
    elif indmark == 3:
        lclr = [DCOLOUR["parti"][1]]
    else:
        lcnv = Val_Conv(val,False)
        if len(lcnv) == 0:
            pass # New board.
        elif not uti.islstup(lcnv[0]):
            lcnv = [lcnv] # Colour a single tile.
        lclr = []
        for v in lcnv:
            if v[0] == "" or v[0] is None: # Empty tiles.
                lclr.append(DCOLOUR["error"][1])
            else:
                for k in DCOLOUR.keys():
                    if DCOLOUR[k][0] == v[1]:
                        lclr.append(DCOLOUR[k][1])
    return lclr

def Flatten(ldeep):
    """Flattens a list (multilayer, distinguishing is difficult).
    
    This method is ordered, at the cost of repeated push / pop;
    encountering an inner list, will open that fully first.
    Many of these iters can be optimised with a loop."""
    #return [v for l1 in l2 for v in l1]
    lflat = []
    q1 = deque()
    q1.append((ldeep,0))
    while q1:
        (lcur,cidx) = q1.pop()
        if cidx < len(lcur):
            q1.append((lcur,cidx + 1))
            vent = lcur[cidx]
            if uti.islstup(vent): # Another list, push for reopening.
                q1.append((vent,0))
            else:
                lflat.append(vent)
    
    return lflat

def Flatten1(ldeep):
    """Flattens up to one layer depth (eg list of tups).
    
    Rather simple function - if current has no list ents,
    leave it alone."""
    lflat = []
    q1 = deque()
    q1.append((ldeep,0))
    while q1:
        (lcur,cidx) = q1.pop()
        indskip = False
        if cidx == 0:
            lchk = [v for v in lcur if uti.islstup(v)]
            if len(lchk) == 0:
                lflat.append(lcur)
                indskip = True
        if cidx < len(lcur) and not indskip:
            q1.append((lcur,cidx + 1))
            vent = lcur[cidx]
            if uti.islstup(vent): # Another list, push for reopening.
                q1.append((vent,0))
            else:
                lflat.append(vent)
    
    return lflat

def Hexify(lval,rcnt = 6,indconvex = False):
    """Converts L1 to L2 of hex shape.
    
    Row count refers to first col, which is +1 if convex."""
    if indconvex:
        conbase = 0
    else:
        conbase = 1
    conmod = (conbase * 2 - 1)
    
    colmod = 0
    vret = []
    l2 = []
    for i,_ in enumerate(lval):
        l2.append(lval[i])
        if len(l2) >= rcnt + conmod * colmod:
            # Filled a col, switch to odd / even and append it to L2.
            colmod = 1 - colmod
            vret.append(l2)
            l2 = []
    if len(l2) > 0:
        vret.append(l2)
        l2 = []
    
    return vret

def Print_Hexagrid(lval,rcnt = 6,ccnt = 9,indconvex = False):
    """Print a 2 value list on a full hexagrid of some length.
    
    The colcount is normal, row count for leftmost col.
    If convex will put odd cols on odd rows (eg 0.0),
    and the row counter varies (+1 for concave yet mod shifted back). 
    Visually fitted currently in a checkered pattern.
    If the list is partially filled, prints column-row wise from top left.
    Sample grid index calcs are in a test sheet for clarification."""
    if indconvex:
        conbase = 0
    else:
        conbase = 1
    conmod = (conbase * 2 - 1)
    maxrow = (rcnt + conbase) * 2 - 1 # Adds spaces in between.
    for ridx in range(maxrow):
        lrow = []
        for cidx in range(ccnt):
            if (ridx + conbase) % 2 == cidx % 2:
                # Col lengths alternate, so need a separate count.
                tidx = int(cidx * (rcnt - 1 + conbase) +
                           (cidx - cidx % 2 * conmod) / 2)
                if (ridx // 2 + tidx < len(lval) 
                and (indconvex or cidx % 2 != 0 or ridx < maxrow - 1)):
                    # Join the keys. All keys used must be strings.
                    lrow.append(",".join((str(c) for c in 
                                          lval[ridx // 2 + tidx])))
                else:
                    lrow.append("   ")
            else:
                lrow.append(" | ")
        print("".join(lrow))

def Print_Format(lval):
    """Prints L2 in an easy to edit mode.
    
    Spam."""
    for l1 in lval:
        for l2 in l1:
            print(l2[0],uti.Multirep(str(l2[1]),TILEVAL2[1],
                                     TILEVAL2[0]),sep="",end = " ")
        print()

# BM! MAIN()
def Main_Test():
    """Short activation.
    
    Spam."""
    global galena
    global mgui
    Deb_Prtlog("Start main TEST",logging.DEBUG)
    uti.St_Timer("Main")
    
#     dbrefs = Init_Parms()
#     (cmpdb,infdb,dbini) = dbrefs
    indstop = False
    verr = 0
    btc = 1000 # dbini["Main"][INIBTC]
#     ddl = ldb.Date_Conv(dbini["Main"][INIDDL])
#    from Rawdt_LDL import lwin
#    lfail = [("Crystal_Babyface-2000-11-27.jpg","19-Sep-2001 19:44 ","7.9K"),
#             ("Crystal_Babyface.jpg","19-Sep-2001 19:44 ","7.9K"),
#             ("abreik_meerca-.jpg","01-Apr-2018 22:43 ","65K")]
#    tstdl = "http://upload.neopets.com/beauty/images/winners/silkmon-2012-05-11.jpg"
    while not indstop:
        if 1 != 0:
            # Trie.
#             tstrie = BNtrie()
#             tstrie.build_dict(np.array(("ziggy","wino")))
            # Convert_Dict()
#             (tri1,tri2) = Load_Dict()
#             print(list(tri1.refs["a"].refs["a"].refs["h"].refs["s"].refs.keys()))
#             print(tri1.search("aardvark"))
            
            # Graph.
            groot = BNgraph(None)
#             groot.build_hex([[10,20,30],[11,21,31,41],[12,22,32]])
#             gi = Graph_Input()
#             smpl = """k,u,l,i,n,o,
#                       t,l,s,o,j,o,u,
#                       a,r,a,a,a,n,
#                       n,d,u,a,s,o,z,
#                       i,a,i,g,a,a,
#                       d,i,a,l,t,f,s,
#                       t,t,o,a,y,l,
#                       u,n,a,i,a,r,i,
#                       n,q,n,l,t,v"""
#             gi = [(v,0) for v in gi if len(v) > 0]
#             gi = Graph_Input(smpl)
            # Form activation.
            mgui.Start_Form()
            smpl = """2,3,5,5-,5,5,
                      3,1,2,3,3,2,4,
                      4,2,1,4-,1,3,
                      3,4,2,5,5,3,3,
                      3,5,2-,2,4,2,
                      3,2,2,2,1,1,5,
                      5,2,3,1,5-,4,
                      3,4,1,1,1,4,3,
                      4,4,5,5,4,1"""
            gi = Graph_Input(smpl)
#             gi = re.split(REDELIM,smpl)
#             gi = [(int(v),0) for v in gi if len(v) > 0]
            gi[10] = gi[10][0],1
            gi[20] = gi[20][0],2
            gi[30] = gi[30][0],1
            gi[40] = gi[40][0],2
            Print_Hexagrid(gi)
            gi = Hexify(gi)
            groot.build_hex(gi)
#             Print_Hexagrid([["a",1],["b",0],["c",2],["d",0]] * 30)
            
            # Pathing.
            #potword = groot.trieverse(tri1,tri2)
            potword = groot.numverse()
            (optim,dang) = groot.Word_Score(potword)
            print("Topmost score:")
            groot.Print_Scores(optim)
            print("Topmost danger:")
            groot.Print_Scores(dang)
            
            # Clearing mechanism.
            groot.Tile_Move([(0,3),(0,4),(1,3)])
#             Print_Format(groot) # Don't have one for graphs.
            
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
    global mgui
    Deb_Prtlog("Start main",logging.DEBUG)
    uti.St_Timer("Main")
    
    verr = 0
#     dbrefs = Init_Parms()
    if FMAIN == 1:
        Convert_Dict()
    if FMAIN == 2:
        (tri1,tri2) = Load_Dict()
        while True:
            groot = BNgraph(None)
            gi = Graph_Input()
            gi = Hexify(gi)
            groot.build_hex(gi)
            potword = groot.trieverse(tri1,tri2)
            (optim,dang) = groot.Word_Score(potword)
            print("Topmost score:")
            groot.Print_Scores(optim)
            print("Topmost danger:")
            groot.Print_Scores(dang)
            print("---------------------")
            Print_Format(gi)
            
        verr = 0
    elif FMAIN == 8:
#         verr = Mine_List(dbrefs)
        verr = 0
    elif FMAIN == 11:
#         verr = Review_Dbs(dbrefs,QUERYLIST)
        # (tri1,tri2) = Load_Dict() # Not always needed, form will summon it once as needed.
        mgui.Start_Form()
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
    
