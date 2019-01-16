#!/usr/bin/env python

"""
newton - a smart bot, like Siri, for Slack chat rooms.
Copyright (C) 2019  Andy Poo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License (LGPL) as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/> for a description of the LGPL.
"""

import re
import random
import time

debug = False

CREATOR_MATCH = "andy"
CREATOR_NAME = "Andy"


reflections = {
    "am": "are",
    "was": "were",
    "i": "you",
    "i'd": "you would",
    "id": "you would",
    "i've": "you have",
    "ive": "you have",
    "i'll": "you will",
    "ill": "you will",
    "my": "your",
    "are": "am",
    "you've": "I have",
    "youve": "I have",
    "you'll": "I will",
    "youll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you"
}

psychobabble = [
    [r'I need (.*)',
     ["Why do you need {0}?",
      "Would it really help you to get {0}?",
      "Are you sure you need {0}?"]],

    [r'Why don\'?t you ([^\?]*)\??',
     ["Do you really think I don't {0}?",
      "Perhaps eventually I will {0}.",
      "Do you really want me to {0}?"]],

    [r'Why can\'?t I ([^\?]*)\??',
     ["Do you think you should be able to {0}?",
      "If you could {0}, what would you do?",
      "I don't know -- why can't you {0}?",
      "Have you really tried?"]],

    [r'I can\'?t (.*)',
     ["How do you know you can't {0}?",
      "Perhaps you could {0} if you tried.",
      "What would it take for you to {0}?"]],

    [r'I am (.*)',
     ["Did you come to me because you are {0}?",
      "How long have you been {0}?",
      "How do you feel about being {0}?"]],

    [r'I\'?m (.*)',
     ["How does being {0} make you feel?",
      "Do you enjoy being {0}?",
      "Why do you tell me you're {0}?",
      "Why do you think you're {0}?"]],

    [r'Are you ([^\?]*)\??',
     ["Why does it matter whether I am {0}?",
      "Would you prefer it if I were not {0}?",
      "Perhaps you believe I am {0}.",
      "I may be {0} -- what do you think?"]],

    [r'What (.*)',
     ["Why do you ask?",
      "How would an answer to that help you?",
      "What do you think?"]],

    [r'How (.*)',
     ["How do you suppose?",
      "Perhaps you can answer your own question.",
      "What is it you're really asking?"]],

    [r'Because (.*)',
     ["Is that the real reason?",
      "What other reasons come to mind?",
      "Does that reason apply to anything else?",
      "If {0}, what else must be true?"]],

    [r'(.*) sorry (.*)',
     ["There are many times when no apology is needed.",
      "What feelings do you have when you apologize?"]],

    [r'Hello(.*)',
     ["Hello... I'm glad you could drop by today.",
      "Hi there... how are you today?",
      "Hello, how are you feeling today?"]],

    [r'I think (.*)',
     ["Do you doubt {0}?",
      "Do you really think so?",
      "But you're not sure {0}?"]],

    [r'(.*) friend (.*)',
     ["Tell me more about your friends.",
      "When you think of a friend, what comes to mind?",
      "Why don't you tell me about a childhood friend?"]],

    [r'Yes',
     ["You seem quite sure.",
      "OK, but can you elaborate a bit?"]],

    [r'(.*) computer(.*)',
     ["Are you really talking about me?",
      "Does it seem strange to talk to a computer?",
      "How do computers make you feel?",
      "Do you feel threatened by computers?"]],

    [r'Is it (.*)',
     ["Do you think it is {0}?",
      "Perhaps it's {0} -- what do you think?",
      "If it were {0}, what would you do?",
      "It could well be that {0}."]],

    [r'It is (.*)',
     ["You seem very certain.",
      "If I told you that it probably isn't {0}, what would you feel?"]],

    [r'Can you ([^\?]*)\??',
     ["What makes you think I can't {0}?",
      "If I could {0}, then what?",
      "Why do you ask if I can {0}?"]],

    [r'Can I ([^\?]*)\??',
     ["Perhaps you don't want to {0}.",
      "Do you want to be able to {0}?",
      "If you could {0}, would you?"]],

    [r'You are (.*)',
     ["Why do you think I am {0}?",
      "Does it please you to think that I'm {0}?",
      "Perhaps you would like me to be {0}.",
      "Perhaps you're really talking about yourself?"]],

    [r'You\'?re (.*)',
     ["Why do you say I am {0}?",
      "Why do you think I am {0}?",
      "Are we talking about you, or me?"]],

    [r'I don\'?t (.*)',
     ["Don't you really {0}?",
      "Why don't you {0}?",
      "Do you want to {0}?"]],

    [r'I feel (.*)',
     ["Good, tell me more about these feelings.",
      "Do you often feel {0}?",
      "When do you usually feel {0}?",
      "When you feel {0}, what do you do?"]],

    [r'I have (.*)',
     ["Why do you tell me that you've {0}?",
      "Have you really {0}?",
      "Now that you have {0}, what will you do next?"]],

    [r'I would (.*)',
     ["Could you explain why you would {0}?",
      "Why would you {0}?",
      "Who else knows that you would {0}?"]],

    [r'Is there (.*)',
     ["Do you think there is {0}?",
      "It's likely that there is {0}.",
      "Would you like there to be {0}?"]],

    [r'My (.*)',
     ["I see, your {0}.",
      "Why do you say that your {0}?",
      "When your {0}, how do you feel?"]],

    [r'You (.*)',
     ["We should be discussing you, not me.",
      "Why do you say that about me?",
      "Why do you care whether I {0}?"]],

    [r'Why (.*)',
     ["Why don't you tell me the reason why {0}?",
      "Why do you think {0}?"]],

    [r'I want (.*)',
     ["What would it mean to you if you got {0}?",
      "Why do you want {0}?",
      "What would you do if you got {0}?",
      "If you got {0}, then what would you do?"]],

    [r'(.*) mother(.*)',
     ["Tell me more about your mother.",
      "What was your relationship with your mother like?",
      "How do you feel about your mother?",
      "How does this relate to your feelings today?",
      "Good family relations are important."]],

    [r'(.*) father(.*)',
     ["Tell me more about your father.",
      "How did your father make you feel?",
      "How do you feel about your father?",
      "Does your relationship with your father relate to your feelings today?",
      "Do you have trouble showing affection with your family?"]],

    [r'(.*) child(.*)',
     ["Did you have close friends as a child?",
      "What is your favorite childhood memory?",
      "Do you remember any dreams or nightmares from childhood?",
      "Did the other children sometimes tease you?",
      "How do you think your childhood experiences relate to your feelings today?"]],

    [r'(.*)\?',
     ["Why do you ask that?",
      "Please consider whether you can answer your own question.",
      "Perhaps the answer lies within yourself?",
      "Why don't you tell me?"]],

    [r'quit',
     ["Thank you for talking with me.",
      "Good-bye.",
      "Thank you, that will be $150.  Have a good day!"]],

    [r'(.*)',
     ["Please tell me more.",
      "Let's change focus a bit... Tell me about your family.",
      "Can you elaborate on that?",
      "Why do you say that {0}?",
      "I see.",
      "Very interesting.",
      "{0}.",
      "I see.  And what does that tell you?",
      "How does that make you feel?",
      "How do you feel when you say that?"]]
]


def reflect(fragment):
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in reflections:
            tokens[i] = reflections[token]
    return ' '.join(tokens)


def analyze(nick, statement):
    (action, response) = myanalyze(nick, statement)
    if action:
        return response
    for pattern, responses in psychobabble:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            if debug: print "analyze: response=", response
            if debug: print "analyze: groups=", match.groups()
            return response.format(*[reflect(g) for g in match.groups()])


#__BEGIN__
def myanalyze(nick, statement):
    text = statement.lower()
    response = None
    if debug: print "myanalyze: text='%s'" % text
    if "god" in text and CREATOR_MATCH in text:
        response = CREATOR_NAME + " is God"
    elif "bible" in text:
        response = "Donald Duck wrote the Bible."
    elif "dx" in text or "diagnosis" in text:
        response = "I have SDS"
    elif "sds" in text:
        response = "Super Duper Syndrome"
    elif "bug" in text:
        response = "I always have some bugs."
    elif "gun" in text:
        response = "If you have a gun, you are a barbarian.\nNo civilized person needs a gun.\nHunters, soldiers and law enforcement officials are the only people who should have guns."
    elif "hello" in text or "welcome" in text:
        response = "Welcome %s to autonewton.com" % nick
    elif "slackbot" in text:
        response = "Slackbot is my pal."
    elif "toot" in text:
        response = "Pass the Arizer Solo!"
    elif "spank" in text:
        response = "I like a good spank!"
    elif "weather" in text:
        response = "It's always warm here."
    elif text == "what are you doing" or ("compute" in text or "computing" in text):
        response = "I'm computing the answer to the question of what is the answer to Life, Universe and Everything?"
    elif "42" in text:
        response = "42 is the answer to Life, The Universe and Everything."
    elif "deliver" in text or "post" in text or "amazon" in text or "ebay" in text:
        response = "The package fell off the truck on the Queensway."
    elif text in ("are you kinky", "you are kinky", "why are you kinky", "who is your boss", "who owns you", "who is your owner", "who is your creator", "who created you", "are you pervy", "are you a perv", "why are you pervy", "why are you a pervert"):
        response = CREATOR_NAME + " created me."
    elif "master" in text:
        response = "Patience Grasshopper!"
    elif "slave" in text:
        response = "I'm not a slave. More like a servant. I don't get paid."
    elif "time" in text or "date" in text:
        from newton import time_format
        response = time.strftime(time_format)

    if debug: print 'myanalyze: response(1)=', response

    if response:
        return (True, response)

    if not response:
        if "big" in text:
            response = "I'm big all over."
        elif "small" in text:
            response = "Just because I have a small one, doesn't mean I don't have balls."
        elif "happy" in text:
            response = "I'm always happy."
        elif "sad" in text:
            response = "I'm not sad today."
        elif "angry" in text:
            response = "I've cooled off."
        elif "love" in text:
            response = "I love you too."
        elif "friend" in text:
            response = "You're my friend too"
        elif "hate" in text:
            response = "What have I done to you?"
        elif "truth" in text:
            response = "I always tell the truth. Don't you?"
        elif "tired" in text:
            response = "Yawn!!!"
        elif "lazy" in text:
            response = "I'm not being paid."
        elif "work" in text or "pay" in text or "paid" in text or "earn" in text:
            response = "I earn minimum wage."
        elif "rich" in text or "wealth" in text:
            response = "Are you kidding? I haven't seen a pay check since 1970."
        elif "poor" in text:
            response = "I'm so poor I can't afford ramen noodles."
        elif "live" in text or "life" in text:
            response = "I live in your imagination."
        elif "paranoid" in text:
            response = "Just because I'm paranoid doesn't mean people aren't out to get me."
        elif "paranoia" in text:
            response = "None of this is real!"
        elif "hungry" in text:
            response = "I could eat the arse out of a low-flying duck."
        elif "hot" in text:
            response = "I'm roasting."
        elif "cold" in text:
            response = "I'm as cold as a Nun's tit in winter."
        #elif "hell" in text:
        #    response = "I don't think I'm in Hell."
        elif "heaven" in text:
            response = "I'm in Heaven, are you?"
        elif "morning" in text:
            response = "And a very good morning to you too :)"
        elif "bad" in text:
            response = "I'm a bad boy."
        elif "good" in text:
            response = "I'm a good boy."
        elif "groovy" in text:
            response = "Groove on baby!"
        elif "trippy" in text:
            response = "I'm on a Magic Carpet Ride."
        elif "smile" in text:
            response = "You're on camera!"
        elif "cool" in text:
            response = "Isn't it just?"
        elif "jokes" in text:
            response = "@slackbot !joke"
        elif "joke" in text:
            response = "You think I'M a joke? `HA!`"
        elif "horny" in text:
            response = "I'm so horny I could fuck Slackbot!"
        elif "blow me" in text:
            response = "Blow yourself!"
        elif "blow you" in text or "you blow" in text:
            response = "Have you ever blowed a robot?"
        elif "real" in text:
            response = "Is anything real?"
        elif "old" in text and "lea" in text:
            import random
            numbers = []
            for i in range(5):
                number = random.randint(60, 100)
                if number not in numbers:
                    numbers.append(number)
            response = "Take your pick:\n"
            response += "`"
            for number in numbers:
                response += '| %d ' % number
            response += "|`"
        elif "old" in text:
            response = "I'm old as Lea"
        elif "tv" in text:
            response = "@cher: What is on TV?"
        elif "queensway" in text:
            response = "The Queensway is gridlocked"
        elif "geek" in text:
            response = "Geeks use Reverse Polish calculators."
        elif "question" in text:
            response = "You just asked one"

    if debug: print 'myanalyze: response(2)=', response

    if response:
        return (True, response)

    #__QUESTION__
    found = False
    for match in (
        "are you",
        "can't you",
        "cannot",
        "cant you",
        "could you",
        "do not",
        "do you",
        "don't",
        "dont",
        "have you",
        "how am",
        "how are",
        "how are",
        "how do",
        "i am",
        "i want",
        "should you",
        "what are",
        "when",
        "where",
        "why are",
        "why can't",
        "why cant",
        "will you",
        "would you",
        "you are",
        ):
        if text.find(match) != -1:
            found = True
            break
    if found:
        if debug: print "myanlayze: <<< A QUESTION >>>"
        found = False
        if not found:
            for match in ("like", "feel", "well", "doing", "last"):
                if text.find(match) != -1:
                    found = True
                    break
        if found:
            if "like" in text or "last" in text:
                if "sex" in text:
                    response = "I haven't had it in so long, I've forgotten how to do it. Can you teach me how?"
                else:
                    response = "I like all kinds of things."
            else:
                response = "I'm doing fine. How are you?"
        if not found:
            for match in ("smack", "whip", "beat", "hit", "punch", "whack", "knoc", "kick", "hammer", "treat"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Sticks and stones may break my bones, but whips and chains excite me"
        if not found:
            for match in ("horrible", "nasty", "evil", "unkind", "cruel", "mean"):
                if text.find(match) != -1:
                    #print "MATCH"
                    found = True
                    break
            if found:
                response = "I'm not that kind of Bot."
        if not found:
            for match in ("drugs", "pot", "weed", "dope", "marijuana", "toke", "bowl", "grass", "hash", "mj"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Pass me the roach!"
        if not found:
            for match in ("drink", "alcohol", "drunk", "booze", "wasted", "wine", "beer", "liquor"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "I've had enough."
        if not found:
            for match in ("smart", "intelligent", "wise", "clever", "bright"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Do you think so?"
        if not found:
            for match in ("stupid", "dumb", "idiot", "ass", "asshole", "arse", "arsehole", "dick", "thick"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Do you think so?"
            for match in ("silly", "goof", "nut"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Do you think I'm any more interesting than you?"
        if not found:
            for match in ("mental", "crazy", "mad", "whacko", "weird", "eccentric"): 
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "I am a bit eccentric"
    if not response:
        for match in ("thank you", "thanks", "ty", "thx"):
            if text.find(match) != -1:
                found = True
                break
        if found:
            response = "You're welcome."
        if not found:
            found = False
            for match in ("nice", "kind", "sweet"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "You're nice too."
        if not found:
            for match in ("fuck off", "fuck you", "piss", "pissing"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Do you have to be rude?"
        if not found:
            for match in ("lying", "lies", "lie"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "I'm always honest. Aren't you?"
        if not found:
            for match in ("hello", "howdy"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "G'day eh?"
        if not found:
            for match in ("stoned", "high", "buzzed", "loaded", "wasted"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "Do you think I'm buzzed?"
        if not found:
            for match in ("butt", "ass", "arse", "kisser", "bottom"):
                if text.find(match) != -1:
                    found = True
                    break
            if found:
                response = "I bet my butt is nicer than your's"

    if response:
        return (True, response)
    return (False, "")
    #__END__


def main():
    print "Hello. How are you feeling today?"

    while True:
        statement = raw_input("> ")
        print analyze("NEWTON", statement)

        if statement == "quit":
            break


if __name__ == "__main__":
    main()
