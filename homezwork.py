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
global SCRIPT_HIS
global SCRIPT_MINE

ANTISPAMDELAY = 10
"""Delay in between chats"""

BOREDOM_TOL = 10
"""Give up after this many seconds if the other person hasn't started talking."""

DEBUG = False
"""Print debug messages if True"""

FINISHDELAY = 30

KEYSTROKEDELAY = 0.3
"""Time it takes to tap a key"""

RECAPTCHA_REQUIRED = threading.Event()
"""Set if recaptcha required.  If this is true the program exits."""

SCRIPT_MINE = ["hi brb",
          10,
          "ok im here",
          "18 f usa",
          2,
          "im horny",
          "u have a pic?",
          5,
          "wanna see me?",
          10,
          "heres my pic",
          "http://goo.gl/EDGWL",
          2,
          "u like it?",
          15,
          "So, actually I'm a dude writing a bot.",
          4,
          "Basically, a bot is a program that talks to people on omegle.",
          "Also, I can custom-make bots for you.",
          "Interested?  omegleuser {dot} 22334 {at} gmail {dot} com "
          "(also my MSN Messenger ID).",
          "My skype name is the same without the @gmail.com bit.",
          "You'll have to replace the ' {dot} ' with a . "
          "and the ' {at} ' with a @",
          "Feel free to zap me a message",
          30,
          "Wow, you're still here?",
          "If you're just looking for someone to talk to, try Blurrypeople: "
          "http://goo.gl/100ZG",
          30,
          "Well, since you've been talking to a computer this whole time, "
          "how about a knock-knock joke?",
          "Knock, Knock.",
          5,
          "(Who's there?)",
          "Disco.",
          5,
          "(disco who?)",
          ]
"""Conversation script as a list.
Each list element is either a message to send or a pause.
If the element is a string it will be sent as a message.
If the message is a number, it is interpreted as a time in seconds to wait before sending the next message
"""

SCRIPT_HIS = ["Hi",
              1,
              "asl?",
              3,
              "18 f usa",
              "whats your email address?",
              ]

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
            print "Unhandled event %s [%s]"%(event, chat.id) + arg
            
class ConvoThread(threading.Thread):
    
    """A single conversation with a stranger"""
    
    def __init__(self, script, print_convo=True):
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
        self.script = script
        """Script to read to Omegle"""
        self.print_convo = print_convo
        """True if the convo is to be printed to stdout"""
    
    def run(self):
        """Send a sequence of messages to the stranger when he's ready."""
        #Start the chat
        self.chat.connect()
        #Wait for him
        self.start_event.wait(BOREDOM_TOL)
        #Check if we actually started
        if not self.start_event.is_set():
            #Got bored
            if self.print_convo: print"[%s] Got bored."%self.chat.id
            if self._is_stopped():
                return
            else:
                if DEBUG: print "Disconnecting"
                self.chat.disconnect()
            return
        #Start sending lines
        for line in self.script:
        #Don't bother if we've stopped
            if self._is_stopped():
                return
            if isinstance(line, basestring):
                if self.print_convo: print "[%s] Spambot: %s"%(self.chat.id, line)
                self.chat.say(line)
            elif isinstance(line,Number):
                if DEBUG: print "Wating %s seconds"%str(line)
                sleep(line)
        #Don't disconnect for a while
        self._wait_for_stop(FINISHDELAY)
        if not self._is_stopped():
            self.chat.disconnect()
            if self.print_convo: print "[%s] Spambot disconnected."%self.chat.id
            self.stop()

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
    #Main program loop
    while RECAPTCHA_REQUIRED.is_set() is False:
        print "Starting a conversation."
        #Make a chat
        my_chat = ConvoThread(SCRIPT_MINE)
        #Start it
        my_chat.start()
        #Run his script while mine is alive
        while my_chat.is_alive():
            if SCRIPT_HIS:
                his_chat = ConvoThread(SCRIPT_HIS)
                his_chat.start()
                his_chat.join()
        #Wait for it to end
        my_chat.join()
        #Bummer
        if RECAPTCHA_REQUIRED.is_set() is True:
            print "Recaptcha required.\n"
        else:
            print"Conversation terminated.\n"
        #Don't spam (heh)
        sleep(ANTISPAMDELAY) 

if __name__ == '__main__':
    main()