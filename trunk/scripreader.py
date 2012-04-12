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

AUTO_RUN = False
"""Run in background.  Ssshh."""

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

VERSION = "46"
"""Version of the software"""
VERSION_URL = base_url + "/version"
"""URL to get the version from"""

UPDATE_URL = base_url
"""Where to download a new version"""


class HwEventHandler(Omegle.EventHandler):
    
    """Event handler to be given to the chats"""
    
    #Class variables
    
    def __init__(self, start_event, chat_thread, recaptcha_event=None, print_messages=True):
        
        """Initialize event handler.
        
        @param start_event: Event to notify others when conversation starts
        @type start_event: threading.Event
        @param recaptcha_event: Event to set if a recaptcha is required
        @type recaptcha_event: threading.Event
        @param chat_thread: Thread controlling the chat
        @type chat_thread: threading.Thread
        @param print_messages: Allow normal output
        @type print_messages: Boolean
        """
        
        self.got_first_msg = False
        """True if the stranger has sent a message."""
        self.start_event = start_event
        """Event to notify others when conversation starts"""
        self.chat_thread = chat_thread
        """Thread controlling the chat"""
        self.print_messages = print_messages
        """Control output"""
        self.recaptcha_event = recaptcha_event
        
    def gotMessage(self,chat,var):
        #Print every message received
        for msg in var:
            if self.print_messages: print "[%s] Stranger: %s"%(chat.id, msg)
        #If it's the first message, raise an exception and set a flag
        if self.got_first_msg == False:
            self.got_first_msg = True
            self.start_event.set()
            
    def typing(self, chat, var):
        #If he's typing, he's there
        if self.got_first_msg == False:
            self.got_first_msg = True
            self.start_event.set()
        if DEBUG:
            self.defaultEvent("typing", chat, var)
                
    def strangerDisconnected(self, chat, var):
        """Fires when stranger disconnects.
        """
        if self.print_messages: print "[%s] Stranger disconnected."%chat.id
        #Don't ask for more events
        chat.terminate()
        #Stop the thread (ish)
        self.chat_thread.stop()
        
    def connected(self, chat, var):
        if self.print_messages: print "[%s] Stranger connected."%chat.id     
        
    def recaptchaRequired(self, chat, var):
        if self.recaptcha_event: self.recaptcha_event.set()
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
            
class ConvoThread(threading.Thread):
    
    """A single conversation with a stranger"""
    
    def __init__(self, script, recaptcha_event=None, print_convo=True):
        """Make a conversation and wait for the stranger to say something.
        
        @param script: Script to send to Omegle
        @type script: String
        @param finished_event: Event that fires when the convo is done
        @type finished_event: threading.Event
        @param print_convo: Turn output on or off
        @type print_convo: Boolean
        """
        threading.Thread.__init__(self)
        self.chat = Omegle.OmegleChat(debug=DEBUG, _id=None)
        """The chat to which to send messages"""
        self.start_event = threading.Event()
        """Fire when the stranger has started chatting."""
        self.chat.keystrokeDelay = KEYSTROKEDELAY
        handler = HwEventHandler(self.start_event, self, 
                                 print_messages=print_convo, 
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
    
    def run(self):
        """Send a sequence of messages to the stranger when he's ready."""
        #Main thread loop
        while self._stop.is_set() is False:
            if self.print_convo: print "Starting a conversation."
            #Start the chat
            self.chat.connect(reconnect = True)

            #Wait for him
            self.start_event.wait(BOREDOM_TOL)
            #Check if we actually started
            if not self.start_event.is_set():
                #Got bored
                if self.print_convo: 
                    print"[%s] Stranger took too long."%self.chat.id
                    server_log("gotbored")
                if self._is_stopped() is False:
                    if DEBUG: print "Disconnecting."
                    self.chat.disconnect()
                if self.print_convo: print "Conversation Terminated."
                continue
          
            if self._is_stopped():
                continue
                
            server_log("startchat")
            #Start sending lines
            for line in self.script:
            #Don't bother if we've stopped
                if self._is_stopped():
                    break
                if isinstance(line, basestring):
                    if self.print_convo: print "[%s] Spambot: %s"%(self.chat.id, line)
                    self.chat.say(line)
                elif isinstance(line,Number):
                    if DEBUG: print "Wating %s seconds"%str(line)
                    sleep(line)
            
            #Don't disconnect for a while
            self._wait_for_stop(FINISHDELAY)
            if not self._is_stopped():
                if self.print_convo: print "[%s] Spambot disconnected."%self.chat.id
                self.stop()
        
        #Fire the event and exit
        if self.finished_event: self.finished_event.set()
        if self.print_convo: print "Conversation Terminated."
        return

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
    
    """If we're realling running silent, be silent"""
    if RUN_SILENT:
        sys.stdout = file(os.devnull, "a")
    
        #First check the version of the spambot
    if not ONLY_MINE:
        try:
            version = urlopen(VERSION_URL).read()
            if VERSION != version:
                print "You have an outdated version.  Please download a new one " + \
                      "from %s.\nHit [Enter] to terminate this program."%UPDATE_URL
                raw_input()
                return
        except Exception:
            pass

    #Thread pool
    #[(Thread, service, asl)]
    threads = []    
    #Gets set when someone is done
    finished_event = threading.Event()  
    #Gets set when a recaptcha is required
    recaptcha_event = threading.Event()
    #Make a thread for my script
    
    threads.append((ConvoThread(get_my_script(), 
                                finished_event=finished_event, 
                                recaptcha_event=recaptcha_event, 
                                print_convo=ONLY_MINE), 
                    "Omegle", "SCRIPT_MINE"))
    #Make a thread for him
    if not ONLY_MINE:
        (script_his, service, asl) = get_his_script()
        threads.append((ConvoThread(script_his, 
                                    finished_event=finished_event, 
                                    recaptcha_event=recaptcha_event, 
                                    print_convo=True), 
                        service, asl))
    
    #Main program loop
    for thread in threads:
        thread[0].start()
    while recaptcha_event.is_set() is False:
        #Clear if we need to restart a thread
        if finished_event.is_set(): finished_event.clear()
        print "1" + str(threads[0][0])
        if threads[0][0].is_alive() is False:
            print "2" + str(threads[0][0])
            threads[0][0].join()
            print "2" + str(threads[0][0])
            threads[0][0].start()
        for thread in threads[1:]:
            if thread[0].is_alive() is False:
                server_log("start", value="%s-%s"%())
                thread[0].start()
        recaptcha_event.wait()
    server_log("Recaptcha")
    print "Omegle has detected spam.  Please press [Enter]."
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
    return srscript.make_his(silent=RUN_SILENT)

def get_my_script():
    return srscript.make_mine()
    
if __name__ == '__main__':
    main()
