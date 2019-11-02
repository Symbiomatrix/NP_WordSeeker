# -*- coding: utf-8 -*-
#!! -*- coding: cp1255 -*-
"""
Created on 11/08/18

@author: Symbiomatrix

Features:
Creates .py from .ui file using batch command, parameter names.

Version log:
29/10/19 V1.0 Forked.
11/08/18 V0.6 Multiple forms.
11/08/18 V0.5 Does its job (with constant parms).
11/08/18 V0.0 New.

"""

#BM! Devmode
DEVMODE = False
if DEVMODE: # DEV
    INPFLD = """C:\\Itai\\Programming\\Python\\Winpy365\\Projects\\Qtui\\"""
    OUTFLD = """C:\\Itai\\Programming\\Repos\\NP_WordSeeker\\src\\""" # Or current folder.
    INPFILE = {"Main":"TestCheckboard.ui"}
    OUTFILE = {"Main":"design_exp.py"}
    LOGFLD = "Dev\errlog.log" 
    BADLOG = "Dev\Logfail-d{}.txt"
else: # PROD
    INPFLD = """C:\\Itai\\Programming\\Python\\Winpy365\\Projects\\Qtui\\"""
    OUTFLD = """C:\\Itai\\Programming\\Repos\\NP_WordSeeker\\src\\""" # Or current folder.
    INPFILE = {"Main":"Wordseeker.ui"}
    OUTFILE = {"Main":"design_prd.py"}
    LOGFLD = "Prd\errlog.log"
    BADLOG = "Prd\Devlog-d{}.txt" 
    
# BM! IMPORTS
import sys
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
                        format="%(asctime)s %(levelname)s:%(name)s:%(message)s") # Adds timestamp.
    logger.setLevel(logging.DEBUG)
SYSENC = "cp1255" # System default encoding for safe logging.

import ctypes
import datetime
import subprocess

# BM! Constants
RUNCMD = "pyuic5 {inpfld}{inpfile} -o {outfld}{outfile}"
FRMTMLOG = "%y%m%d-%H%M%S" # Time format for logging.
PRTLIM = 1000
LOGMSG = {
"loger": "Unknown error in log encoding.\n {} {}",
"mainer": "Run crashed, check log.",
"mainer1": "Error in build, check log for details.",
"mainer2": "Error in read all, check log for details.",
"mainer3": "Error in save skip labelling, check log for details.",
"maintmo": "Program has timed out, quitting.",
"mainok": "Run completed, continue.",
"mainok1": "Completed crawling list pages {}-{}.",
"mainok2": "Completed reading up to list page {}.",
"null": "This is the end my friend."
}

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
    """
    ctypes.windll.user32.MessageBoxW(0,mtxt,mttl,mtype)

def Deb_Prtlog(vmsg,vlvl = logging.ERROR):
    """Prints and logs message.
    
    Uses logging levels.
    Prints to utf file in case of failure."""
    try:
        smsg = str(vmsg)
    except Exception as err:
        logger.error(LOGMSG["loger"].format(err.__class__.__name__,err.args))
        smsg = vmsg # Try to print as is.
    try:
        smsg.encode(SYSENC)
    except UnicodeEncodeError: # Not safe to print or log.
        now = datetime.datetime.now()
        flnm = BADLOG.format(now.strftime(FRMTMLOG))
        print("Unicorn message intercepted, see logfile {}.".format(flnm))
#         uti.Write_UTF(flnm,smsg,True)
        return
    except Exception as err:
        logger.error(LOGMSG["loger"].format(err.__class__.__name__,err.args))
    
    if len(smsg) <= PRTLIM:
        print(smsg)
    else:
        print("Long message intercepted, check the log.")
    if vlvl == logging.DEBUG:
        logger.debug(smsg)
    elif vlvl == logging.INFO:
        logger.info(smsg)
    elif vlvl == logging.WARN:
        logger.warn(smsg)
    elif vlvl == logging.ERROR:
        logger.error(smsg)
    elif vlvl == logging.CRITICAL:
        logger.critical(smsg)
    else:
        logger.debug(smsg)

# def Main_Test():
#     """Short activation.
#      
#     Spam."""
#  
#     return verr

def Main():
    """Activates function calls.
    
    Main."""
    Deb_Prtlog("Start form creator",logging.DEBUG)
    verr = 0

    # Add ,shell = True for internal commands, whatever that means.
    for k in INPFILE.keys(): # All forms.
        subprocess.call(RUNCMD.format(inpfld = INPFLD, inpfile = INPFILE[k],
                                      outfld = OUTFLD, outfile = OUTFILE[k]))
    
    print("\nFin.")
    logger.debug("End form creator")
    if verr == 0:
        Msgbox(LOGMSG["mainok"],"Good morning chrono")
    else:
        Msgbox(LOGMSG["mainer"],"Wake up")
    
    return verr

# Checks whether imported.
if __name__ == '__main__':
    if DEVMODE:
        Main() # No distinguishing necessary.
    else:
        Main()
else:
    pass
    