#!/usr/bin/env python

'''
Created on Mar 22, 2012

@author: stuart
'''

from numbers import Number
from time import sleep

import Omegle
import threading

global ANTISPAMDELAY
global BOREDOM_TOL
global DEBUG
global FINISHDELAY
global KEYSTROKEDELAY
global RECAPTCHA_REQUIRED
global SCRIPT

ANTISPAMDELAY = 10
"""Delay in between chats"""

BOREDOM_TOL = 10
"""Give up after this many seconds if the other person hasn't started talking."""

DEBUG = False
"""Print debug messages if True"""

FINISHDELAY = 30

KEYSTROKEDELAY = 0.5
"""Time it takes to tap a key"""

RECAPTCHA_REQUIRED = threading.Event()
"""Set if recaptcha required.  If this is true the program exits."""

SCRIPT = ["hi",
          2,
          "brb",
          15,
          "ok back",
          2,
          "18 f usa",
          "wanna trade pix?",
          5,
          "heres mine: http://goo.gl/nr5qz",
          2,
          "u like it?",
          15,
          "So, actually I'm a dude writing a bot.",
          4,
          "Basically, a bot is a program that talks to people on omegle.",
          "Also, I can custom-make bots for you.",
          "Interested?  omegleuser {dot} 22334 {at} gmail {dot} com "
          "(also, works for MSN).",
          "With my bot, I have gotten thousands of people to go to that site.",
          "Wanna know how good I am?  This whole time you've been talking to "
          "one of my bots.",
          ]
"""Conversation script as a list.
Each list element is either a message to send or a pause.
If the element is a string (ascii or unicode) it will be sent as a message.
If the message is a number, it is interpreted as a time in seconds to wait before sending the next message
"""

class HwEventHandler(Omegle.EventHandler):
    
    """Event handler to be given to the chats"""
    
    #Class variables
    
    def __init__(self, start_event, chat_thread):
        
        """Initialize event handler.
        
        @param start_event: Event to notify others when conversation starts
        @type start_event: threading.Event
        @param chat_thread: Thread controlling the chat
        @type chat_thread: threading.Thread
        """
        
        self.got_first_msg = False
        """True if the stranger has sent a message."""
        self.start_event = start_event
        """Event to notify others when conversation starts"""
        self.chat_thread = chat_thread
        """Thread controlling the chat"""
        
    def gotMessage(self,chat,var):
        #Print every message received
        for msg in var:
            print "[%s] Stranger: %s"%(chat.id, msg)
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
        print "[%s] Stranger disconnected."%chat.id
        #Don't ask for more events
        chat.terminate()
        #Stop the thread (ish)
        self.chat_thread.stop()
        
    def connected(self, chat, var):
        print "[%s] Stranger connected."%chat.id     
        
    def recaptchaRequired(self, chat, var):
        RECAPTCHA_REQUIRED.set()
        
    #Events to ignore
    def count(self, chat, var):
        return
    def stoppedTyping(self, chat, var):
        return
    def waiting(self, chat, var):
        return
        
    def defaultEvent(self, event, chat, var):
        """Fires when an unexpected event occurs."""
        if DEBUG or "DEBUG":
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
            print "Unhandled event %s [%s]"%(event, chat.id) + arg
            
class ConvoThread(threading.Thread):
    
    """A single conversation with a stranger"""
    
    def __init__(self):
        """Make a conversation and wait for the stranger to say something."""
        threading.Thread.__init__(self)
        self.chat = Omegle.OmegleChat(debug=DEBUG, _id=None)
        """The chat to which to send messages"""
        self.start_event = threading.Event()
        """Fire when the stranger has started chatting."""
        self.chat.keystrokeDelay = KEYSTROKEDELAY
        handler = HwEventHandler(self.start_event, self)
        self.chat.connect_events(handler)
        self._stop = threading.Event() 
    
    def run(self):
        """Send a sequence of messages to the stranger when he's ready."""
        #Start the chat
        self.chat.connect()
        #Wait for him
        self.start_event.wait(BOREDOM_TOL)
        #Check if we actually started
        if not self.start_event.is_set():
            #Got bored
            if DEBUG: print"Got bored."
            if self._is_stopped():
                return
            else:
                if DEBUG: print "Disconnecting"
                self.chat.disconnect()
            return
        #Start sending lines
        for line in SCRIPT:
        #Don't bother if we've stopped
            if self._is_stopped():
                return
            if isinstance(line, basestring):
                print "[%s] Spambot: %s"%(self.chat.id, line)
                self.chat.say(line)
            elif isinstance(line,Number):
                if DEBUG: print "Wating %s seconds"%str(line)
                sleep(line)
        #Don't disconnect for a while
        self._wait_for_stop(FINISHDELAY)
        if not self._is_stopped():
            self.chat.disconnect()
            self.stop()

    def stop(self):
        """Stop the thread and end the convo."""
        self._stop.set()
        
    def _is_stopped(self):
        """Check if thread is stopped."""
        return self._stop.isSet()
    
    def _wait_for_stop(self, delay=None):
        self._stop.wait(delay)
        
class InputThread(threading.Thread):
    """Takes input and sends it to the current chat."""
    
    def __init__(self, chat):
        """Makes an input thread for a chat
        @param chat: The chat for which to make the thread
        @type chat: ConvoThread
        """
    
    def run(self):
        #Get a line of input
        while True:
            line = raw_input()
            

if __name__ == '__main__':
    #Main program loop
    while RECAPTCHA_REQUIRED.is_set() is False:
        print "Starting a conversation."
        #Make a chat
        chat = ConvoThread()
        #Start it
        chat.start()
        #Wait for it to end
        chat.join()
        #Bummer
        if RECAPTCHA_REQUIRED.is_set() is True:
            print "Recaptcha required.\n"
        else:
            print"Conversation terminated.\n"
        #Don't spam (heh)
        sleep(ANTISPAMDELAY) 
