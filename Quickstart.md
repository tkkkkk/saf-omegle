# Introduction #

simpleomegle is a small python API to interact with the text side of the chat site Omegle.com.  It is a derivative of similar projects hosted on this site.

Without further ado, lets's jump into code.

## Make a Chat ##
The first task when writing code to interact with omegle is making a chat:
```python

import Omegle
my_chat = Omegle.OmegleChat()```
We now have an object representing an Omegle conversation.  This is analogous to loading omegle.com, but not starting a chat.

Before we can do that, though, we're going to have to set up handlers to handle events.
## Event Handlers ##
```python
class MyEventHandler(Omegle.EventHandler):
"""Event handler for the chat"""
def connected(self, chat, var):
"""Fire when the stranger connects."""
print "Stranger Connected"
#Say hello to him.
chat.say("Hello, Stranger!")
#Hang up
chat.disconnect()```
Here we've made a very small event handling class.  It only takes care of one event: connected.  This event fires when a stranger connects.  There are, of course, other [events](Events.md), a partial list of which can be found on the wiki page [Events](Events.md).

Every handler takes two arguments:<pre>chat: the instance of Omegle.OmegleChat that fired the event<br>
var: a list of data relevant to the event</pre>
Nearly always `var` will have 0 or 1 elements.

`print "Stranger Connected"` is debugging output for our own purposes.  Printing to stdout doesn't touch Omegle.

`chat.say("Hello, Stranger!")` sends a message, `Hello, Stranger!` to the chat that fired the event.

All that's left is to start the chat.
## Start the Chat ##
```python

my_chat.connect_events(MyEventHandler())
my_chat.connect()```This connects an instance of the event handler to the chat and starts the chat.

## All Together ##
When combined, our Hello, World! program is as follows:
```python

class MyEventHandler(Omegle.EventHandler):
"""Handle chat events"""

def __init__(self, finished_event):
"""Initialize event handler.

@param finished_event: Signals main thread the chat has finished
@type finished_event: threading.Event
"""
self.finished_event = finished_event

def connected(self, chat, var):
"""Stranger connected."""
print "Stranger connected."
#Say hello to him
chat.say("Hello, World!")
#Hang up
chat.disconnect()
#Signal main thread we're done
self.finished_event.set()

#Used to wait for chat to finish
finished_event = threading.Event()
#Create a new chat
my_chat = Omegle.OmegleChat()
#Connect handlers to the chat
my_chat.connect_events(MyEventHandler(finished_event))
#Connect the chat to omegle
my_chat.connect()
#Wait for the chat to finish
finished_event.wait()```
Note we've added the use of `threading.Event` to wait for the chat to finish.