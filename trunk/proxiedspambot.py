#!/usr/bin/env python
import ast
import numbers
import Omegle
import Queue
import sys
import threading

u="""This program requires two arguments on the command line:

The first is the path to a script.  The entire contents of this file will be
passed to eval().  Yeah, it's not secure.  eval() should return a list
containing strings and numbers.  Strings are sent as messages to the stranger
and numbers are interpreted as pauses.  This argument is not optional.

The second argument is an http proxy in any format that urllib2.ProxyHandler()
will accept.  It will be used as a proxy.  If it doesn't hide the program's
public (internet-facing) IP address, the program will die gracefully and
return a non-zero value to the calling shell.
"""

#Global debugging variable
VERBOSE=True #Verbose output
DEBUG=False #Debug output
KEYSTROKEDELAY=0.5 #Delay between simulated keystrokes
STARTTIMEOUT=10 #Seconds to wait for a stranger to do something

class ProxiedOmegleEventHandler(Omegle.EventHandler):
    def __init__(self, start_queue, discon_event):
        """Make an event handler."""
        Omegle.EventHandler.__init__(self)
        self.start_queue = start_queue
        self.has_started = False
        """True if the stranger has started doing something."""
        self.discon_event = discon_event
    def defaultEvent(self, event, chat, var):
        """Print unhandled events."""
        debug(chat.id, "Unhandled event %s: %s"%(event, str(var)))
    def connected(self,chat,var):
        verbose(chat.id, "Connected")
    def recaptchaRequired(self,chat,var):
        if self.has_started == False:
            verbose(chat.id, "Recaptcha Required")
            self.start_queue.put("rr")
            self.has_started = True
    def typing(self,chat,var):
        if not self.has_started:
            self.start_queue.put("ty")
            self.has_started = True
    def gotMessage(self,chat,var):
        if not self.has_started:
            self.start_queue.put("gm")
            self.has_started = True
        for msg in var:
            verbose(chat.id, "Stranger: " + msg)
    def strangerDisconnected(self,chat,var):
        verbose(chat.id, "Stranger disconnected")
        self.discon_event.set()
    #Events to ignore
    def waiting(self,chat,var):
        return
            

def main():
    """Run a chatbot."""
    #Get the script
    script = get_script()
    #Get the proxy
    if len(sys.argv) >=3:
        proxy = sys.argv[2]
    else:
        proxy = None
    #Make a chat
    chat = Omegle.OmegleChat(debug=DEBUG, keystrokedelay=KEYSTROKEDELAY, 
                             proxy=proxy)
    #Give it events
    start_queue = Queue.Queue()
    discon_event = threading.Event()
    chat.connect_events(ProxiedOmegleEventHandler(start_queue, discon_event))
    #Connect to Omegle
    verbose(None, "Starting Chat")
    if chat.connect() is False:
        verbose(None, "Unable to connect to Chat")
        sys.exit(-1)
    #Wait for the other user to say something
    try:
        startstr = start_queue.get(timeout=STARTTIMEOUT)
    except Queue.Empty:
        verbose(chat.id, "Got bored")
        verbose(None, "Terminating")
        sys.exit(-4)
    #Why did we start?
    if startstr == "rr": #Recaptcha required
        verbose(None, "Terminating")
        sys.exit(-2)
    #Ok, so the stranger's said something or started typing.
    for line in script:
        #If we're pausing
        if isinstance(line, numbers.Number):
            if discon_event.wait(line) == True: #If strander disconnected
                break
        elif isinstance(line, basestring):
            if chat.say(line, event=discon_event):
                verbose(chat.id, "Spambot: %s"%line)    
    #Done with the script.  Bye
    chat.disconnect()
    verbose(None, "Terminating")    
    return        
    
def get_script():
    """Open the file specified on the command line, read the contents, and
    either get the script or exit the program."""
    #Check for the script
    if len(sys.argv) < 2:
        usage()
    fname = sys.argv[1]
    #Open the file
    try:
        script_file = open(fname, "r")
    except Exception as e:
        sys.exit("Unable to read script file due to %s: %s"%(str(type(e)), 
                                                             str(e)))
    #Evaluate it
    try:
        script = ast.literal_eval(script_file.read())
    except Exception as e:
        sys.exit("Unable to parse script file due to %s: %s"%(str(type(e)),
                                                              str(e)))
    #TODO: Run through script and do typechecking 
    return script

def usage():
    """Print a usage message and exit."""
    sys.stderr.write(u)
    sys.stderr.flush()
    sys.exit(-3)
    
def verbose(chat, string):
    """Print a string giving information."""
    #What to do if the message isn't specific to a chat
    if chat is not None:
        ostr = "[%s] %s\n"%(chat, string)
    else:
        ostr = string + "\n"
    #Print the message to the appropriate stream
    if VERBOSE:
        sys.stdout.write(ostr)
        sys.stdout.flush()
    elif DEBUG and not VERBOSE:
        sys.stderr.write(ostr)
        sys.stderr.flush()
def debug(chatid, string):
    """Print a string to stderr if debugging is enabled."""
    if DEBUG:
        sys.stderr.write("{%s} %s\n"%(chatid,string))
        sys.stderr.flush()

if __name__ == "__main__":
    main() 