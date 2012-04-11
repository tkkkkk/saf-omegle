#!/usr/bin/env python

'''
Created on Mar 22, 2012

@author: stuart
'''

from numbers import Number
from time import sleep
from urllib import urlopen

import Omegle
import threading

global ANTISPAMDELAY
global BOREDOM_TOL
global DEBUG
global FINISHDELAY
global KEYSTROKEDELAY
global LOG_URL
global ONLY_MINE
global RECAPTCHA_REQUIRED
global SCRIPT_MINE
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
          "http://goo.gl/TvEPP",
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
          "You can also head to that site for more info (http://goo.gl/TvEPP)",
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

SCRIPT_MINE = ["hi brb",
               5,
               "ok back",
               "18 f usa",
               2,
               "im horny",
               "r u?",
               3,
               "want 2 c me?",
               8,
               "ok heres my pic",
               "http://goo.gl/KpG8H",
               2,
               "u like it?",
               10,
               "So, actually I'm a programmer.",
               "My program gets girls to come to you.",
               "Want it?",
               10,
               "You can find it at http://goo.gl/W6crl",
               20,
               "You can email me: omegleuser {dot} 22334 {at} gmail {dot} com "
               "(also my MSN Messenger ID).",
               "My skype name is the same without the @gmail.com bit.",
               "You'll have to replace the ' {dot} ' with a . "
               "and the ' {at} ' with a @",
               "Feel free to contact me.",
               "I can also write you your own custom program.",
               "One last thing, I'm a dude :) (and a good programmer).",
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
    
    def __init__(self, start_event, chat_thread, print_messages=True):
        
        """Initialize event handler.
        
        @param start_event: Event to notify others when conversation starts
        @type start_event: threading.Event
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
        RECAPTCHA_REQUIRED.set()
#        chat.stop()
#        chat.start_event.set()
        
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
    
    def __init__(self, script, finished_event, print_convo=True):
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
        handler = HwEventHandler(self.start_event, self, print_convo)
        self.chat.connect_events(handler)
        self._stop = threading.Event() 
        self.script = script
        """Script to read to Omegle"""
        self.print_convo = print_convo
        """True if the convo is to be printed to stdout"""
        #Fire when convo is done
        self.finished_event = finished_event
    
    def run(self):
        """Send a sequence of messages to the stranger when he's ready."""
        #Start the chat
        self.chat.connect()
        #Wait for him
        self.start_event.wait(BOREDOM_TOL)
        #Check if we actually started
        if not self.start_event.is_set():
            #Got bored
            if self.print_convo: 
                print"[%s] Got bored."%self.chat.id
                print"[%s] Stranger took too long"%self.chat.id
            if self._is_stopped():
                return
            else:
                if DEBUG: print "Disconnecting"
                self.chat.disconnect()
            return
            self.stop()
        if not self._is_stopped():
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
            self.chat.disconnect()
            if self.print_convo: print "[%s] Spambot disconnected."%self.chat.id
            self.stop()
        
        #Fire the event and exit
        self.finished_event.set()
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
    #Get set when someone is done
    finish_event = threading.Thread()  
    #Make a thread for my script
    threads.append(ConvoThread(SCRIPT_MINE, finish_event, print_convo=ONLY_MINE))
    #Make a thread for him
    if not ONLY_MINE:
        threads.append(ConvoThread(get_his_script(), finish_event, print_convo=True))
    
    #Main program loop
    while True:
        finish_event.wait(FINISHDELAY)
        for thread in threads[1:]:
            if thread.is_stopped():
                thread.start()
        

        
def main():
    """Launch the spambot""" 
    server_log("launch", VERSION)
    if ONLY_MINE is False:
        #Get info from the user about his spamming
        server_log("start", value="%s-%s"%(service_t[0], asl if asl else ""))
    #Main program loop
    my_chat = None
    while RECAPTCHA_REQUIRED.is_set() is False:
        if ONLY_MINE: print "Starting a conversation."
        #Make a chat if we don't have one
        if (my_chat is None) or (not my_chat.is_alive()):
            my_chat = ConvoThread(SCRIPT_MINE, print_convo=(not SCRIPT_HIS))
            #Start it
            my_chat.start()
        #Run his script while mine is alive
        while my_chat.is_alive() and (RECAPTCHA_REQUIRED.is_set() is False) and ONLY_MINE is False:
            print "Starting a conversation."
            his_chat = ConvoThread(SCRIPT_HIS)
            his_chat.start()
            his_chat.join()
            my_chat.join(ANTISPAMDELAY)
            if RECAPTCHA_REQUIRED.is_set() is True:
                print "Recaptcha required.\n"
            else:
                print"Conversation terminated.\n"
            RECAPTCHA_REQUIRED.wait(ANTISPAMDELAY)
        #Wait for it to end
        if ONLY_MINE:
            my_chat.join()
        else:
            if not my_chat.is_alive():
                my_chat.join()
            
        #Bummer
        if RECAPTCHA_REQUIRED.is_set() is True:
            if ONLY_MINE: print "Recaptcha required.\n"
        else:
            if ONLY_MINE: print"Conversation terminated.\n"
        #Don't spam (heh)
        RECAPTCHA_REQUIRED.wait(ANTISPAMDELAY)
    print "Omegle has detected spam.  Please press [Enter] to exit."
    server_log("recaptcha")
    raw_input()
        
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
    try:
        services = [("Skype", "ID"),
                    ("Yahoo Messenger", "ID"),
                    ("MSN Messenger", "ID"),
                    ("Facebook", "name")]
        print ""
        for i in range(len(services)):
            print "%i. %s"%(i+1, services[i][0])
        print ""
        service_s = raw_input("Type the number of the service you'd like other people to use to contact you: ")
        service_i = int(service_s)
        service_t = services[service_i-1]
        username = raw_input("What is the %s you use on %s that you want other people to use to contact you? "%(service_t[1], service_t[0]))
        if username == "":
            raise ValueError()
    except (ValueError, IndexError):
        service_t = ("Tinychat", "link")
        username = "http://tinychat.com/lgr5k"
    asl = raw_input("What is your asl? ")
    SCRIPT_HIS = ["hi",
                  "brb",
                  5,
                  "asl?",
                  4,
                  asl if asl else "I don't give my asl out on Omegle.",
                  2,
                  "Let's switch to %s.  It's much better."%service_t[0],
                  "My %s there is %s"%(service_t[1], username),
                  1,
                  "See you there, cutie ;)"]

    
if __name__ == '__main__':
    main()
