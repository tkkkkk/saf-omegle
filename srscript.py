import cPickle

global SCRIPT_MINE
#TODO: Download this eventually
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
               "im having fun",
               2,
               "r u horny",
               3,
               "want 2 c?",
               8,
               "http://goo.gl/gM7M0",
               2,
               "u like it?",
               10,
               "i thought it was cool",
               "what do u think?",
               30,
               "the end is the best part",
               300,
               "Wow, you're still here?",
               "If you're just looking for someone to talk to, try Blurrypeople: "
               "http://goo.gl/0p5JJ",
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


def make_his(run_silent):
    script = None
    if run_silent is False:
        try:
            services = [("Skype", "ID"),
                        ("Yahoo Messenger", "ID"),
                        ("MSN Messenger", "ID"),
                        ("Facebook", "name"),
                        ("Email", "address"),]
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
        asl = raw_input("How old are you? ")
        asl = asl + " " + raw_input("What is your gender? ")
        asl = asl + " " + raw_input("Where are you located? ") 
        asl = asl.strip() if asl.strip() else "I don't give my asl out on Omegle."
        #Tell the user that it'll run automatically.
        print "\nOk.  Now just sit back and watch."
        print "I'll do everything for you.\n"
    else: #Running silently
        service_t = ("Skype", "ID") #Assumption :(
        fail_script = ["hi brb", #Use this if something goes wrong
                       5,
                      "ok back",
                      "im using an app that should be getting me girls, "
                      "but I didn't tell it my skype username when it asked",
                      1,
                      "if you would like to try it, you can get it at "
                      "http://goo.gl/VstMM",
                      1,
                      "you can also find the skype id for the guy who wrote "
                      "this app on that page",
                      "if you ask nicely, he may write something for you"]

        import os
        #If we're using windows, try to get the script from a file
        if os.name == "nt":
            from win32com.shell import shell, shellcon
            path = shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0)
            path = os.path.join(path, "asys.exe")
            try: #Try to open the file and get the uname/asl
                f = open(path, "r")
                script = cPickle.load(f)
                f.close()
            except IOError: #Well, something went wrong
                return (fail_script, "win_fail", "")
            except cPickle.PickleError:
                return (fail_script, "pickle_fail", "")
        #Maybe in the future we can make a non-windows version
        else: #Not windows
            return (fail_script, "unknown_os", "")
            
    if script is None:
        script = ["hi",
                  "brb",
                  5,
                  "asl?",
                  4,
                  asl,
                  2,
                  "Let's switch to %s.  It's much better."%service_t[0],
                  "My %s is %s"%(service_t[1], username),
                  1,
                  "See you there."]

    return (script, service_t[0], asl)

def make_mine():
    return SCRIPT_MINE
