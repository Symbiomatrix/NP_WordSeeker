# -*- coding: cp1255 -*-
#!! -*- coding: utf-8 -*-
"""
Created on 30/10/19

@author: Symbiomatrix

Todo:
- Drop button should be enabled only after commit + select.
  New, rollback, drop, desel should disable it.
  (Gridtext, gtype and numdiff changes have no immediate effect).
- Commit should mark null grid cells (red) and refuse to search combos.

Features:
Gui with switchable forms and ad hoc modifications to any controls.
Ad hocs include: Create board from plain text (resizable),
commit style calc combos, css marks for special tiles and selection,
select & drop tiles move. 

Future:

Bugs:
- "AttributeError: Can't get attribute 'BNtrie' on <module '__main__' from..."
  Error when loading a dict saved directly from mmain pickle.
  Prolly the class instance is forked and unusable.
  Workaround: Conversion + load directly from the gui. 

Notes:
- TexteEdit control has toHtml / toPlainText methods for extracting the text.
- Lineedit / label have text property and method.
- Haven't explicitly set it, but the tab order of the grid is cols-rows.
  This is important for input convenience.

Version log:
04/11/19 V0.9 Added empty tile detection.
03/11/19 V0.8 Added select & drop move + button.
01/11/19 V0.7 Completed list handling up to groupings.
31/10/19 V0.5 Completed basic design, grid generation, new + commit (p) + rollback board, colouring (p).
30/10/19 V0.1 Forked gui from ft.
30/10/19 V0.0 New.

"""

#BM! Devmode
DEVMODE = False
if DEVMODE: # DEV
    import design_exp
    mform = design_exp
    BRANCH = "Dev\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "IniMain" # No folder for ini, hope this works.
    DBFLD = BRANCH + "DBFiles"
    BADLOG = BRANCH + "Devlog-d{}.txt" 
    TSTCOL = 4 # For a test query.
    TSTWROW = 1 
else: # PROD
    import design_prd
    mform = design_prd
    BRANCH = "Prd\\"
    LOGFLD = BRANCH + "errlog.log"
    INIFLD = BRANCH + "IniMain"
    DBFLD = BRANCH + "DBFiles" # Cannot use none because dbset is fixed. 
    BADLOG = BRANCH + "Logfail-d{}.txt"
    TSTCOL = 1
    TSTWROW = 1

# BM! Imports
if __name__ == "__main__":
    import utils
    uti = utils
    from utils import LOGMSG,METHCODES
    # Guess I could import the engine functions, but this feels wrong for a test.
    MAXCMB = 0
    fnull = lambda *_:None
    Graph_Input = fnull
    Hexify = fnull
    Convert_Dict = fnull
    Load_Dict = fnull
    Val_Conv = fnull
    Colour_Decision = fnull
    Print_Format = fnull
else:
    # See note on relative imports.
    from mmain import uti
    from mmain import LOGMSG,METHCODES,Deb_Prtlog
    from mmain import BNgraph,BNtrie,MAXCMB
    from mmain import Graph_Input,Hexify,Convert_Dict,Load_Dict,Val_Conv
    from mmain import Colour_Decision,Print_Format
    try:
        # Alt: Global call the first time a text board is committed.
        (tri1,tri2) = Load_Dict()
    except AttributeError: # See bugs.
        Convert_Dict()
        (tri1,tri2) = Load_Dict()
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
                        format="%(asctime)s %(levelname)s:%(name)s:%(message)s") # Adds timestamp.
    logger.setLevel(logging.DEBUG)
SYSENC = "cp1255" # System default encoding for safe logging.
Deb_Prtlog = lambda x,y = logging.ERROR:uti.Deb_Prtlog(x,y,logger)

from PyQt5 import QtCore, QtGui, QtWidgets # v
import datetime
import inspect

# BM! Constants
dbini = None
indcrash = False # Tracks gui crashes, since exit code communication is shoddy.
CSS_RGBA = "background-color: rgba({},{},{},{})"
LOGMSG.update({
"loger": "Unknown error in log encoding.\n {} {}",
"guier":"Error in gui: Func {}, class {} {}",
"miscer": "An odd thing happened in {}.",
"mainer": "Run crashed, check log.",
"maintmo": "Program has timed out, quitting.",
"mainok": "Run completed, continue.",
# "queok": "Added records to queue: {} new, {} iffy, {} db cons, {} dropped.",
# "quecan": "Queuing cancelled by user.",
# "quedok": "Removed key {} from queue.",
# "fopenok": "Opened file {} successfully.",
# "fopenwr": "Could not open file {} , not in the filesystem.",
# "fopener": "Could not open file {} , reason unknown.",
# "swpwr": "Cannot swap key {}, not ambiguous.",
# "swpok": "Swapped db connections for key {}.",
# "qcnver": "Failed to convert key to string: {}",
# "qdbok": "Added {} new and updated {} files in tags.",
# "qupder": "Could not update file record after {} updated files.\n Reason: {} {}\n Records: {}",
# "qinser": "Could not insert file records after {} updated files.\n Reason: {} {}\n Records: {}",
# "updgdeb": "Warning of type {}: {}",
# "runqbadwr": "Ignored vaguely formatted query filters: {}",
# "lwdbok": "Retrieved {} rows from tags.",
# "null": "This is the end my friend."
})
METHCODES.update({
"guierr": (1,"Gui froze."),
"cmderr": (11,"Disallowed operation."),
# "inserr": (5,"Insert to db failed."),
# "upderr": (6,"Update db failed."),
# "infloop": (9,"Entered an infinite loop state."),
# "selerr": (21,"Select failed."),
# "csverr": (22,"Write to csv failed."),
# "cnverr": (31,"Type conversion failed."),
# "filnext": (32,"File does not exist."),
# "nullval": (33,"Some values missing from data."),
# "badact": (41,"Cannot select this action."),
# "userq": (55,"User prompted quit function.")
})
MINTS = 86400 # Any less fails with oserr 22.
MINTS = 1000000000 # Avoiding regular numbers, for lack of more intelligent type detection.
MAXTS = 4102444800 # 01/01/2100.
MINDT = datetime.datetime(1970,1,2,2,0) # Below this causes oserr on ts.
DATETYPE = MINDT.__class__
DEFDT = datetime.datetime(1971,1,1)
QUETXT = "{cmb}-{sc1}-{sc2}"
SEPHILE = ["jpg","gif","png","jpeg", # Files to be opened with default editor.
           "mp4","ods","xls","xlsx","csv"]
EDITXT = ["C:\\Program Files (x86)\\Notepad++\\notepad++.exe","notepad.exe"]
FORMDIR = dict() # Ease of access to form loads.
# Key for quick reference, v[0] for ini storage, v[1] default value.
INIDDL = {"CHKUPD":("CheckUpdRem",1), # Boolean converted to string.
          "CHKFUL":("CheckLoadFull",0),
          "CHKDIR":("CheckLoadDir",1),
          "CHKDSL":("CheckDeselectRem",1),
          "LSTDIR":("LastDirectory","C:\\"),
          "DEFSER":("LastSeries",19),
          "NULL":("TheEnd",None)}
# Key / important values which the user might have not filled (or deleted).
FILLCHK = ["pid","lseq","series","fldir","flnm","tagscene"] # Entities debatable.
# Def vals. Tagscene, enti and ref may be empty string, but this is equivalent to null for checks.
DEFQUE = {"pid":0,"lseq":-1,"qseq":-1,"series":0,"fldir":"C:\\temp","flnm":"Nonce.txt",
          "tagscene":None,"tagenti":None,"refsrc":None,"dsnd":DEFDT,"dmod":DEFDT,
          "fsz":0,"dcre":None,"dupd":None,"comments":None} # Db safe values.
QUETYPES = {"pid":1,"lseq":1,"qseq":1,"series":1,"fldir":11,"flnm":11,
            "tagscene":0,"tagenti":12,"refsrc":0,"dsnd":4,"dmod":4,
            "fsz":1,"dcre":41,"dupd":42,"comments":0}
# Control groups - use getat(self,name) to activate them.
# Name, form separator:Type, Que props.
# 1 = Detail display and input. 2 = Old db view. 
# 11 = Db where filters. 12 = Query form detail view.
# Dicts cannot have repeated keys, hence the separator.
# Alt: Define the types as a single entry list, check for "v in types" later.
# Alt2: Have any sigevent calls send the property (or a separate ref dict)
#  directly rather than quecont ref only.
QUECONTS = {
#     ("txtSeries",0):(1,"series"),
#     ("txtFile",0):(1,("fldir","flnm")), # Enforce existence of both.
#     ("txtScene",0):(1,"tagscene"),
#     ("txtEnti",0):(1,"tagenti"),
#     ("txtSource",0):(1,"refsrc"),
#     ("txtDate",0):(1,"dsnd"),
#     ("txtSize",0):(1,"fsz"),
#     ("txtComment",0):(1,"comments"),
#     ("txtSeriesOld",0):(2,"series"),
#     ("txtFileOld",0):(2,("fldir","flnm")),
#     ("txtSceneOld",0):(2,"tagscene"),
#     ("txtEntiOld",0):(2,"tagenti"),
#     ("txtSourceOld",0):(2,"refsrc"),
#     ("txtDateOld",0):(2,"dsnd"),
#     ("txtSizeOld",0):(2,"fsz"),
#     ("txtCommentOld",0):(2,"comments"),
#     ("txtSeriesR",0):(11,"series"),
#     ("txtFileR",0):(11,("fldir","flnm")),
#     ("txtSceneR",0):(11,"tagscene"),
#     ("txtEntiR",0):(11,"tagenti"),
#     ("txtSourceR",0):(11,"refsrc"),
#     ("txtDateR",0):(11,"dsnd"),
#     ("txtSeries",1):(12,"series"),
#     ("txtFile",1):(12,("fldir","flnm")),
#     ("txtScene",1):(12,"tagscene"),
#     ("txtEnti",1):(12,"tagenti"),
#     ("txtSource",1):(12,"refsrc"),
#     ("txtDate",1):(12,"dsnd"),
#     ("txtSize",1):(12,"fsz"),
#     ("txtComment",1):(12,"comments")
}
# Controls whose focus event requires overriding (connection).
FOCOFFCONT = dict()
FOCOFFCONT["Main"] = [("focusOutEvent",qtcont,"Sig_Focout")
                      for qtcont,p in QUECONTS.items() if p[0] == 1]
FOCOFFCONT["Main"].extend([("focusInEvent",qtcont,"Sig_Focin")
                           for qtcont,p in QUECONTS.items() if p[0] == 1])
FOCOFFCONT["Query"] = [("focusOutEvent",qtcont,"Sig_Focout")
                       for qtcont,p in QUECONTS.items() if p[0] == 11]
FOCOFFCONT["Query"].extend([("focusInEvent",qtcont,"Sig_Focin")
                            for qtcont,p in QUECONTS.items() if p[0] == 11])  

# BM! Defs

class Grouping:
    """Quick access double dict for finding an element's group and group's other elems."""
    def __init__(self):
        self.dgrpref = dict()
        self.dstore = dict() # Of dicts.
        
    def Add_Key(self,e,k,g):
        """Adds a ref from key k to group g and from g to elem e. 
        
        The keys must be suitable for indexing, elem may be anything."""
        self.dgrpref[k] = g # Currently 1-1.
        if g not in self.dstore:
            self.dstore[g] = dict()
        self.dstore[g][k] = e
    
    def Get_Group(self,g):
        """Obtains all elems in a group.
        
        Dict does include the key, for no specific reason."""
        return self.dstore[g]
    
    def Group_Other(self,k,g):
        """Obtains the elems in a group save for one.
        
        Converted to a list, no keys necessary."""
        return [self.dstore[g][nok] for nok in self.dstore[g].keys()
                if nok != k]
        
# List controls split to several parts - possess a ref and group num,
# one selection deselects all others.
MLSTCONT = Grouping()

def isdate(dt):
    """Check if value is feasible date.
    
    Dates such as 13/3/3333 yield oserr 22 invalid argument when timestamped."""
    inddt = isinstance(dt,DATETYPE)
    if inddt:
        try:
            dt.timestamp()
        except OSError:
            inddt = False
    return inddt

def Type_Conv(val,ntyp,baconv = False):
    """Convert to type by list.
    
    0 = string, 1 = int, 4 = date, 11 = path (filename / dir / both),
    12 = comma separated.
    Identical to 4 here: 41 = cre date, 42 = upd date. 
    Returns verr when failed.
    Also does conversion to gui form - specific str formatting."""
    verr = 0
    #filedb = dbrefs[0]
    tval = None
    if not baconv:
        if val == "":
            tval = None
        elif ntyp == 0:
            tval = val
        elif ntyp == 1:
            try:
                tval = int(val)
            except Exception:
                verr = 31
        elif ntyp in (4,41,42):
            try:
                raise NotImplementedError
                #tval = ldb.Date_Conv(val)
            except Exception:
                verr = 31
            if not isdate(tval):
                verr = 31 # Dateconv usually fails silently.
        elif ntyp == 11:
            try: # Creep: Relative paths should be erroneous or extended.
                flext = uti.File_Exists(val)[0] 
                if flext == 0: # Filename, nonexistent file or gibberish. The last raises an exception.
                    if len(os.path.split(val)[0]) >= 0:
                        verr = 32
                    else: # Cannot test filename existence.
                        tval = (None,val)
                elif flext == 1: # Full path.
                    tval = os.path.split(val)
                elif flext == 2: # Dir only.
                    tval = (val,None)
            except Exception:
                verr = 31
        elif ntyp == 12:
            try:
                if uti.islstup(val):
                    tval = val
                else: # Str.
                    tval = val.split(",")
            except Exception:
                verr = 31
        else:
            tval = val
            # verr = 31
    else: # Conversion to str ought to encounter few failures.
        if val is None:
            tval = ""
        elif ntyp in (4,41,42):
            try:
                raise NotImplementedError
                #tval = filedb.Disp_Res(val) # Basically independent function, but is in internal usage.
            except Exception:
                verr = 31
        elif ntyp == 11: # Either filename, dir or path tup.
            try:
                if uti.islstup(val):
                    tval = os.path.join(*val)
                else:
                    tval = str(val)
            except Exception:
                verr = 31
        elif ntyp == 12:
            try:
                if uti.islstup(val):
                    tval = ",".join(val)
                else:
                    tval = str(val)
            except Exception:
                verr = 31
        else:
            try:
                tval = str(val)
            except Exception:
                verr = 31
    
    return (verr,tval)

def Questrcnv(que1,key):
    """Convenience que1 value -> str.
    
    Uses dict to discern type.
    Que1 can be either que1 class or dict (ie one of the bks)."""
    if uti.islstup(key):
        qtyp = QUETYPES[key[0]]
        qval = [que1[k] for k in key]
    else:
        qtyp = QUETYPES[key]
        qval = que1[key]
    (verr,tval) = Type_Conv(qval,qtyp,True)
    if verr != 0:
        Deb_Prtlog(LOGMSG["qcnver"].format(key),logging.WARN)
    return tval

def Init_Parms():
    """Loads up (db connections and) ini parms - LEAN VERSION.
    
    Spam."""
    Deb_Prtlog("Start init parms",logging.DEBUG)
#     filedb = ldb.LiteBrowser(dbbs = "Tagger",cre = CREFILE, crex = CREFILEX, fld = DBFLD,
#                              dbtb = "filetag",nseq = 0,spsz = None,autosp = None)
    dbini = uti.IniFile(INIFLD) # Parms saved or loaded in place using ini keywords.
    for (inikey,inidef) in INIDDL.values():
        vdef = dbini["Main"][inikey]
        if vdef is None:
            vdef = inidef
        dbini["Main"][inikey] = vdef
    return dbini

def Sini(dkey):
    """Grab key from ddl.
    
    Dunno if possible to replace the entire ini statement,
    so that both get and set would function [prolly impossible]."""
    return INIDDL[dkey][0]

def Updini(key,val,typcnv = 0):
    """Update by ddl.
    
    Spam."""
    #global dbini
    (verr,tval) = Type_Conv(val, typcnv)
    if verr == 0: # User may type any garbage - ignore their folly.
        dbini["Main"][Sini(key)] = tval

def List_Files(frm,lstw,indldir = 1):
    """Adds filename/s to list widget.
    
    Per load full ind, will ignore definite connections;
    in this workflow only only update when filled,
    can load only remaining new (or iffy) entries from the folder."""
    raise NotImplementedError # No need for this here at all.

def List_Text(rund):
    """Text view of a combo, with the full values and scores.
    
    Expected format: Full path (not displayed), score1+2, route."""
    tdisp = QUETXT.format(cmb = rund[3],sc1 = rund[1],sc2 = rund[2])
    return tdisp

def List_Add(lstw,laddq):
    """Adds items to a list.
    
    Spam."""
    for rund in laddq:
        # Widget likely does not have member props, 
        # though a list could be matched to ins / del theoretically.
        tdisp = List_Text(rund)
        lstw.addItem(tdisp) # All files in dir added to list.

def QtMsgbox_Okcan(frm,mttl = "Message",mtxt = "Text goes here",mdet = None):
    msg = QtWidgets.QMessageBox(frm)
    msg.setText(mtxt)
    msg.setWindowTitle(mttl)
    if mdet is not None:
        msg.setDetailedText(mdet)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    v = msg.exec_()
    return v == QtWidgets.QMessageBox.Ok

def QueStr2Key(skey):
    """Converts formatted str to hash + qseq key. 
    
    Till better list member linking is available.
    """
    lkey = skey.split("-")
    # Quick way to obtain hash + seq, and add warning when it exists.
    lkey = [int(k) for k in lkey[-2:]] + [k for k in [lkey[0]] if len(lkey) > 2]
    
    return lkey

def List_Desel(lstw): # ,frm
    """Deselects current items.
    
    Spam."""
    cursel = lstw.selectedIndexes()
    for idx in cursel:
        itm = lstw.item(idx.row())
        itm.setSelected(False)
    #frm.Clear_Details() # Per form function - txts used for data display or update.
    # Leaving this out to prevent repetitive clears.

def List_Del(frm,lstw,selidx):
    """Removes (selected) recs from both list and que class.
    
    Index is list of the (selected) items (modelindex list or empty) format, or ints.
    Not actually items (listwidgetitem) - doesn't know its own index."""
#     self.lstQue.selectedIndexes()[0].row(),
#     self.lstQue.selectedIndexes()[0].column(),
#     self.lstQue.selectedIndexes()[0].data())
    Deb_Prtlog("Start listdel",logging.DEBUG)
#     dbini = dbrefs[-1]
    verr = 0
    inddsl = False
    for itm in selidx: # No items, no delete.
        if isinstance(itm,int):
            idx = itm
        else:
            idx = itm.row()
        skey = lstw.takeItem(idx)
        skey = skey.text()
        # Alt: Generic way.
        # skey = lstw.item(idx).text()
        lkey = QueStr2Key(skey)
        qkey = tuple(lkey[:2])
        
#         scrque.Del_One(qkey)
        inddsl = True
        Deb_Prtlog(LOGMSG["quedok"].format(skey),logging.DEBUG)
        
    if inddsl and int(dbini["Main"][Sini("CHKDSL")]) == 1:
        List_Desel(lstw) # Creep: Ini setting. Faster for multidelete.
        
    return verr

def List_Getsel1(lstw,indque = 0):
    """First selected value in given list. 
    
    Returns its index, separated key / warn and equivalent queue ref if desired.
    0 = no queue, 1 = main, 2 = query.
    Easily expanded to a generator by yielding indices, however no multisel here."""
    selidx = lstw.selectedIndexes()
    if len(selidx) > 0:
        idx = selidx[0].row()
        skey = selidx[0].data()
        # skey = lstw.item(idx).text() # Alt: Generic way.
        lkey = QueStr2Key(skey)
        qkey = tuple(lkey[:2])
        if indque == "":
            quemem = None
        elif indque == "opt":
            quemem = quecmb1[idx][0]
        elif indque == "dang":
            quemem = quecmb2[idx][0]
    else:
        idx = -1
        lkey = None
        qkey = None
        quemem = None
    
    return (idx,lkey,qkey,quemem)

def Quiterr(err):
    """Default exception handling.
    
    Log and print then quit.
    Trigger wherever code potentially unsafe."""
    Deb_Prtlog("Start quit due to error",logging.DEBUG)
    global indcrash # Alt: Append to list requires no global ref.
    badfunc = inspect.stack()[1][3] # [0][3] is current function, 1 is caller.
    # These are much faster methods for current func, but use "private" members.
#     print(inspect.currentframe().f_code.co_name)
#     print(sys._getframe().f_code.co_name)
    Deb_Prtlog(LOGMSG["guier"].format(badfunc,err.__class__.__name__,err.args))
    indcrash = True 
    for frm in FORMDIR.values():
        frm.close()

def Sig_Event(frm,evenm,wig,cfunc):
    """Overrides an event for a widget in form adding function.
    
    Form is the REF rather than name, since directory isn't available at class def time.
    Widget is full quecont key since a precise ref is needed sometimes for the override data.
    (See alts in queconts definition.) 
    All parms are str converted using get attribute, to enable loop defs.
    Functions must be form level and match orig parms (nothing sent here).
    Position of activation is determined by function."""
    acfunc = getattr(frm,cfunc)
    acfunc2 = lambda *p: acfunc((evenm,wig),*p)
    awig = getattr(frm,wig[0])
    aevenm = getattr(awig,evenm)
    frm.dfun[(evenm,wig)] = aevenm
    setattr(awig,evenm,acfunc2)

def Go_Form(curfrm,newfrm):
    """Hide current form and show different one.
    
    Send appname vals as parms.
    Alt: Permit sending references directly."""
    Deb_Prtlog("Start form switch",logging.DEBUG)
    FORMDIR[curfrm].hide()
    FORMDIR[newfrm].show()

def Colour_Control(wedgie,r = None,g = None,b = None,a = None):
    """Sets colour for a control widget.
    
    Uses the handy rgb + alpha css format.
    Send null to remove."""
    if r is None:
        wedgie.setStyleSheet("")
    else:
        wedgie.setStyleSheet(CSS_RGBA.format(r,g,b,a))

class MainApp(QtWidgets.QMainWindow, mform.Ui_MainWindow):
    appname = "Main" 
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        
        self.Screen_Init()
        
        # Custom events.
        self.cmdNew.clicked.connect(self.New_Board)
        self.cmdUpd.clicked.connect(self.Commit_Board)
        self.cmdCan.clicked.connect(self.Rollback_Board)
        # Plain func sends p2 = False which fails the trigger, hence lmb.
        self.cmdDrop.clicked.connect(lambda: self.Select_Drop())
        self.lstRes1.itemSelectionChanged.connect(
            lambda: self.Sel_Combo(self.lstRes1,"opt"))
        self.lstRes1.itemDoubleClicked.connect(
            lambda: self.Desel_Combo(self.lstRes1))
        self.lstRes2.itemSelectionChanged.connect(
            lambda: self.Sel_Combo(self.lstRes2,"dang"))
        self.lstRes2.itemDoubleClicked.connect(
            lambda: self.Desel_Combo(self.lstRes2))
#         self.cmdLoadFld.clicked.connect(self.Load_Click)
#         self.cmdSelDb.clicked.connect(lambda: Go_Form(self.appname,"Query"))
#         self.cmdUpdO.clicked.connect(lambda: self.Upd_Click(1))
#         self.cmdUpdF.clicked.connect(lambda: self.Upd_Click(2))
#         self.cmdUpdA.clicked.connect(lambda: self.Upd_Click(3))
#         self.cmdDelO.clicked.connect(self.Del_Click)
#         self.lstQue.itemSelectionChanged.connect(self.Sel_Queue)
#         self.lstQue.itemDoubleClicked.connect(self.File_Rclk) # Default action.
#         self.savedfoc = self.txtSeries.focusOutEvent # Test way.
#         self.txtSeries.focusOutEvent = self.newfocout
        # Signal events for this form. 
        self.dfun = dict() 
        for qtol in FOCOFFCONT.get(self.appname,[]):
            Sig_Event(self,*qtol)
        
        # Context menu.
        self.quemenu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction("Open file",self)
        action.triggered.connect(self.File_Rclk)
        self.quemenu.addAction(action)
        self.quemenu.addSeparator()
        action = QtWidgets.QAction("Open containing folder",self)
        action.triggered.connect(self.Folder_Rclk)
        self.quemenu.addAction(action)
        action = QtWidgets.QAction("Swap cons",self)
        action.triggered.connect(self.Dbcon_Rclk)
        self.quemenu.addAction(action)
#         self.quemenu.addAction(QtWidgets.QAction("Nothing",self))
        self.sortmenu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction("Name",self)
        action.triggered.connect(lambda: self.Sort_Queue(1))
        self.sortmenu.addAction(action)
        action = QtWidgets.QAction("Size",self)
        action.triggered.connect(lambda: self.Sort_Queue(2))
        self.sortmenu.addAction(action)
        action = QtWidgets.QAction("Warning", self)
        action.triggered.connect(lambda: self.Sort_Queue(3))
        self.sortmenu.addAction(action)
        action = QtWidgets.QAction("Date", self)
        action.triggered.connect(lambda: self.Sort_Queue(4))
        self.sortmenu.addAction(action)
        self.sortmenu.setTitle("Sort by...")
        self.quemenu.addMenu(self.sortmenu)
#         self.lstQue.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
#         self.lstQue.customContextMenuRequested.connect(self.Que_Show_Context)

    def Sig_Focin(self,key,*p): # e parm.
        """Signal for focusinevent, queue controls.
        
        Resets background to ease user view whilst editing."""
        try:
            # Actual connect code goes here.
            # k0 is event, therefore irrelevant for this section.
            qtcont = key[1]
            awig = getattr(self,qtcont[0])
            awig.setStyleSheet("")
            
            # Super call.
            self.dfun[key](*p)
        except Exception as err:
            Quiterr(err)

    def Sig_Focout(self,key,*p): # e parm.
        """Signal for focusoutevent, queue controls.
        
        Using focout rather than text change mostly since settext would trigger that.
        Checks validity of altered (possibly) field.
        Updates in queue if feasible or marks as erroneous otherwise."""
        try:
            # Actual connect code goes here.
            # k0 is event, therefore irrelevant for this section.
            qtcont = key[1]
            awig = getattr(self,qtcont[0])
            pque = QUECONTS[qtcont][1]
            if uti.islstup(pque): # Ldb's listdef would be handy in such cases.
                qtyp = QUETYPES[pque[0]]
                #qval = [que1[k] for k in key] # IMHERE
            else:
                qtyp = QUETYPES[pque]
                #qval = que1[key]
            
            # Specific handling of the focus goes here - eg mark wrong type.
#             (verr,tval) = Type_Conv(awig.toPlainText(),qtyp,False)
#             if uti.islstup(tval) and verr == 0: # Must have both file & dir, for example.
#                 if None in tval: # Any / all must receive bool list, comprehension is slower.
#                     verr = 33 # Logic warning.
#             if verr != 0: # Ignore user update until corrected. 
#                 awig.setStyleSheet("background-color: red")
#                 # Alt: awig.setStyleSheet("background-color: #ff0000"), rgb(255,0,0) 
#                 # Creep: Error indication in widget disallowing update.
#                 # It's fine since a simple move will reset the field since it isn't saved to queue currently.
#             else:
#                 awig.setStyleSheet("")
#                 (idx,_,_,quemem) = List_Getsel1(self.lstQue,1)
#                 if idx >= 0:
#                     if uti.islstup(pque): # Tval might be list (entities), but where it's put matters.
#                         for i,_ in enumerate(tval): # If multitag (dir + fl), give one val to each.
#                             quemem[pque[i]] = tval[i]
#                     else:
#                         quemem[pque] = tval
#                 else:
#                     Deb_Prtlog(LOGMSG["miscer"].format(inspect.stack()[0][3]),logging.WARN)
            
            # Super call.
            self.dfun[key](*p)
        except Exception as err:
            Quiterr(err)
    
    def Screen_Init(self):
        """Small direct links of gui - inner data.
        
        Spam."""
        Deb_Prtlog("Start main screen init",logging.DEBUG)
#         dbini = dbrefs[-1]
        # Init widgets.
#         self.txtDser.setText(dbini["Main"][Sini("DEFSER")])
#         self.chkUpdRem.setChecked(int(dbini["Main"][Sini("CHKUPD")])) # Alt: Setchecked?
#         self.chkLFull.setChecked(int(dbini["Main"][Sini("CHKFUL")]))
#         self.chkLDir.setChecked(int(dbini["Main"][Sini("CHKDIR")]))
#         self.chkDsl.setChecked(int(dbini["Main"][Sini("CHKDSL")]))
        # print(self.chkLDir.isChecked(),self.chkLDir.checkState(),self.chkLFull.checkState()) # Test.
        #self.lstQue.clear()
        self.ltxtBoard = [] # May vary in size.
        MLSTCONT.Add_Key(self.lstRes1,"opt","combo")
        MLSTCONT.Add_Key(self.lstRes2,"dang","combo")
        self.txtHiddenTest.hide()
        self.Clear_Details()
        
        # Value tracking.
#         self.txtDser.editingFinished.connect(lambda:Updini("DEFSER",self.txtDser.text(),1))
#         self.chkUpdRem.toggled.connect(lambda x:Updini("CHKUPD",x,1))
#         self.chkLFull.toggled.connect(lambda x:Updini("CHKFUL",x,1))
#         self.chkLDir.toggled.connect(lambda x:Updini("CHKDIR",x,1))
#         self.chkDsl.toggled.connect(lambda x:Updini("CHKDSL",x,1))
    
    def Clear_Details(self):
        """Disable all detail holder widgets. 
        
        In this form, just need to refresh the board."""
        self.Refresh_Board()
#         try:
#             for qtcont,p in QUECONTS.items():
#                 if p[0] in (1,2):
#                     acont = getattr(self,qtcont[0])
#                     acont.setPlainText("")
#                     if p[0] == 1:
#                         acont.setEnabled(False)
#                         acont.setStyleSheet("")
#         except Exception as err:
#             Quiterr(err)
        
    def Show_Details(self,quemem):
        """Get and display combo from queue for selected index. 
        
        The text is already set, this just overrides the colour.
        Note that quemem is a list of 2d coords;
        rather than check the graph, it recreates the hex based grid."""
        # Deb_Prtlog("Start showdet",logging.DEBUG) # Spam.
        try:
            if quemem is not None:
                lclr = Colour_Decision(quemem,True) # Sel doesn't care for value.
                lboard2 = Hexify(self.ltxtBoard)
                for i,_ in enumerate(quemem):
                    wboard = lboard2[quemem[i][0]][quemem[i][1]]
                    Colour_Control(wboard,*lclr[i])
        except Exception as err:
            Quiterr(err)
    
    def Sel_Combo(self,lstw = None,indque = ""):
        """Display combo on the grid and control both lists.
        
        Also refreshes the field to remove prior selections,
        rather than bother with storage."""
        try:
            #self.Refresh_Board()
            (idx,_,_,quemem) = List_Getsel1(lstw,indque)
            if idx >= 0:
                # Deselect other grouped lists weakly.
                lotr = MLSTCONT.Group_Other(indque,"combo")
                for wedgie in lotr:
                    List_Desel(wedgie)
                self.Clear_Details() # Removes prior sel ere making a new path.
                self.Show_Details(quemem)
            else:
                #self.Clear_Details()
                pass # Auto desel should not affect the board.
        except Exception as err:
            Quiterr(err)
            
    def Desel_Combo(self,lstw):
        """Actively deselect a combo, removing its mark and operations.
        
        Generic desel + refresh board, so automated desel should not go here."""
        try:
            List_Desel(lstw)
            self.Clear_Details()
        except Exception as err:
            Quiterr(err)
    
    def Load_Db(self,laddq):
        """Load data from query form.
        
        As in other functions, laddq should be dict (pid+lseq) of dicts (full data from sel).
        Build it externally as necessary."""
        cntnew = 0
        cntiffy = 0
        cntdrop = 0
        for vtag in laddq.values():
            key = (vtag["pid"],-1) # Use the default load increment.
#             scrque[key] = vtag
        (_,_,cntupd) = List_Add(self.lstQue,laddq,"qseq")
        Deb_Prtlog(LOGMSG["queok"].format(cntnew,cntiffy,cntupd,cntdrop),logging.INFO)
#         scrque.Tag_Postprocess(self.lstQue)
    
    def Que_Show_Context(self,point):
        """Show context menu on rclk.
        
        Spam."""
#         self.testmenu.exec_(point) # Prints regardless of screen dimensions.
        try:
            self.quemenu.exec_(self.lstQue.mapToGlobal(point))
        except Exception as err:
            Quiterr(err)
    
    def File_Rclk(self):
        """Open selected file. 
        
        Spam."""
        try:
            (idx,_,_,quemem) = List_Getsel1(self.lstQue,1)
            if idx >= 0:
                quemem.Open_File()
            else:
                pass
        except Exception as err:
            Quiterr(err)
            
    def Folder_Rclk(self):
        """Open selected file. 
        
        Spam."""
        try:
            (idx,_,_,quemem) = List_Getsel1(self.lstQue,1)
            if idx >= 0:
                quemem.Open_Folder()
            else:
                pass
        except Exception as err:
            Quiterr(err)

    def Dbcon_Rclk(self):
        """Disconnect / reconnect iffy record from db. 
        
        Disc = pass bk to undo, recon = when undo is not null, move it back to bk;
        both overwrite current user input completely.
        Only relevant for mtc 5, for now.
        Updates the displayed list key including postprocessing, but it's display only -
        a swap back ought to ignore mtc 2 when a bk is available."""
        Deb_Prtlog("Start dbcon",logging.DEBUG)
        verr = 0
        try:
            (idx,lkey,_,quemem) = List_Getsel1(self.lstQue,1)
            if idx >= 0:
                (verr,_,_) = quemem.Swap_Dbcon()
                if verr == METHCODES["badact"][0]:
                    Deb_Prtlog(LOGMSG["swpwr"].format(lkey),logging.WARN)
                    return verr
                (tdisp,_) = List_Text(quemem,"qseq")
                self.lstQue.item(idx).setText(tdisp)
                self.Show_Details(quemem) # Refresh display.
                Deb_Prtlog(LOGMSG["swpok"].format(lkey),logging.DEBUG)
#                 scrque.Tag_Postprocess(self.lstQue)
            else:
                pass
        except Exception as err:
            Quiterr(err)
            
    def Sort_Queue(self,sord = 0):
        """Sort queue by a property.
        
        Sort orders defined in global var (strings receive lcase).
        Listwidgets cannot be sorted other than text, so it falls to rebuild.
        Creep: Asc / desc through negative val or ini."""
        raise NotImplementedError
#         try:
#             if not isinstance(sord,int): # Direct field listing.
#                 lord = sord # Check if list.
#                 indsc = False
#             else: 
#                 (lord,indsc) = SORTCODE[sord]
#             if lord is not None:
#                 # Sorts the dict by props.
#                 # When passing a tup to key, will go through each one.
#                 # Note: Itemgetter works for lists, faster. Or attrgetter, methodcaller. 
#                 # Takes multiple indices for complex sorts, but not gen.
#                 sque = OrderedDict(
#                         sorted(scrque.ltags.items(),
#                                key = lambda x:[x[1].gsort(o) for o in lord],
#                                reverse = indsc))
#                 self.lstQue.clear()
#                 List_Add(self.lstQue,sque,"qseq")
#         except Exception as err:
#             Quiterr(err)

    def New_Board(self):
        """User forms layout of a grid which is copied to textboxes in gui.
        
        Spam."""
        try:
            gi = Graph_Input(self.txtGrid.toPlainText())
            gi = Hexify(gi)
            for wboard in self.ltxtBoard:
                # layout.removeWidget(self.widget_name) # I dunno which layout.
                wboard.deleteLater()
                # wboard = None
            self.ltxtBoard = []
            sgi = Val_Conv(gi,True)
            sgi = Hexify(sgi)
            lclr = Colour_Decision(gi,False)
            lclr = Hexify(lclr)
            if gi is not None:
                for i,lcol in enumerate(gi):
                    for j,_val in enumerate(lcol):
                        wboard = QtWidgets.QLineEdit(self.gridLayoutWidget)
                        # Not sure I need this line.
                        wboard.setObjectName("txtBoard_{}_{}".format(i,j))
                        wboard.setText(sgi[i][j])
                        Colour_Control(wboard,*lclr[i][j])
                        self.gridLayout.addWidget(wboard, j * 2 + (i + 1) % 2, i, 1, 1)
                        self.ltxtBoard.append(wboard)
            return gi
        except Exception as err:
            Quiterr(err)
    
    def Commit_Board(self):
        """Get combos for the current board on gui.
        
        Ere this stage, the user may alter the board at will.
        The grid textbox will NOT be considered (used as bk and overwritten)."""
        global quecmb1
        global quecmb2
        verr = 0
        try:
            quecmb1 = []
            quecmb2 = []
            self.lstRes1.clear()
            self.lstRes2.clear()
            self.Refresh_Board()
            # Check for empty tiles. Refresh marks them.
            for wedgie in self.ltxtBoard:
                if len(wedgie.text().strip()) == 0:
                    verr = METHCODES["cmderr"][0]
            if verr != 0:
                return
            gi = [wedgie.text() for wedgie in self.ltxtBoard]
            gi = Val_Conv(gi,False)
            gi = Hexify(gi)
            groot = BNgraph(None)
            groot.build_hex(gi)
            # CONT: Optional trieversal using parms,
            # add to lists,
            # later colour selection. 
            if self.txtGtype.text() == "1":
                potword = groot.trieverse(tri1,tri2)
            elif self.txtGtype.text() == "2":
                potword = groot.numverse(int(self.txtDiff.text()))
            else:
                potword = []
            (optim,dang) = groot.Word_Score(potword)
            lroute = groot.Route_Text(optim)
            quecmb1 = [(*optim[i],lroute[i])
                       for i,_ in enumerate(lroute)]
            lroute = groot.Route_Text(dang)
            quecmb2 = [(*dang[i],lroute[i])
                       for i,_ in enumerate(lroute)]
            List_Add(self.lstRes1,quecmb1)
            List_Add(self.lstRes2,quecmb2)
            print("Topmost score:")
            groot.Print_Scores(optim)
            print("Topmost danger:")
            groot.Print_Scores(dang)
            print("---------------------")
            Print_Format(gi)
        except Exception as err:
            Quiterr(err) 
    
    def Rollback_Board(self):
        """Reset gui to prior configuration (using the bk grid).
        
        Uses the grid textbox, which is only updated by user and commits.
        Not a perfect rollback, murky treatment of drops, good enough for now.
        Also, a true rollback would reset the controls, saving here."""
        global quecmb1
        global quecmb2
        try:
            quecmb1 = []
            quecmb2 = []
            self.lstRes1.clear()
            self.lstRes2.clear()
            gi = Graph_Input(self.txtGrid.toPlainText())
            sgi = Val_Conv(gi,True)
            lclr = Colour_Decision(gi,False)
            if gi is not None:
                for i,_ in enumerate(gi):
                    wboard = self.ltxtBoard[i]
                    wboard.setText(sgi[i])
                    Colour_Control(wboard,*lclr[i])
        except Exception as err:
            Quiterr(err)
    
    def Refresh_Board(self):
        """Resets colours sans combos.
        
        Spam."""
        try:
            lvals = [wedgie.text().strip() for wedgie in self.ltxtBoard]
            lclr = Colour_Decision(lvals,False)
            if lvals is not None:
                for i,_ in enumerate(lvals):
                    wboard = self.ltxtBoard[i]
                    Colour_Control(wboard,*lclr[i])
        except Exception as err:
            Quiterr(err)
            
    def Select_Drop(self,lchain = None):
        """Clears the grid of selected chain and curse destroyed tiles.
        
        Cont: Should copy the new structure to grid text.
        Or mayhap commit ought to do so."""
        global quecmb1
        global quecmb2
        try:
            # Obtain chain from any combo type lists.
            if lchain is None:
                lchain = [] # Prolly a mistake, but this is natural corruption.
                lcmb = MLSTCONT.Get_Group("combo")
                for lstk in lcmb.keys():
                    (cidx,_,_,quemem) = List_Getsel1(lcmb[lstk],lstk)
                    if cidx >= 0: # Is selected.
                        lchain = quemem
            
            # Prep the graph for chain move func.
            lvals = [wedgie.text() for wedgie in self.ltxtBoard]
            lboard2 = Hexify(self.ltxtBoard)
            gi = Val_Conv(lvals,False)
            gi = Hexify(gi)
            groot = BNgraph(None)
            groot.build_hex(gi)
            groot.Tile_Move(lchain)
            # Update the gui from graph.
            for idxc,_ in enumerate(lboard2):
                for idxr,_ in enumerate(lboard2[idxc]):
                    wboard = lboard2[idxc][idxr]
                    nval = Val_Conv(groot.root[(idxc,idxr)].value,True) # Alt: Hex convert all ahead.
                    wboard.setText(nval)
            # Clear board. Not sure whether clear triggers sel / desel.
            # CONT: Should be a func.
            quecmb1 = []
            quecmb2 = []
            self.lstRes1.clear()
            self.lstRes2.clear()
            self.Refresh_Board()
        except Exception as err:
            Quiterr(err)

def Start_Form():
    """Start form - for use by callers.
    
    Spam."""
    verr = 0
    global dbini
    global indcrash # Lasting indication from the gui.
    global FORMDIR
    global quecmb1
    global quecmb2
    dbini = Init_Parms()
    # Start gui.
    app = QtWidgets.QApplication(sys.argv)
    FORMDIR["Main"] = MainApp()
    #FORMDIR["Query"] = QueryApp()
    FORMDIR["Main"].show()
    FORMDIR["Main"].New_Board()
    quecmb1 = [] # No need for the intricacy of updque class. 
    quecmb2 = []
    try:
        app.exec_()
    except Exception as err: # Not very useful, since the gui hangs after uncaught action.
        Deb_Prtlog(LOGMSG["guier"].format(err.__class__.__name__,err.args))
        indcrash = True
    if indcrash:
        verr = METHCODES["guierr"][0]
#     input() # Keeps the thread alive after form window is closed.
    return verr

def Main():
    """Activates function calls.
    
    Main."""
    Deb_Prtlog("Start main",logging.DEBUG)
    uti.St_Timer("Main")
    verr = 0
    
    Start_Form()
    
    tdiff = uti.Ed_Timer("Main")
    print("\nFin.")
    Deb_Prtlog("End main {}".format(tdiff),logging.DEBUG) # Remember that timestamp is automatic in logger.
    if verr == 0:
        uti.Msgbox(LOGMSG["mainok"],"Good morning chrono")
    else:
        uti.Msgbox(LOGMSG["mainer"],"Wake up")
    
    return verr
    
if __name__ == "__main__":
    Main()
