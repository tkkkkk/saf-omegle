#!/usr/bin/env python

'''
Created on Mar 22, 2012

@author: stuart
'''

from numbers import Number
from time import sleep
from urllib import urlopen

import Omegle
import os
import srscript
import sys
import threading
import urllib2

global ANTISPAMDELAY
global BOREDOM_TOL
global DEBUG
global FINISHDELAY
global KEYSTROKEDELAY
global LOG_URL
global ONLY_MINE
global RUN_SILENT
global UPDATE_URL
global VERSION
global VERSION_URL

ANTISPAMDELAY = 10
"""Delay in between chats"""

BOREDOM_TOL = 10
"""Give up after this many seconds if the other person hasn't started talking."""

DEBUG = False
"""Print debug messages if True"""

FINISHDELAY = 30

KEYSTROKEDELAY = 0.2
"""Time it takes to tap a key"""

ONLY_MINE = True
#ONLY_MINE = False
"""Only use my script. (normal spamming)"""

RUN_SILENT = False
"""Run without interaction"""

"""Conversation script as a list.
Each list element is either a message to send or a pause.
If the element is a string it will be sent as a message.
If the message is a number, it is interpreted as a time in seconds to wait before sending the next message
"""

base_url = "http://littlesitetomakemoney.appspot.com"
#base_url = "http://127.0.0.1"
LOG_URL = base_url + "/log"
"""URL to open when we start conversing"""

VERSION = "73"
"""Version of the software"""
VERSION_URL = base_url + "/version"
"""URL to get the version from"""

UPDATE_URL = base_url
"""Where to download a new version"""


class HwEventHandler(Omegle.EventHandler):
    
    """Event handler to be given to the chats"""
    
    #Class variables
    
    def __init__(self, start_event, chat_thread, recaptcha_event, 
                 disconnected_event, print_messages=True):
        
        """Initialize event handler.
        
        @param start_event: Event to notify others when conversation starts
        @type start_event: threading.Event
        @param recaptcha_event: Event to set if a recaptcha is required
        @type recaptcha_event: threading.Event
        @param chat_thread: Thread controlling the chat
        @type chat_thread: threading.Thread
        @param disconnected_event: Event to set when stranger disconnects
        @type disconnected_event: threading.Thread
        @param print_messages: Allow normal output
        @type print_messages: Boolean
        """
        
        self.start_event = start_event
        """Event to notify others when conversation starts"""
        self.chat_thread = chat_thread
        """Thread controlling the chat"""
        self.print_messages = print_messages
        """Control output"""
        self.recaptcha_event = recaptcha_event
        """Fire when we hit a recaptchaRequired"""
        self.disconnected_event = disconnected_event
        """Fire when we get a strangerDisconnected"""
        
    def gotMessage(self,chat,var):
        #Print every message received
        for msg in var:
            if self.print_messages: print "[%s] Stranger: %s"%(chat.id, msg)
        #If it's the first message, raise an exception and set a flag
        if self.start_event.is_set() == False:
            self.start_event.set()
            
    def typing(self, chat, var):
        #If he's typing, he's there
        if self.start_event.is_set() == False:
            self.start_event.set()
                
    def strangerDisconnected(self, chat, var):
        """Fires when stranger disconnects.
        """
        if self.print_messages: print "[%s] Stranger disconnected."%chat.id
        self.disconnected_event.set()
        
    def connected(self, chat, var):
        if self.print_messages: print "[%s] Stranger connected."%chat.id     
        
    def recaptchaRequired(self, chat, var):
        self.recaptcha_event.set()
        self.chat_thread.stop()
        
    #Events to ignore
    def count(self, chat, var):
        return
    def stoppedTyping(self, chat, var):
        return
    def waiting(self, chat, var):
        return
        
    def defaultEvent(self, event, chat, var):
        """Fires when an unexpected event occurs."""
        if DEBUG:
            try:
                if var is None:
                    arg = None
                elif len(var) > 1:
                    arg = str(var)
                elif len(var) == 1:
                    arg = var[0]
                elif len(var) < 1:
                    arg = None
            except TypeError:
                arg = str(var)
            if arg is not None:
                arg = ": " + str(arg)
            else:
                arg = ""
            if self.print_messages: print "Unhandled event %s [%s]"%(event, chat.id) + arg
            
class ScriptThread(threading.Thread):
    
    """Read a script over and over again"""
    
    def __init__(self, script, recaptcha_event, print_convo=True, logstr=""):
        """Make a conversation and wait for the stranger to say something.
        
        @param script: Script to send to Omegle
        @type script: String
        @param recaptcha_event: Set when a recaptcha is requested.
        @type recaptcha_event: threading.Event
        @param print_convo: Turn output on or off
        @type print_convo: Boolean
        @param logstr: String to use in server logs
        @type logstr: String
        """
        threading.Thread.__init__(self)
        self.daemon = True
        #Daemonize
        self.start_event = threading.Event()
        """Fire when the stranger has started chatting."""
        self.disconnected = threading.Event()
        """Set when stranger disconnects."""
        self.chat = Omegle.OmegleChat(debug=DEBUG, _id=None)
        """The chat to which to send messages"""
        self.chat.keystrokeDelay = KEYSTROKEDELAY
        handler = HwEventHandler(self.start_event, self, 
                                 print_messages=print_convo, 
                                 disconnected_event=self.disconnected,
                                 recaptcha_event=recaptcha_event)
        self.chat.connect_events(handler)
        self._stop = threading.Event() 
        self.script = script
        """Script to read to Omegle"""
        self.print_convo = print_convo
        """True if the convo is to be printed to stdout"""
        #Fire when convo is done
        self.recaptcha_event = recaptcha_event
        """Set if a recaptcha is required"""
        self.logstr = logstr
        """String to use in server logs"""
    
    def run(self):
        """Send a sequence of messages to the stranger when he's ready."""
        #Main thread loop
        while self._stop.is_set() is False:
            if self.print_convo: print "Starting a conversation."
            #Start the chat
            self.disconnected.clear()
            self.start_event.clear()
            if self.chat.connect(reconnect = True) is False:
                if DEBUG: print "Could not start chat"
                return

            #Wait for him
            self.start_event.wait(BOREDOM_TOL)
            if self._stop.is_set():
                if DEBUG: print "Return due to stop"
                return
            
            #Check if we actually started
            if self.start_event.is_set() is False:
                #Got bored
                if self.print_convo: 
                    print"[%s] Stranger took too long."%self.chat.id
                    server_log("gotbored", value=self.logstr)
                if self.disconnected.is_set() is False:
                    if DEBUG: print "Disconnecting."
                    self.chat.disconnect()
                    if self.print_convo: print "[%s] Spambot disconnected."%self.chat.id
                    self.disconnected.set()
                if self.print_convo: print "Conversation terminated.\n"
                #Don't bother with the rest.
                continue
          
            if self._is_stopped():
                break
                
            server_log("startchat", value=self.logstr)
            #Start sending lines
            for line in self.script:
            #Don't bother if we've stopped
                if self._stop.is_set() or self.disconnected.is_set():
                    break
                if isinstance(line, basestring):
                    self.chat.say(line)
                    #The stranger might disconnect while we're typing
                    if self._stop.is_set() or self.disconnected.is_set():
                        break
                    if self.print_convo: print "[%s] Spambot: %s"%(self.chat.id, line)
                elif isinstance(line,Number):
                    if DEBUG: print "Wating %s seconds"%str(line)
                    sleep(line)
                    
            #If we've been stopped, stop
            if self._stop.is_set():
                break
            
            #Don't disconnect for a while
            if self.disconnected.is_set() is False:
                if self.print_convo: print "[%s] Finished.  Giving stranger %d seconds for last words."%(self.chat.id, FINISHDELAY)
            self.disconnected.wait(FINISHDELAY)
            if self.disconnected.is_set() is False:
                if self.print_convo: print "[%s] Spambot disconnected."%self.chat.id
                try:
                    self.chat.disconnect()
                except urllib2.HTTPError:
                    if DEBUG: print "Caught HTTP Error on disconnect."
                server_log("selfdisconnet", value=self.logstr)  
            print "Conversation terminated.\n"      

        return
    
    def stranger_disconnected(self):
        """Inform the thread the stranger disconnected."""
        self.disconnected.set()

    def stop(self):
        """Stop the thread and end the convo."""
        self._stop.set()
        
    def _is_stopped(self):
        """Check if thread is stopped."""
        return self._stop.isSet()
    
    def _wait_for_stop(self, delay=None):
        self._stop.wait(delay)

def main():
    """Launch the spambot"""
    server_log("launch", VERSION)
    
    #If we're running silent, be silent
    if RUN_SILENT:
        sys.stdout = file(os.devnull, "a")

    #Gets set when a recaptcha is required
    recaptcha_event = threading.Event()

    #Make the conversation(s)
    threads = []
    my_thread = ScriptThread(get_my_script(), 
                            recaptcha_event=recaptcha_event, 
                            print_convo=ONLY_MINE)
    my_thread.start()
    threads.append(my_thread)

    
    #First check the version of the spambot if it's for someone else
    #Don't bother if we're running silent
    if not (ONLY_MINE or RUN_SILENT):
        try:
            version = urlopen(VERSION_URL).read()
            if VERSION != version:
                server_log("versionmismatch", VERSION)
                print "You have an outdated version.  Please download a new one " + \
                      "from %s.\nHit [Enter] to terminate this program."%UPDATE_URL
                import webbrowser
                webbrowser.open_new(UPDATE_URL)
                if not RUN_SILENT:
                    raw_input()
                return
        except Exception:
            pass

        (script_his, service, asl) = get_his_script()
        his_thread = ScriptThread(script_his, 
                                 recaptcha_event=recaptcha_event, 
                                 print_convo=True,
                                 logstr="%s-%s"%(service, asl))
        his_thread.start()
        threads.append(his_thread)

    while len(threads) > 0:
        try:
            # Join all threads using a timeout so it doesn't block
            # Filter out threads which have been joined or are None
            for t in threads:
                if t is not None and t.is_alive():
                    t.join(1)
                    if t.is_alive() is False:
                        threads.remove(t)
        except KeyboardInterrupt:
            print "Ctrl-c received! Sending kill to threads..."
            return
            for t in threads:
                t.stop()

    
    #Check for a captcha.  At the moment, if this isn't set, there's a problem.
    if recaptcha_event.is_set(): 
        if not ONLY_MINE: server_log("Recaptcha", value="%s-%s"%(service, asl))
        print "Omegle has detected spam.  Please press [Enter]."
        if not RUN_SILENT:
            raw_input()
    return

        
def server_log(action, value=""):
    """Log an action to the server.
    Does not log messages if ONLY_MINE is True.
    
    @param action: The action to be logged
    @type action: String
    @param value: An optional argument to the action
    @type value: String
    """
    if ONLY_MINE: return
    urlopen(LOG_URL+"?action="+str(action)+"&value="+value)
    return

def get_his_script():
    return srscript.make_his(run_silent=RUN_SILENT)

def get_my_script():
    return srscript.make_mine()
    
if __name__ == '__main__':
    main()
