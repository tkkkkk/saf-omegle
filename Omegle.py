import urllib
import urllib2
import thread
import simplejson
import cookielib
import time

user_agent = "Mozilla/5.1 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.4"
"""Bogus user agent.  *May* be somethnig omegle uses for bot detection."""

class EventHandler:
    def fire(self,event,chat,var):
        ''' Callback class. Var is info relating to the event.
        If a subclass defines a method defaultEvent, it will be called as defaultEvent(event, chat, var) if no event handler is found for an event.
        '''
        if hasattr(self,event):
            getattr(self,event)(chat,var)
        elif hasattr(self, "defaultEvent"):
            getattr(self, "defaultEvent")(event,chat,var)
        else:
            raise UnknownEventException(event, chat, var)
            
class UnknownEventException(Exception):
    
    """Exception to be raised when an unknown event happens."""
    
    def __init__(self, event, chat, var):
        """Initialize the exception.
        
        @param event: The unhandled event
        @type event:  str
        @param chat:  The chat which generated the event
        @type chat:   OmegleChat
        @param var:   A list of variables associated with the event
        @type var:    list
        """
        self.event = event
        """The unhandled event"""
        self.chat = chat
        """The chat that generated the event"""
        self.var = var
        """Variables associated with the event"""
        
    def __str__(self):
        """Generate a string describing the unhandled event"""
        return "%s [%s]: "%(self.event, self.chat.id) + str(self.var)
            

class OmegleChat:
    def __init__(self,_id=None,debug=False):
        self.url = "http://cardassia.omegle.com/"
        self.id = _id
        self.failed = False
        self.connected = False
        self.in_chat = False
        self.handlers = []
        self.terminated = False
        self.keystrokeDelay = 0
        """Delay for each keystroke when say()ing.  Set this to 0 do disable.  If nonzero, the appropriate typing events will be sent."""
        self.debug = debug

        jar = cookielib.CookieJar()
        processor = urllib2.HTTPCookieProcessor(jar)
        self.connector = urllib2.build_opener(processor)#,urllib2.HTTPHandler(debuglevel=1))
        self.connector.addheaders = [
            ('User-agent',user_agent)
            ]
        
        

    def pausedChat(self,chat,message,pause):
        ''' Make it look like the bot is typing something '''
        self.typing()
        time.sleep(pause)
        self.stoppedTyping()
        self.say(message)

    def get_events(self,json=False):
        ''' Poll the /events/ page and process the response '''
        #requester = urllib2.Request(self.url+'events',headers={'id':self.id})
        events = self.connector.open(self.url+'events',data=urllib.urlencode({'id':self.id})).read()
        if json:
            return simplejson.loads(events)
        else:
            return events

    def connect_events(self, event_handler):
        ''' Add an event handler '''
        self.handlers.append(event_handler)

    def fire(self,event,var):
        for handler in self.handlers:
            handler.fire(event,self,var)

    def terminate(self):
        ''' Terminate the thread. Don't call directly, use .disconnect() instead '''
        self.terminated = True

    def open_page(self,page,data={}):
        if self.terminated:
            return
        data['id'] = self.id
        try:
            url = self.url+page
            encdata = urllib.urlencode(data)
            r = self.connector.open(url,encdata).read()
        except urllib2.HTTPError as e:
            if self.debug:
                print "HTTP Error: " + str(e)
                print "URL: " + str(url)
                print "Data: " + str(data)
                raise
            r = ""
        if not r == "win":
            # Maybe make it except here?
            if self.debug: print 'Page %s returned %s'%(page,r)
        return r

    def say(self,message):
        ''' Send a message from the chat '''
        if self.keystrokeDelay > 0 and not self.terminated:
            if self.debug: print "Typing message: %s"%message
            self.typing()
            time.sleep(len(message) * self.keystrokeDelay)
        if not self.terminated:
            if self.debug: print 'Saying message: %s'%message
            self.open_page('send',{'msg':message})

    def disconnect(self):
        ''' Close the chat '''
        self.open_page('disconnect',{})
        self.terminate()

    def typing(self):
        ''' Tell the stranger we are typing '''
        self.open_page('typing')

    def stoppedTyping(self):
        ''' Tell the stranger we are no longer typing '''
        self.open_page('stoppedtyping')

    def connect(self,threaded=True):
        ''' Start a chat session'''
        if self.id: 
            if self.debug: print "HAVE ID: " + self.id
        elif not self.id:
            page = self.connector.open(self.url+'start')
            text = page.read()
            self.id = text.strip('"')
            if self.debug: print "Got ID: " + self.id
        self.connected = True
        if threaded:
            thread.start_new_thread(self.reactor,())
        else:
            self.reactor()

    def waitForTerminate(self):
        ''' This only returns when .disconnect() or .terminate() is called '''
        while not self.terminated:
            time.sleep(0.1)
            pass
        return

    def reactor(self):
        while True:
            if self.terminated:
                if self.debug: print "Thread terminating"
                return

            events = self.get_events(json=True)
            if not events:
                continue
            if self.debug: print events
            if self.terminated:
                return
            for event in events:
                if len(event) > 1:
                    self.fire(event[0],event[1:])
                else:
                    self.fire(event[0],None)
