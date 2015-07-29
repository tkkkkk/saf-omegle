# Introduction #
This page documents the events that come from Omegle's servers and which may be processed by the event handler.  They should be handled with a function of the form `handler(self, chat, var)` where `handler` is the name of the function, `chat` is the `Omegle.OmegleChat` object that sent the event (and to which the handler is attached), and `var` is a list of supporting data.  The handler should be named the **Event Name** in the below table.

# Table of Events #
This list will grow as I see more events.
| **Event Name** | **`var`** | **Meaning** |
|:---------------|:----------|:------------|
| `connected`    | None      | The stranger has connected |
| `count`        | int       | The "strangers online" number |
| `gotMessage`   | str       | A message has been received |
| `recaptchaRequired` | str       | A key for a recaptcha required to use Omegle |
| `stoppedTyping` | None      | The stranger has stopped typing |
| `strangerDisconnected` | None      | The stranger has disconnected |
| `typing`       | None      | The stranger is typing |
| `waiting`      | None      | Waiting for a stranger |