import cookielib
import simplejson
import threading
import time
import urllib
import urllib2

#TODO: make debug a function pointer -> debug(chat, str), True for some
#default or False for quietness

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.11 Safari/535.19"
"""Bogus user agent.  *May* be somethnig omegle uses for bot detection."""

class EventHandler(object):
    def fire(self,event,chat,var):
        ''' Callback class. Var is info relating to the event.
        If a subclass defines a method defaultEvent, it will be called as defaultEvent(event, chat, var) if no event handler is found for an event.
        '''
        if hasattr(self,event):
            getattr(self,event)(chat,var)
            return
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
    
class ProxyException(Exception):
    """Exception raised when proxy doesn't mask our IP address."""
    def __init__(self, proxy, own_ip):
        """
        Initialize exception
        proxy: What was used as a proxy
        our_ip: Our IP and the IP as seen through the proxy.
        """
        self.proxy=proxy
        self.own_ip=own_ip
    def __str__(self):
        """Turn the exception into a string."""
        return "Own IP address %s found using proxy %s."%(self.own_ip, 
                                                          self.proxy)
            

class OmegleChat(object):
    def __init__(self, _id=None, debug=False, keystrokedelay=0, proxy=None):
        """Make a chat.
        @param _id: ID For the chat
        @type _id: String
        @param debug: Print debugging messages
        @type debug: Boolean
        @param keystrokedelay: Delay for each keystroke when say()ing
        @type keystrokedelay: Number
        @param proxy: A proxy through which to connect
        @type proxy: String
        """
        self.url = "http://cardassia.omegle.com/"
        self.id = _id
        self.connected = False
        self.handlers = []
        self.terminated = threading.Event()
        """Set when chat is terminated"""
        self.connected = False
        """True while we're connected"""
        self.keystrokeDelay = keystrokedelay
        """Delay for each keystroke when say()ing.  
        Set this to 0 do disable.  
        If nonzero, the appropriate typing events will be sent."""
        self.debug = debug

        jar = cookielib.CookieJar()
        processor = urllib2.HTTPCookieProcessor(jar)
        if proxy is not None: #Include a proxy if we want
            #Proxy code stolen from kd5pbo's pyproxyfinder
            #https://code.google.com/p/pyproxyfinder/
            proxy_handler = urllib2.ProxyHandler({"http": proxy})
            self.connector = urllib2.build_opener(proxy_handler, processor)
            #Make sure we're using a proxy
            own_ip = urllib2.urlopen(
                "http://api.externalip.net/ip/").read().strip() 
            proxied_ip = urllib2.urlopen(
                "http://api.externalip.net/ip/").read().strip()
            if own_ip == proxied_ip:
                raise ProxyException(proxy, own_ip)
        else:
            self.connector = urllib2.build_opener(processor)
        self.connector.addheaders = [
            ('User-agent',user_agent)
            ]
        #Connect default events
        self.connect_events(_DefaultHandler())

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

    def open_page(self,page,data={}):
        data['id'] = self.id
        try:
            url = self.url+page
            encdata = urllib.urlencode(data)
            #Don't generate an error
            if self.terminated.is_set():
                if self.debug: print "Conversation has terminated."
                return
            r = self.connector.open(url,encdata).read()
        except urllib2.HTTPError as e:
            if self.debug:
                print "HTTP Error: " + str(e)
                print "URL: " + str(url)
                print "Data: " + str(data)
                print "Terminated: " + str(self.terminated.is_set())
                raise
            r = ""
        if not r == "win":
            # Maybe make it except here?
            if self.debug: print 'Page %s returned %s'%(page,r)
        return r

    def say(self,message):
        ''' Send a message from the chat '''
        if self.keystrokeDelay > 0:
            if self.debug: print "Typing message: %s"%message
            self.typing()
            time.sleep(len(message) * self.keystrokeDelay)
        if self.debug: print 'Saying message: %s'%message
        self.open_page('send',{'msg':message})

    def typing(self):
        ''' Tell the stranger we are typing '''
        self.open_page('typing')

    def stoppedTyping(self):
        ''' Tell the stranger we are no longer typing '''
        self.open_page('stoppedtyping')
        
    def disconnect(self):
        ''' Close the chat '''
        if self.connected:
            self.terminated.set()
            self.open_page('disconnect',{})
            self.reactor.kill()
            self.id = None 
            self.connected = False
            if self.reactor.is_alive():
                self.reactor.kill()
                self.reactor.join()


    def connect(self, reconnect=True):
        ''' Start a chat session.
        @param reconnect: Reconnect if we've disconnected
        @type reconnect: True
        @return: The Chat ID as a string or False on failure
        '''
        #Don't reconnect if we're not meant to
        if self.connected and not reconnect:
            return
        #Disconnect thoroughly
        if reconnect:
            self.disconnect()
        #Warn us if we already have an ID
        if self.id and self.debug: 
            print "HAVE ID: " + self.id
        if self.id is None:
            try:
                page = self.connector.open(self.url+'start')
                text = page.read()
            except urllib2.HTTPError as e:
                if self.debug:
                    print "ERROR Connecting"
                    print str(e)
                return False
            self.id = text.strip('"')
            if self.debug: print "Got ID: " + self.id
            self.terminated.clear()
            self.connected = True
            self.reactor = _ReactorThread(self)
            self.reactor.start()
            return self.id

    def waitForTerminate(self):
        ''' This only returns when .disconnect() or .terminate() is called '''
        self.terminated.wait()
        
class _DefaultHandler(EventHandler):
    def strangerDisconnected(self,chat,var):
        chat.terminated.set()
    def defaultEvent(self,event,chat,var):
        return

class _ReactorThread(threading.Thread):
    def __init__(self, chat):
        threading.Thread.__init__(self)
        self.chat = chat
        self._stop = threading.Event()
        return
    
    def run(self):
        while self._stop.is_set() is False:
            if self.chat.terminated.is_set():
                if self.chat.debug: print "Thread terminating"
                return
            events = self.chat.get_events(json=True)
            if not events: continue
            if self.chat.debug: print events
            if self.chat.terminated.is_set(): return
            for event in events:
                if len(event) > 1:
                    self.chat.fire(event[0], event[1:])
                else:
                    self.chat.fire(event[0], None)
    
    def kill(self):
        self._stop.set()
            