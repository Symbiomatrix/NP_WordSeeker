# -*- coding: utf-8 -*-
#!! -*- coding: cp1255 -*-
"""
Created on 16/12/17

@author: Symbiomatrix

@purpose: General utilities. 

Version log (incrementing on imports):
30/04/19 V8.2 Added ellipsis replacement.
24/03/19 V8.1 Added hash str and digits (any basic object).
23/03/19 V8.0 Forked to repstest. Added viewdict methods.
09/10/18 V7.9 Added suffix strip.
23/09/18 V7.8 Added heb reverse (CC).
07/09/18 V7.7 Added open folder + sel file.
27/08/18 V7.6 Added methocodes standard. Some verr value conflicts (1, 3, 9, copyfl),
                but that matters little since the key is textual.
26/08/18 V7.5 Added open file in program, with timeout capabilities.
                Upgraded file open def to utilise timeout mechanism.
20/08/18 V7.4 Corrected dict compare - matched is also a dict for completeness.
17/08/18 V7.3 Added logger parm to debprt, so it can be inherited using lambda. 
16/08/18 V7.2 Corrected dict compare - unique d1 / d2 return full dict rather than set.
12/08/18 V7.1 Forked from linkdl.
15/05/18 V7.0 Added file / folder generator. (shutil)
                Added batch copy / move / del.
                Added msgbox. (ctypes)
                Added logmsg, deb print methods (for new stuff).
11/05/18 V6.3 Fixed large bugs in floop: repeated when exceeding str boundary (0 / len),
                and backfind skips adjacent letters (-1 in ed slice)
10/05/18 V6.2 Added deep list formatter.
09/05/18 V6.1 Added multireplace function.
06/05/18 V6.0 Fork for link dl.
                Fixed empty lists packed as L rather than L [ ].
02/03/18 V5.0 New project - archive hqa.
                Added fstr skipping parm to find loop (when discarding the key text).
                Added dict comparison tool.
                Added none default to floop.
04/02/18 V4.1 Added str handling for file exists (relative directory).
                Added isstr function.
03/02/18 V4.0 Added csv writing + imp.
                Notwithstanding manual claiming no support for utf without external lib,
                it seems to work with codecs.
16/01/18 V3.4 Added sign.
12/01/18 V3.3 Added multikey get / set functionality to ini using temp class. 
11/01/18 V3.2 Added directory creation (lite cannot).
25/12/17 V3.1 Expanded ini to convert complex lists (of strings, no class return). Added deque.
24/12/17 V3.0 Added str left/right, ini class.
20/12/17 V2.1 Added int sequence.
16/12/17 V2.0 Continued from pa.
13/12/17 V2.0 Added threading + limited time input (cancel). It is buggy.
19/11/17 V1.1 Fixed erroneous main checker (all uses).
06/11/17 V1.0 New.

"""

import sys
import logging
logger = logging.getLogger(__name__) # Separated logger, does not spam main.
if __name__ == '__main__':
#    logging.basicConfig(stream=sys.stderr,
#                    level=logging.ERROR, # Prints to the console.
#                    format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    logger.setLevel(logging.DEBUG)
#    logging.basicConfig(filename="errlog.log",
#                        level=logging.DEBUG, # Prints to a file. Should be utf. #.warn
#                        format="%(asctime)s %(levelname)s:%(name)s:%(message)s") # Adds timestamp.
SYSENC = "cp1255" # System default encoding for safe logging.
FRMTMLOG = "%y%m%d-%H%M%S" # Time format for logging.
PRTLIM = 1000 # When printing too long a message, will invoke automatic clear screen.
BADLOG = "Utilog-d{}.txt"

logger.debug("Start util module")

import datetime
import subprocess, os
import webbrowser
from pathlib import Path # v
import codecs
import csv
import re
import threading
import queue
import configparser
from collections import deque # v
import shutil
import ctypes
import hashlib
import json

NLN = "\n"
REGANY = r"""(.*)""" # Any characters.
REIS = re.I + re.S
INTREM = "," # Characters skipped in number sequence.
INIEXT = "{}.ini"
ININULL = "NULL" # A string which replaces a none value and vice versa. It can be garbled.
INILIST = "L" # Identifies a list, as well as squaries and quotes.
INISTRC = "\"[]" # Structure chars of cilist.
INICDEF = "DEFAULT" # Default category.
QUOMRK = "\""
BCKSLS = "\\" # Equivalent to raw tagged single, but that messes up eclipse syntax.
REGILST = r"""[{}\\]([\"\[\]])""" # Any (non-)escaped structure chars. Group doesn't care which.
LSTPH = ":placeholder" # No easy format alt for lists. This ought to disrupt a query.
OPFLD = """explorer /select,\"{}\""""
HEB1 = 'א'
HEB2 = 'ת'
LETENG = set(chr(i) for i in range(ord("a"),ord("z") + 1)) # Alt: From string.ascii_lowercase.
LETENGU = set(chr(i) for i in range(ord("A"),ord("Z") + 1))
LETENG.update(LETENGU)
LETDIG = set(chr(i) for i in range(ord("0"),ord("9") + 1))
LETHEB = [chr(i) for i in range(ord(HEB1),ord(HEB2) + 1)]
LETSEPH = "!#$%*+,-.:;<=>?@^_`|~"
LETSEPHI = """ "&'()/[\]{}"""
HASHDEF = 8
CNTASC = 256
# Valid hash sets:
# 0 = Ascii, 1 = A-Z + digs (conservative),
# 2 = a-Z + digs + safe punctuation (by my standard),
# 3 = printable (32 - 127, excludes extended and spacing).
HASHCHR = {
0: "NULL",
1: sorted(list(LETENGU.union(LETDIG))),
2: sorted(list(LETENG.union(LETDIG).union(LETSEPH))),
3: sorted(list(LETENG.union(LETDIG).union(LETSEPH).union(LETSEPHI))),
9: "9"
}
MBRSP = { # Message box responses.
1: "OK",
2: "Cancel",
3: "Abort",
4: "Retry",
5: "Ignore",
6: "Yes",
7: "No",
10: "Try again",
11: "Continue",
99: "Null"
}
RMBRSP = {v: k for (k,v) in MBRSP.items()}
LOGMSG = {
"loger": "Unknown error in log encoding.\n {} {}",
"copnofilewr": "File {} not found in source {} or target dir does not exist, ignored.",
"copunker": "Fs operation {} failed at file {} - unknown.\n Reason: {} {}",
"opfer": "Error during opening of file {} using {}.\n Reason: {} {}",
"opfwr": "No such program {} (during open file).",
"opder": "Error during opening of directory {}.\n Reason: {} {}",
"null": "This is the end my friend."
}
METHCODES = dict()
# Same codeword keys override old val tups, others added as new.
METHCODES.update({
"ok": (0,""),
"wfilext": (1,"File exists, will not overwrite."),
"cpartskip": (1,"Skipped some files."),
"wfildir": (2, "Directory, not a file."),
"wfilnext": (3,"File does not exist."),
"cpusrcan": (3,"User cancelled operation."),
"wunkerr": (9,"Unknown error."),
"wfiluse": (13,"File is in use.")
})
REVMETHCD = {v[0]: (k,v[1]) for (k,v) in METHCODES.items()}

tmdict = dict()
qtrd = queue.Queue()
trd = []
# BUG: Must use global queue, local causes weird ship, 
# leaves input hanging forever and when written does nothing.
# Input still doesn't die (needs horrible thread's interrupt_main), but only one extra at a time.

FDEFS = {
"Fig":{"ppr":1,"ppc":1,"figsize":(13,3),
        "supttl":"Figure {fign}","supx":0.5,"supy":1.03,"supfont":14}, # y = 0.98 overlaps.
"Axis":{"pptitle":"Graph","ppxlabel":"X axis","ppylabel":"Y axis","ppindleg":False,
        "ppindalbl":True,"ppindgrid":True,"ppindmgrid":True},
"Plot":{"label":"Function {fn}",
        "ppfign":1,"ppaxr":0,"ppaxc":0,"holdon":True},
"Imgs":{"ppindleg":True, # Legend merged for ease of access.
        "ppfign":1,"ppaxr":0,"ppaxc":0,"holdon":False,
        "ppindalbl":False,"ppindgrid":True,"ppindmgrid":False,"ppxlabel":"","ppylabel":""},
"Fgrid":{"ppfign":1,"ppr":-1,"ppc":-1, # Will override rc if dict set.
         "ppindleg":False,"cmap":"gray", # Cbars unreadable in medium grid. Greyscale preferable.
         "ppindalbl":False,"ppindgrid":False,"ppindmgrid":False, # Save more space on grid tags.
         "adjh":0.05,"adjw":0.05,"adjl":0.05,"adjr":0.95,"figsize":None, # Tighter layout.
         "vmin":None,"vmax":None,"ppindlocol":1, # Local / global / rc brightness.
         "heatrmin":None,"heatrmax":None,"heatcmin":None,"heatcmax":None},
"Null":None
}
# View dictionary. Sends parms relevant to function, through the percolation.
# PP parms do not need this since no atterr is thrown for these.
# Note that the keys differ from defs, which refer to the pp function.
DVIEW = {
"Fig":{"figsize"},
"Figb":{"ppr","ppc","figspec"}, # Backup only (used outside fig cre).
"Axis":{"fcnt","pptitle","ppxlabel""ppylabel","ppindleg"},
"Plot":{"label","lw"},
"Imgs":{"cmap","vmin","vmax"},
"Null":set()
}
DVIEW2 = { # Conversion dicts. Can work for all keys, but unnecessary dupe.
"Supt":{"supttl":"t","supx":"x","supy":"y","supfont":"fontsize"},
"Gspec":{"ppr":"nrows","ppc":"ncols",
         "gshgts":"height_ratios","gswids":"width_ratios"}, # Does not accept dict, but can be coerced.
"Tgtlay":{"tgtpad":"pad"}, # h, wpad. Does nothing - use adjust.
"Adjsub":{"adjl":"left","adjr":"right","adjb":"bottom","adjt":"top", # 0 - 1, edge margin.
          "adjh":"hspace","adjw":"wspace"}, # 0 - 1 (0.2), inner distance.
"Null":dict()
}

def Default_Dict(catg,d):
    """Fills copy of dictionary with given values and defaults where missing.
    
    Spam."""
    rund = d.copy()
    for k in FDEFS[catg]:
        rund[k] = d.get(k,FDEFS[catg][k])
    
    return rund

def View_Dict(catg,d,indcnv = True):
    """Extracts necessary keys from dict.
    
    Also converts some keys which otherwise overlap in naming.
    For fussy functions."""
    d2 = {k:v for k,v in d.items() if k in DVIEW.get(catg,{})}
    if indcnv: # Function usage.
        d2.update({DVIEW2[catg][k]:v for k,v in d.items() if k in DVIEW2.get(catg,{})})
    else: # Deferred backup.
        d2.update({k:v for k,v in d.items() if k in DVIEW2.get(catg,{})})
    return d2

def Parm_Consolidate(k,v = None,d = None,vdef = None):
    """Takes values from tup - dict - default.
    
    Kind of a bother to setup, so limited to high usage parms.
    Vdef is slightly redundant, can go directly to dict."""
    nv = d.get(k,None)
    if v is not None:
        nv = v
    if nv is None:
        nv = vdef
    return nv

def Deb_Prtlog(vmsg,vlvl = logging.ERROR,deblgr = logger):
    """Prints and logs message.
    
    Uses logging levels.
    Prints to utf file in case of failure."""
    try:
        smsg = str(vmsg)
    except Exception as err:
        deblgr.error(LOGMSG["loger"].format(err.__class__.__name__,err.args))
        smsg = vmsg # Try to print as is.
    try:
        smsg.encode(SYSENC)
    except UnicodeEncodeError: # Not safe to print or log.
        now = datetime.datetime.now()
        flnm = BADLOG.format(now.strftime(FRMTMLOG))
        print("Unicorn message intercepted, see logfile {}.".format(flnm))
        Write_UTF(flnm,smsg,True)
        return
    except Exception as err:
        deblgr.error(LOGMSG["loger"].format(err.__class__.__name__,err.args))
    
    if len(smsg) <= PRTLIM:
        print(smsg)
    else:
        print("Long message intercepted, check the log.")
    if vlvl == logging.DEBUG:
        deblgr.debug(smsg)
    elif vlvl == logging.INFO:
        deblgr.info(smsg)
    elif vlvl == logging.WARN:
        deblgr.warn(smsg)
    elif vlvl == logging.ERROR:
        deblgr.error(smsg)
    elif vlvl == logging.CRITICAL:
        deblgr.critical(smsg)
    else:
        deblgr.debug(smsg)

# System file handling.
def Msgbox(mtxt = "",mttl = "Message",mtype = 0):
    """Display a message box.
    
    Styles:
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | No 
    6 : Cancel | Try Again | Continue
    
    Responses:
    OK = 1, cancel = 2, abort = 3, retry = 4, ignore = 5, yes = 6, no = 7,
    try again = 10, continue =  11
    """
    ursp = ctypes.windll.user32.MessageBoxW(0,mtxt,mttl,mtype)
    return ursp

def File_Exists(flprm):
    """Checks whether string exists as file or directory.
    
    0 = no, 1 = yes, 2 = directory.
    Expects path, if str will treat as relative directory."""
    if isstr(flprm):
        flpt = Path(flprm)
    else:
        flpt = flprm
    if flpt.is_file():
        #print("File %s exists, will not overwrite." % flpt)
        return METHCODES["wfilext"]
    else:
        if flpt.is_dir(): # Unexpected.
            #print("%s is a directory, not file" % flpt)
            return METHCODES["wfildir"]
        else:
            return METHCODES["ok"]
        
def Find_Loop(instr,fstr,repcnt,fdir = False,fst = 0,fed = -1,keyskip = False):
    """Find nth instance in probed string.
    
    If any fail, immediately returns.
    Default direction is forward, in back mode seeks rightmost starting from end.
    Kepskip returns (after) right end of fstr when found."""
    if fst is None: # Permit standard empty values.
        fst = 0
    if fed is None:
        fed = -1
    if fed < 0:
        fed = len(instr) # Or call without parm.
        
    if not fdir:
        curind = fst - 1
        for _ in range(repcnt):
            curind = instr.find(fstr,curind + 1,fed)
            logger.debug("Found {} {}".format("",curind)) # fstr[0:7] # Cannot print utf to log file.
            if curind < 0:
                return curind # String not found.
    else:
        curind = fed + 1
        for _ in range(repcnt):
            curind = instr.rfind(fstr,fst,curind)
            logger.debug("Found {} {}".format("",curind))
            if curind < 0:
                return curind
    
    if keyskip:
        curind = curind + len(fstr)
    return curind

def Open_File_Def(flpt,timeout = -1):
    """Open file using system default app.
    
    Win is prolly nt.
    Does not use os.system("open/start ...") which is buggy.
    Works for browser tabbing too, in FF default."""
    (err,_) = File_Exists(flpt) # Can catch the filenotfounderror on startfile.
    if err != 1:
        return METHCODES["wfilnext"]
    if sys.platform.startswith('darwin'):
        subprocess.call(('open',flpt)) # Prolly waits indefinitely, but dunno prog open syntax.
    elif os.name == 'nt':
        # os.startfile(flpt) # Does not receive err code.
        (verr,_) = Open_Progfile(flpt,timeout = timeout)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', flpt)) # Also waits.
    return METHCODES["ok"]

def Open_Webfile(flpt,tabber):
    """Open file using default browser.
    
    For tabber, 0 = same window (replace?), 1 = new and 2 = tabbed. Setting does naught in practice.
    Though browser needs file - full path,
    both file name and path types are supported by os - this is reprimanded in documentation.
    Webr has the rather dreadful errhandle of silently opening iexplorer
     search engine on eg file doesn't exist, so this function takes it."""
    #flpt = "file://" + os.path.abspath(flnm).replace("\\","/") # No need in win.
    (err,_) = File_Exists(flpt)
    if err != 1:
        return METHCODES["wfilnext"]
    webbrowser.open(flpt,tabber) # Likely 1 is new window.
    return METHCODES["ok"]

def Open_Progfile(flpt,prgpt = None,timeout = -1):
    """Opens file using the specified program.
    
    Program must be the exe file's full path (in program files).
    Opening a directory may or may not fail, but it's not intended.
    Timeout = -1 will leave file open, timeout >= 0 will open the file for to seconds,
    timeout = none will wait until file closes."""
    # Alt: Os command works, needs quotes for spaces in directory.
    # os.system("""start "" "{}" "{}" """.format(prgpt,flpt))
    fargs = [flpt]
    shell = False
    if prgpt is not None:
        fargs.insert(0,prgpt)
    else:
        shell = True # Bad idea, but not alt found for opening as default. File is validated at any rate.
    (err,_) = File_Exists(flpt)
    if err != 1:
        return METHCODES["wfilnext"]
#     (err,_) = File_Exists(prgpt) # Not checked here, eg notepad.exe can be called directly.
#     if err != 1:
#         return METHCODES["wfilnext"]
    verr = 0
    try:
#         subprocess.call([prgpt,flpt],timeout = 0)
        if timeout < 0:
            # Not setting an out value seems to work, mayhap garbage collected.
            # Forum method indicates setting parms stdin, stdout, stderr to null in the call.
            subprocess.Popen(fargs,shell = shell)
        else: # Basically call code without error.
            with subprocess.Popen(fargs,shell = shell) as p:
                try:
                    verr = p.wait(timeout = timeout)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait() # Dunno what this does.
                    # raise # It's okay. Might set verr.
    except FileNotFoundError:
        Deb_Prtlog(LOGMSG["opfwr"].format(prgpt),logging.WARN)
        return METHCODES["wfilnext"] # Fallbacks.
    except Exception as err: # Important to catch all, otherwise might hang.
        Deb_Prtlog(LOGMSG["opfer"].format(flpt,prgpt,
                               err.__class__.__name__,err.args))
        return METHCODES["wunkerr"]
    
    return (verr,REVMETHCD[verr][1])

def Open_FolderSl(flpt,timeout = -1):
    """Open a folder and select a specific file.
    
    Dunno how to prevent opening additional explorers on repeat.
    Standard timeout rules."""
    fargs = OPFLD.format(flpt)
    shell = False
    (err,_) = File_Exists(flpt)
    if err != 1:
        return METHCODES["wfilnext"]
#     (err,_) = File_Exists(prgpt) # Not checked here, eg notepad.exe can be called directly.
#     if err != 1:
#         return METHCODES["wfilnext"]
    verr = 0
    try:
#         subprocess.call([prgpt,flpt],timeout = 0)
        if timeout < 0:
            # Not setting an out value seems to work, mayhap garbage collected.
            # Forum method indicates setting parms stdin, stdout, stderr to null in the call.
            subprocess.Popen(fargs,shell = shell)
        else: # Basically call code without error.
            with subprocess.Popen(fargs,shell = shell) as p:
                try:
                    verr = p.wait(timeout = timeout)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait() # Dunno what this does.
                    # raise # It's okay. Might set verr.
    except Exception as err: # Important to catch all, otherwise might hang.
        Deb_Prtlog(LOGMSG["opder"].format(flpt,
                               err.__class__.__name__,err.args))
        return METHCODES["wunkerr"]
    
    return (verr,REVMETHCD[verr][1])

def Write_UTF(flnm,wrdata,autoverwr = False):
    """Writes multiline data to utf8 file.
    
    Optional file overwrite check."""
    logger.debug("Start write utf")
    flpt = Path(flnm)
    (err,errmsg) = File_Exists(flpt)
    if err > 0 and not autoverwr:
        return (err,errmsg)

    #with open(flnm,"w") as flw: # Not utf encoded.
    with codecs.open(flnm, "w", "utf-8-sig") as flw:
        for ln in wrdata:
            flw.write(ln)
    
    return METHCODES["ok"]

def Write_CSV_UTF(flnm,wrdata,autoverwr = 1,dlm = ";",quoch = QUOMRK):
    """Writes multiline data to utf8 csv file.
    
    Overwrite modes: 0 = return with error, 1 = overwrite, 2 = append."""
    logger.debug("Start write utf")
    flpt = Path(flnm)
    (err,errmsg) = File_Exists(flpt)
    if err > 0 and autoverwr == 0:
        return (err,errmsg)
    elif autoverwr == 1:
        try:
            codecs.open(flnm, "w","utf-8-sig").close() # Clears file.
        except PermissionError: # File is open.
            logger.error("File {} is in use.".format(flnm))
            return METHCODES["wfiluse"]
    
    try:
        with codecs.open(flnm, "a", "utf-8-sig") as flw:
            csvwr = csv.writer(flw, delimiter=dlm,
                               quotechar=quoch,quoting=csv.QUOTE_MINIMAL)
            for ln in wrdata:
                csvwr.writerow(ln)
    except PermissionError:
        logger.error("File {} is in use.".format(flnm))
        return METHCODES["wfiluse"]
    
    return METHCODES["ok"]

def Read_CSV_UTF(flnm,dlm = ";",quoch = QUOMRK,Apply_Func = None):
    """Reads multiline data from utf8 csv file, either to activate function or list.
    
    Spam"""
    logger.debug("Start read utf")
    lret = []
    flpt = Path(flnm)
    (err,_) = File_Exists(flpt)
    if err == 0:
        return (lret,*METHCODES["wfilnext"])
    
    with codecs.open(flnm, "r", "utf-8-sig") as flr:
        csvrd = csv.reader(flr, delimiter=dlm,quotechar=quoch)
        for ln in csvrd:
            if Apply_Func is None:
                lret.append(ln)
            else:
                Apply_Func(ln)
    
    return (lret,*METHCODES["ok"])

def Create_Directory(cdir):
    """Creates directory if it doesn't exist.
    
    Lite module lacks this functionality."""
    if not os.path.exists(cdir):
        os.makedirs(cdir)
        return True
    else:
        return False

def Gen_Filesystem(srcfld,indtype = 0):
    """Generator for all files / folders in directory.
    
    0 = 1 = files, 2 = folders, 3 = both.
    Simple gathering: list(gen)."""
    if srcfld == "":
        srcfld = os.getcwd()
    if indtype == 0:
        indtype = 1
    srcfiles = os.listdir(srcfld)
    for objnm in srcfiles:
        objpt = os.path.join(srcfld,objnm)
        if (indtype in (1,3)
        and os.path.isfile(objpt)):
            yield objnm
        if (indtype in (2,3)
        and not os.path.isfile(objpt)):
            yield objnm

def Del_Filedir(delpath):
    """Removes file using os rem or whole dir using shutil rmtree.
    
    Spam."""
    verr = 0
    if os.path.isfile(delpath):
        os.remove(delpath)
    else:
        shutil.rmtree(delpath)
    return verr

def Copy_Files(lfls,srcfld,trgfld,indcopy = 1,indconf = None):
    """Copies files in list from source to target.
    
    Nothing = 0, copy = 1, move = 2, delete = 3.
    If confirmation is set, will be required for every operation
     (selecting no will skip one file / folder), cancel for the whole operation.
    Caller must invoke fso generator, cba to pipe it.
    0 = ok, 1 = user skipped some, 3 = user cancelled, 9 = unknown error halt."""
    verr = 0
    if indconf is None:
        if indcopy == 3:
            indconf = True
        else:
            indconf = False
    if srcfld == "":
        srcfld = os.getcwd()
    if trgfld == "":
        trgfld = os.getcwd()
    if indcopy == 0: # Do nothing.
        indconf = False
        fsfun = lambda x: x # Cannot use pass
        msgconf = lambda x: "I didn\'t do nothin\' {}.".format(x)
    elif indcopy == 1:
        fsfun = lambda x: shutil.copy2(os.path.join(srcfld,x),
                                       os.path.join(trgfld,x))
        msgconf = lambda x: "Continue copy of {} from {} to {}?".format(x,srcfld,trgfld)
    elif indcopy == 2:
        fsfun = lambda x:shutil.move(os.path.join(srcfld,x),
                                     os.path.join(trgfld,x))
        msgconf = lambda x: "Continue move of {} from {} to {}?".format(x,srcfld,trgfld)
    elif indcopy == 3:
        # Much more dangerous than os.remove - deletes subdirs.
        fsfun = lambda x: Del_Filedir(os.path.join(srcfld,x))
        msgconf = lambda x: "Continue *delete* of {} and its contents from {}???".format(x,srcfld)
    for fl in lfls:
        indskip = False
        if indconf:
            ursp = Msgbox(msgconf(fl),"Warning",3)
            if ursp == RMBRSP["No"]:
                logger.info("User skipped fs operation {} of file {}.".format(indcopy,fl))
                indskip = True
                # Can save which files, but pointless (see log, rerun list).
                verr = METHCODES["cpartskip"][0]
            elif ursp == RMBRSP["Cancel"]: # Halt procedure.
                logger.warn("User cancelled fs operation {} at file {}.".format(indcopy,fl))
                verr = METHCODES["cpusrcan"]
                return (verr, fl)
        if not indskip:
            try:
                fsfun(fl)
            except FileNotFoundError: # 2, no such file / dir.
                Deb_Prtlog(LOGMSG["copnofilewr"].format(fl,srcfld),logging.WARN)
            except Exception as err:
                Deb_Prtlog(LOGMSG["copunker"].format(indcopy,fl,
                               err.__class__.__name__,err.args))
                verr = METHCODES["wunkerr"]
                return (verr,fl)
    
    return (verr,"")

# Mini timer class, along with tmdict init.
def St_Timer(tmkey):
    """Inserts current time to dictionary under given key.
    
    Also returns the time, but not necessary."""
    tmdict[tmkey] = datetime.datetime.now()
    return tmdict[tmkey]

def Ed_Timer(tmkey):
    """Returns time difference betwixt start of key and now.
    
    If key not set, returns 0 difference."""
    edtm = datetime.datetime.now()
    try:
        return edtm - tmdict[tmkey]
    except KeyError: #as err:
        return edtm - edtm

def Queue_Input(vqueue,vprompt):
    """Waits for the slow minded user to take forever to decide.
    
    Forever.
    And returns whatever they write."""
    #ustr = ""
    vprompt = "{}{}".format(vprompt.rstrip(NLN),NLN)
    vqueue.put(input(vprompt))
    
    #print(prompt)
    #myque.put(Tmod.GetChar())
    vqueue.task_done()
    return None # Does not matter.

def Timed_Input(boolmd,vprompt,vwait,vkey = REGANY,
                vtry = 1,vmsgbad = "",vmsgtmo = ""):
    """Return t/f/s if user writes a keyword in allotted time.
    
    Uses regexp for comparison.
    In bool mode, returns t / f, otherwise string / none.
     Always the second option on timeout or failing key.
    Can set failure limit in vtry, negative for infinite.
    Messages for incorrect response / timeout."""
    global qtrd
    global trd
    logger.debug("start timed input {}".format(datetime.datetime.now()))
    indresp = False
    stresp = None
    indloop = True
    hammertime = vwait # Remaining time.
    while indloop:
        try:
            # Create thread - threads cannot be restarted.
            try:
                if not trd.isAlive(): # User responded at some point before or after timeout.
                    raise AttributeError("Needs moar thread")
                vprompt = "{}{}".format(vprompt.rstrip(NLN),NLN)
                print(vprompt) # Thread usage may have changed, give the new message.
            except AttributeError as err: # This also applies to the initiated list state.
                #logger.debug(err.args)
                trd = threading.Thread(target=Queue_Input, args=(qtrd, vprompt))
                trd.setDaemon(True)
                trd.start()

            # Accept results, or crash in timeout.
            St_Timer("Timed_Input") # Could add a global seq var for threaded calls.
            qget = qtrd.get(timeout = hammertime)
            tdiff = Ed_Timer("Timed_Input")
            hammertime = hammertime - tdiff.total_seconds() # Shorten wait to remainder.
            logger.debug("User wrote <{}> in {}.".format(qget,tdiff))
            
            # Process result at convenience.
            lrefs = re.finditer(vkey,qget,REIS)
            for cref in lrefs:
                tmpspn = (cref.span(0)[0],cref.span(0)[1]) # Refer to other capture groups using span num.
                if indresp and tmpspn[0] == tmpspn[1]: # "Any" reg gives additional empty result len-len, ignore.
                    pass
                elif tmpspn[0] == tmpspn[1]:
                    stresp = "" # But if no input, it is the only one which is okay.
                else:
                    stresp = qget[tmpspn[0]:tmpspn[1]]
                    
                indresp = True
                indloop = False
            if not indresp: # Incorrect response, continue clock.
                logger.debug("It was a stupid, {:.2f}s left.".format(hammertime))
                vtry = vtry - 1
                if vtry == 0: # Negative continues indefinitely.
                    indloop = False
                else:
                    if vmsgbad != "":
                        print(vmsgbad)
            else:
                logger.debug("Total response time {:.2f}s.".format(vwait - hammertime))
        except queue.Empty: # Timeout.
            tdiff = Ed_Timer("Timed_Input")
            logger.debug("User did not respond in {}.".format(tdiff))
            if vmsgtmo != "":
                print(vmsgtmo)
            indloop = False
            
    #qtrd.join() # Nothing can nuke an input thread except the script death.
    if boolmd:
        return indresp
    else:
        return stresp

def Int_Sequence(strbase,st,ed = -1,rdlen = -1):
    """Returns sequential number starting at position, and the end position.
    
    Skips certain readability chars.
    If end position / len is granted, will attempt to return that first, instead.
    Note the returned end is not equivalent to len due to char removal."""
    logger.debug("Start int sequence")
    n = ""
    if rdlen > 0:
        ed = st + rdlen
    if ed > 0:
        n = strbase[st:ed]
        for c in INTREM:
            n = n.replace(c,"") # Could use locale, but that's overkill.
        if n.isnumeric():
            return (int(n),ed)
        else:
            logger.info("Substring not numeric, continuing by sequence. {}".format(n))
    
    indstp = False
    ed = st
    while not indstp:
        c = strbase[ed:ed + 1]
        if ((c.isnumeric() # Regular digit ok. Equivalent to in string.digits, or int conversion.
          or c in INTREM)
         and len(c) > 0): # A readability sign, removed at end.
            ed = ed + 1
        else: # Unknown, halt procedure.
            indstp = True
            n = strbase[st:ed]
            for c in INTREM:
                n = n.replace(c,"") # Could use locale, but that's overkill.
            try:
                return (int(n),ed)
            except ValueError: # Should only occur when empty, ie starts in char.
                logger.error("Given substring not numeric at all, returning default.")
                return (0,st) # Null might screw things up.

def StrLeft(str1,ccnt):
    """Returns n leftmost chars in string."""
    return str1[:ccnt]

def StrRight(str1,ccnt):
    """Returns n rightmost chars in string."""
    return str1[-ccnt:] # Ie go backwards n from the end, until the end.

def StrMid(str1,st,ccnt=-1):
    """Returns n chars starting in st from string.
    
    This is more for completion sake than usefulness."""
    if ccnt < 0:
        return str1[st:]
    else:
        return str1[st:st + ccnt]

def islstup(v1):
    """Checks whether variable is list or tuple.
    
    Any iterable might work, but since it won't recreate that class it's moot."""
    if (isinstance(v1,tuple().__class__)
    or  isinstance(v1,list().__class__)): # Same as passing (list,tuple) as second var.
        return True
    else:
        return False

def isstr(v1):
    """Returns t/f is a string.
    
    Spam."""
    return isinstance(v1,"".__class__)

class IniFile:
    """Ini reader and writer based on configparser.
    
    Features full nested list conversion (cilist) and none handling."""
    flnm = "Config"
    
    def __init__(self,flnm = None):
        """Init."""
        cmpext = INIEXT[2:]
        if flnm is not None:
            if StrRight(flnm, len(cmpext)).lower() == cmpext.lower():
                flnm = flnm[0:-len(cmpext)] # Exclude right.
            self.flnm = flnm
        self.cnfg = configparser.ConfigParser()
        self.Read_Ini()
        self.Sval(INICDEF,"Root","",True) # Test that saving works.
    
    def __getitem__(self,key):
        """Squaries.
        
        Creates temp helper class which calls back the set."""
        return IniDex(self,key)
    
    def Read_Ini(self):
        """Read given file.
        
        Mostly unnecessary with list in memory."""
        self.cnfg.read(INIEXT.format(self.flnm))
    
    def Write_Ini(self):
        """Return current values to ini file.
        
        Completely unnecessary since value changes trigger save in configparser."""
        with open(INIEXT.format(self.flnm), 'w') as cnfgfl:
            self.cnfg.write(cnfgfl)
    
    def Gval(self,catg,vkey):
        """Return value for key under category."""
        try:
            vget1 = self.cnfg[catg][vkey]
            if self.isinipack(vget1): # Unpack cilist first.
                return self.Unpack_List(vget1)
            else:
                return self.SwapNull(vget1,2)
        except KeyError: # No such catgeory or key.
            return None
    
    def Sval(self,catg,vkey,nval,autosave = False):
        """Set value for key under category.
        
        Creates category if missing.
        Seems to save automatically in module sometimes,
         assume it doesn't since main fails."""
        if (not self.cnfg.has_section(catg)
        and catg.lower() != INICDEF.lower()):
            self.cnfg.add_section(catg) # Only default section granted, others must be created.
            
        if islstup(nval): # Iterables converted to nested list structure, cilist.
            self.cnfg[catg][vkey] = self.Pack_List(nval)
        else:
            self.cnfg[catg][vkey] = str(self.SwapNull(nval, 1)) # Non strings raise typeerror.
        if autosave:
            self.Write_Ini()
    
    def SwapNull(self,v1,svgt):
        """Swaps none and string by mode.
        
        In save (1), none becomes string.
        In get (2), string becomes none."""
        if svgt == 1 and v1 is None:
            return ININULL
        elif svgt == 2 and v1 == ININULL:
            return None
        else:
            return v1
    
    def IniStr(self,vstr1):
        """Calls str on var then escapes problematic chars (in lists).
        
        Repr might be more precise for the job,
         yet requires more unpredictable back conversion work.
        Could use the non escaped regex if user is a smartarse."""
        vstr2 = str(self.SwapNull(vstr1, 1))
        for c in INISTRC:
            vstr2 = vstr2.replace(c,BCKSLS + c)
        vstr2 = """ {}{}{}""".format(QUOMRK,vstr2,QUOMRK)
        return vstr2
    
    def IniStrRev(self,vstr1):
        """Removes prior escapes from string.
        
        Uses regex since we have it ready.
        Prolly more efficient to send substring in both space + time,
         than regex the whole thing and limit st + ed (so no parm alt)."""
        lstr1 = []
        lrefs = re.finditer(REGILST.format(""),vstr1,REIS)
        st = 0
        for cref in lrefs:
            tmpspn = (cref.span(1)[0] - 1,cref.span(1)[1])
            lstr1.append(vstr1[st:tmpspn[0]]) # Cut out slash.
            st = tmpspn[1] - 1 # Include the struct mark only.
        lstr1.append(vstr1[st:len(vstr1)]) # Add the rest regardless.
        return self.SwapNull("".join(lstr1), 2)
    
    def Pack_List(self,lst1):
        """Convert complex list / tup of base classes to string.
        
        Other modules such as csv, xml, or json lack the depth part.
        Distinguished by L [... ] structure.
        Don't really need squaries or quotes, nevertheless they're escaped - returned.
        Can use recursion or reverse stack method (dfs) -
         list members extracted in fifo order but inner depth gains priority.
        Handles single value lists, silly as they are."""
        logger.debug("Start ini pack list")
        pack1 = []
        pack1.append(INILIST)
        if len(lst1) == 0: # Empty lists fizzle ere first insert.
            pack1.append(" [")
            pack1.append(" ]")
            return "".join(pack1)
        vque = deque()
        indcom = False # Comma added after a member read, before squaries.
        vque.append((lst1,0,0)) # The other parms indicate number of squaries.
        while len(vque) > 0:
            pv = vque.pop()
            if islstup(pv[0]): # List - repeat packing with extra squaries.
                lexp = reversed(
                        [(pv[0][i],
                         pv[1] + 1 if i == 0 else 0,
                         pv[2] + 1 if i == len(pv[0]) - 1 else 0)
                        for i,_ in enumerate(pv[0])])
                vque.extend(lexp)
                # Longer route.
#                 lsplt = pv[0]
#                 opsqr = pv[1] + 1
#                 edsqr = pv[2] + 1
#                 for i,_ in enumerate(lsplt):
#                     opsqr2 = 0
#                     edsqr2 = 0
#                     if i == 0: # First.
#                         opsqr2 = opsqr
#                         opsqr = 0 # Not really necessary since triggered once.
#                     if i + 1 == len(lsplt): # Last.
#                         edsqr2 = edsqr
#                         edsqr = 0
#                     lexp.append((lsplt[i],opsqr2,edsqr2))
            else: # Assumed to be string.
                if indcom:
                    pack1.append(",")
                indcom = True
                pack1.append(" [" * pv[1])
                pack1.append(self.IniStr(pv[0]))
                pack1.append(" ]" * pv[2])
        return "".join(pack1)
    
    def isinipack(self,lstr1):
        """Check whether string matches complex ini list structure.
        
        It is only an initial structure check.
        Bracket and que balancing during unpack itself."""
        if StrLeft(lstr1,len(INILIST)) != INILIST:
            return False
        if StrMid(lstr1,len(INILIST),2) != " [":
            return False
        if StrRight(lstr1,2) != " ]":
            return False
        return True
        
    def Unpack_List(self,vstr1):
        """Convert ini list string to complex list.
        
        New lists are created and reference added to stack on [.
        Quoted strings are added to current list.
        Pop an older list on reaching ].
        Regex in use counts for escape, for future convenience.
         Unfortunately, results cannot overlap chars (eg ana in banana),
         hence the additional spaces in pack.
         Nevertheless, need to sandbox empty str to avoid extra space inside."""
        logger.debug("Start ini unpack list")
        if not self.isinipack(vstr1):
            logger.error("Not a cilist")
            raise TypeError("Not a cilist") # Shouldn't call this function.
        pack1 = None # Current list getting appended. Popping this prematurely is bad struct.
        pack2 = None # Previous list. Swallows up the new list.
        vque = deque() # Stores deep list refs whilst reading pack str.
        lrefs = re.finditer(REGILST.format("^"),vstr1,REIS) # Non escaped, ie structural.
        strmode = False
        st = 0
        for cref in lrefs:
            tmpspn = (cref.span(1)[0],cref.span(1)[1])
            strc = vstr1[tmpspn[0]:tmpspn[1]]
            if strc == "[": # Start new list as mem of cur, shelve to old.
                if strmode:
                    msgerr = "Cilist struct error, unclosed str at {}-{}.d".format(st,tmpspn[0])
                    logger.error(msgerr)
                    raise TypeError(msgerr)
                vque.append(pack1)
                pack2 = pack1 # Works like peek.
                pack1 = []
                if pack2 is not None:
                    pack2.append(pack1) # Store ref as mem.
            elif strc == "]": # This list done, pop its container.
                if strmode:
                    msgerr = "Cilist struct error, unclosed str at {}-{}.".format(st,tmpspn[0])
                    logger.error(msgerr)
                    raise TypeError(msgerr)
                pack3 = pack1 # Have to save it due to popping the bottom at last bracket.
                try:
                    pack1 = vque.pop()
                except IndexError:
                    msgerr = "Cilist struct error, bracket close without open at {}.".format(tmpspn[0])
                    logger.error(msgerr)
                    raise TypeError(msgerr)
            elif strc == QUOMRK: # String st/ed.
                if vstr1[tmpspn[0] + 1:tmpspn[1] + 1] == QUOMRK: # Regex missed case.
                    if strmode: # Bad, ought to be comma separated.
                        # Can be made acceptable by running rev only.
                        msgerr = "Cilist struct error, sequential mems {}-{}.".format(st,tmpspn[0])
                        logger.error(msgerr)
                        raise TypeError(msgerr)
                    else: # Empty.
                        pack1.append("")
                        st = tmpspn[1] + 1
                else:
                    if strmode: # End - append to current list whilst clearing escapes.
                        pack1.append(self.IniStrRev(vstr1[st:tmpspn[0]]))
                        strmode = False
                    else: # Start - mark for reading.
                        st = tmpspn[1]
                        strmode = True
        # No need for last iteration, should end in close.
        # A proper structure leaves pack3 as the outermost list, pack1 as start and queue emptied.
        if pack1 is not None: # Missing squaries ed.
            msgerr = "Cilist struct error, brackets opened left unclosed."
            logger.error(msgerr)
            raise TypeError(msgerr)
        
        return pack3

class IniDex:
    """For 2 indices of getitem and set methods.
    
    Holds ref back to main which interrupts destructor,
     unsure one is used and it should be temp anyway."""
    def __init__(self,iniparent,catg):
        """Init."""
        self.iniparent = iniparent
        self.catg = catg
    
    def __getitem__(self,key):
        """Squaries."""
        return self.iniparent.Gval(self.catg,key)
    
    def __setitem__(self,key,value):
        """Squaries assignment.
        
        Autosave detection would have to go through value tup."""
        self.iniparent.Sval(self.catg,key,value,autosave = True)

def Sign(n):
    """Returns number's sign.
    
    Math has copysign which is two parameter with some multiplication."""
    if n > 0:
        return 1
    elif n < 0:
        return -1
    return 0

def Dict_Compare(d1, d2):
    """Compares two dictionaries.
    
    Returns tuple containing:
     Dict of keys in d1 and not d2 | in d2 and not d1 |
     modified values - tuple of both | d1 = d2.
    Keys must be convertible to set (not list). 
    """
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    d1_ext = d1_keys - d2_keys
    d2_ext = d2_keys - d1_keys
    d1_eel = {o:d1[o] for o in d1_ext} # Cont: Check for dict index by entire set.
    d2_eel = {o:d2[o] for o in d2_ext} 
    vchange = {o:(d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    vmatch = {o:d1[o] for o in intersect_keys if d1[o] == d2[o]}
    return (d1_eel, d2_eel, vchange, vmatch)

def Magicrep(sbase = None, **repdct):
    """Magic regrep from dict (as function).
    
    Translation: Triggers on all input, grabs replacement per each from dict.
    If base string is given, will return its replacement, otherwise lmb."""
    repfunc = lambda mtc:repdct[mtc.group(0)]
    ptrn = re.compile("|".join([re.escape(k) for k in repdct.keys()]),re.M)
    if sbase is not None:
        return ptrn.sub(repfunc,sbase)
    else:
        return lambda str1: ptrn.sub(repfunc,str1)

def Multirep(sbase,fchr = "",rchr = "",**repdct):
    """Replaces all occurrences of char / string with another.
    
    Fchr and rchr must be strings of same length -
     each char is replaced with equivalent position.
    Alternatively dict must be of str:str, replacing each pair.
    All replacement is single pass."""
    srep = sbase
    if len(fchr) > 0:
        srep = srep.translate("".maketrans(fchr,rchr))
        # Alt: srep = "".join(repdct2.get(c,c) for c in srep) # Rebuilds the string from chars.
    if len(repdct) > 0:
        srep = Magicrep(srep,**repdct)
        # Alt: srep = Magicrep(**repdct)(srep)
    return srep

def List_Format(lst1, lph = LSTPH, *args):
    """Replaces placeholder instances in a list with args.
    
    Only basic order of appearance, no naming.
    Unlike format, leaves missing ph untouched,
     and extra args do nothing (other than log err).
    Deep replacement of lstup to lists as well.
    
    >>> List_Format([LSTPH,2,LSTPH,3,LSTPH],LSTPH,5,["apples","oranges"],None)
    [5,2,["apples","oranges"],3,None]
    >>> List_Format([LSTPH,2,LSTPH,3,LSTPH],LSTPH,5)
    [5,2,LSTPH,3,LSTPH]
    """
    j = 0
    vque = deque()
    vque.append(([],lst1,0))
    while len(vque) > 0:
        (lout,lin,i) = vque.pop()
        indstop = False
        if i >= len(lin):
            indstop = True
        while not indstop:
            if lin[i] == lph:
                try:
                    iv = args[j]
                except IndexError:
                    logger.error("Insufficient parameters sent to format.")
                    iv = lin[i]
                    #return lst1
                j = j + 1
            elif islstup(lin[i]):
                iv = []
                vque.append((lout,lin,i + 1)) # Defer to later insertion.
                vque.append((iv,lin[i],0)) # Explore the inner list first.
                indstop = True
            else:
                iv = lin[i]
            
            lout.append(iv)
            i = i + 1
            if i >= len(lin):
                indstop = True

    if j < len(args):
        logger.error("Excessive parameters sent to format.")
    return lout

def Heb_Reverse(vstr,trev = 1):
    """Rearranges a string containing english, hebrew, punctuation etc.
     
    Different methods of reversal.
    1: Heb and eng interact normally, but eng is reversed around punctuation.
    For example, (heb) hello.world (heb2) -> (heb) world.hello (heb2).
    Ostensibly had some subtleties regarding direction of parentheses / brackets,
    but that was my misconception.
    Digits act like letters with a variable direction (separable by punc in eng)."""
    vrev = []
    if trev == 1:
        indeng = False
        st = 0
        ed = -1
        stp = -1
        edp = -1
        tmpeng = deque()
        for i,_ in enumerate(vstr):
            if (vstr[i] in LETENG
            or (vstr[i] in LETDIG)):
                if indeng: # Continuation of the word.
                    ed = i
                else:
                    if ed >= 0: # Add the prior heb.
                        vrev.append(vstr[st:ed + 1])
                    st = i
                    ed = i
                if edp >= 0: # Punctuation in eng is reversed in both respects.
                    # Actually, no punc inner reversal.
                    #tmpeng.appendleft("".join(reversed(vstr[stp:edp + 1])))
                    if indeng or len(vrev) == 0:
                        tmpeng.appendleft("".join(vstr[stp:edp + 1]))
                    else: # Asymmetrically, punc seems to prefer heb on either side.
                        vrev.append("".join(vstr[stp:edp + 1]))
                    stp = -1
                    edp = -1
                    st = i
                indeng = True
            elif (vstr[i] in LETHEB):
                if not indeng: # Continuation of the word.
                    ed = i
                else:
                    if ed >= 0: # Eng reversed.
                        tmpeng.appendleft(vstr[st:ed + 1])
                    if len(tmpeng) > 0: # Add the entire eng queue.
                        vrev.extend(tmpeng)
                        tmpeng.clear()
                    st = i
                    ed = i
                if edp >= 0: # Punctuation separating heb is in normal order.
                    vrev.append(vstr[stp:edp + 1])
                    stp = -1
                    edp = -1
                    st = i
                indeng = False
            else: # Punctuation takes on the direction of lang after it, mayhap.
                if ed >= 0:
                    if indeng:
                        tmpeng.appendleft(vstr[st:ed + 1])
                    else:
                        vrev.append(vstr[st:ed + 1])
                    st = -1
                    ed = -1
                if edp < 0:
                    stp = i
                edp = i
                 
        # Final handling of all cases - technically, as though heb was triggered.
        if indeng and edp >= 0: # Punctuation reversed if not separating heb.
            tmpeng.appendleft(vstr[stp:edp + 1])
        elif indeng and ed >= 0: # Eng reversed.
            tmpeng.appendleft(vstr[st:ed + 1])
        elif not indeng and edp >= 0:
            vrev.append(vstr[stp:edp + 1])
        elif not indeng and ed >= 0:
            vrev.append(vstr[st:ed + 1])
        if len(tmpeng) > 0:
            vrev.extend(tmpeng)
            tmpeng.clear()
         
        return "".join(vrev)

def Sufstrip(str1,lsuf):
    """Remove suffixes from string if present.
    
    Note that rstrip converts a string into characters removes individually."""
    if not islstup(lsuf): # Should be str.
        lsuf = [lsuf]
    retstr = str(str1) # Copy.
    for sf in lsuf:
        if retstr.endswith(sf):
            retstr = retstr[:-len(sf)]
    return retstr

def Hash_Str(vlong,chrs = HASHDEF,indasc = 1):
    """Create hashed string from value.
    
    Accepts str, dict or other json interpretable object.
    Json is necessary to enforce order in eg dicts.
    Note that json dumps numbers adequately.
    Bytearrays have a decode method, but it fails for non strings.
    Since the hash value is not shown, preferred to pick uniform distro
    over a mod approach (which maps the first values correctly).
    Other forms of hash are sha1, sha2, md5 - less secure.
    Can be used as function cache under filename - pass the parms dict."""
    if isstr(vlong):
        vhash = hashlib.sha256(vlong.encode('utf-8')).hexdigest()
    else: # Dict.
        vhash = hashlib.sha256(json.dumps(vlong).encode("utf-8")).hexdigest()
    if indasc != -1:
        # Converts to list of 2 hexchars each (sans last standalone),
        # then each elem to an ascii char or subset of list.
        if indasc == 0: # All ascii.
            fnc = chr
        else:
            fmaprng = lambda x: int(x / CNTASC * len(HASHCHR[indasc]))
            # Alt: Mod.
            # fmaprng = lambda x: x % len(HASHCHR[indasc])
            fnc = lambda x: HASHCHR[indasc][fmaprng(x)]
        
        hsh2str = [fnc(int(vhash[2 * ic:2 * ic + 2],16))
                   for ic in range(len(vhash) // 2)]
        hsh2str = "".join(hsh2str)
    else: # Produces nifty assortment of gibberish.
        hsh2str = bytearray.fromhex(vhash)
        hsh2str = bytes(hsh2str)
        hsh2str = "".join(map(chr,hsh2str))
    
    hsh2str = hsh2str.replace(r"\x","") # Remove non chars.
    vn = hsh2str[:chrs]
    return vn

def Hash_Digits(vlong,digs = HASHDEF):
    """Small number of digits to identify long value.
    
    Accepts str, dict or other json interpretable object."""
    if isstr(vlong):
        vhash = hashlib.sha256(vlong.encode('utf-8')).hexdigest()
    else: # Dict.
        vhash = hashlib.sha256(json.dumps(vlong).encode("utf-8")).hexdigest()
    vn = int(vhash, 16) % (10 ** digs) 
    return vn

def Ellipsis_Rep(lfull,lpart,ellimark = "..."):
    """Replaces ellipsis from a partial list with the full data.
    
    The intent is to discard elems left and right of el, per their count.
    Impossible to discern the position for multiple els.
    If partial list is longer, will simply drop the el"""
    # Index is not a major improvement in speed - linear,
    # and lacks multielem, so disabled it.
#     if len(ellimark) == 1: 
#         try:
#             idx = lpart.index(ellimark)
#         except ValueError: # No elli.
#             return lpart
    if not islstup(ellimark):
        ellimark = [ellimark]
    idx = min([i for i,v in enumerate(lpart) if v in ellimark])
    vret = lpart[:idx] + lfull[idx:len(lfull) + idx - len(lpart)] + lpart[idx + 1:]
    return vret

# Checks whether imported.
if __name__ == '__main__':
    print("hello world")
    flpt = Path("CrawlMe.txt")
    booli = File_Exists(flpt)
    print(booli)
    tini = IniFile("Test.InI")
    tval = tini.Gval("Not","Exist")
    print("No ticket:",tval)
    tini.Sval("Main","Empty",None)
    tval = tini.Gval("Main","Empty")
    print("Null representation:",tval)
    plt0 = ["This","",["is","a",[[["ridi\[\]\"culous"]]]],"list",None] # DEAL WITH THIS
    plt1 = tini.Pack_List(plt0)
    print("Packed X 1",plt1)
    plt2 = tini.Unpack_List(plt1)
    print("Unpacked X 1",plt2)
    plt1 = tini.Pack_List(plt2)
    print("Packed X 2",plt1)
    plt2 = tini.Unpack_List(plt1)
    print("Unpacked X 2",plt2)
    bad1 = """L [ "hello" ] ]""" # Too many closes.
    bad2 = """L [ [ "hello" ]""" # Too many opens.
    bad3 = """L [ [ "hello ]""" # Unbalanced ques.
    try: # All known structural errors raised as type.
        print(tini.Unpack_List(bad1))
    except TypeError as err:
        logger.debug("Abuse type 1: {}".format(err.args))
    try: # All known structural errors raised as type.
        print(tini.Unpack_List(bad2))
    except TypeError as err:
        logger.debug("Abuse type 2: {}".format(err.args))
    try: # All known structural errors raised as type.
        print(tini.Unpack_List(bad3))
    except TypeError as err:
        logger.debug("Abuse type 3: {}".format(err.args))
    # Despite appearing like slashes still doubled,
    #  this is a list print thing and actually only one. Check the string len.
    tini.Sval("Main", "Test2", ["This",["is","a"],"list"], True)
    tval = tini.Gval("Main", "Test2")
    print("Nested list extracted",tval)
    tini["Main"]["Test3"] = "Just normal string" #,"not anymore!")
    #tini.Write_Ini()
    tval = tini["Main"]["Test3"]
    print("Spam string",tval)
    print("Sequence",Int_Sequence("the number of the counting shall be 3", 36))
    print("Seq2",Int_Sequence("another 42, if you please",8,0,3))
    print("Seq3",Int_Sequence("another 42, you will fail",7,12))
    Write_CSV_UTF("testcsv.csv", [[1,"\'cheese\'"],[2,"☠wut☠"],[3,"goat"]])
    Write_CSV_UTF("testcsv.csv", [[4,"potty\n ^^",1],[5,"d.n.a",0],[6,"do\tlll@",1]],2)
    Read_CSV_UTF("testcsv.csv",Apply_Func = print)
    d1 = dict(a=1, b=2,c=5)
    d2 = dict(a=2, b=2,d=5)
    ddif = Dict_Compare(d1, d2)
    print("Dict comparison",ddif)
    sbase = "banananabanananaba"
    drep = {"bana":"hammerthe","nana":"grandma"}
    print(Multirep(sbase,"ban","lol"))
    print(Multirep(sbase,**drep))
    print(List_Format([]))
    print(List_Format([LSTPH],LSTPH,5))
    print(List_Format([(LSTPH,1),(LSTPH,2)],LSTPH,"f_1","f_2"))
    print(List_Format([(LSTPH,1),(LSTPH,2)],LSTPH,"f_1","f_2","f_4"))
    print(List_Format([(LSTPH,1),(LSTPH,2)],LSTPH,"f_1"))
    lsfl = []
    for fl in Gen_Filesystem("",3):
        lsfl.append(fl)
    print("Files in project working directory:",lsfl)
#     Copy_Files(["Nothere.txt"],"","Test",1,True)
#     Copy_Files(["CopySpam.txt"],"","Test",1)
#     Copy_Files(["CopySpam.txt"],"Test","Dontmatter",3,None)
    print("Hash string",Hash_Str(1,999,1))
    ursp = Timed_Input(False,"Cheese?", 5,"(^y$)|(yes)",-1,"Come again?","Wake up sir!")
    print("Response", ursp)
    ursp = Timed_Input(True, "Are you sure?",5)
    print("I guess",ursp)
    ursp = Timed_Input(True, "How many more hanging?",5)
    print("I dunno",ursp)
    input("Any threads alive?") # Must input twice if not done before. Stupid.
    
    print("\nFin")
else:
    pass
    
# FIN