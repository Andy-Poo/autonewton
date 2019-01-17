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

# flags for turning on debugging diagnostics
debug = False

# animal "database" to save stats during bot restarts
animal_database = "/home/andy/data/newton.pickle"

import re
import random
import pickle

"""
this is the list of animals we support in Slack
the dictionary key is the animal emoji,
which will be inserted into the output in the
required surrounding colons.
The dictionary items consist of these objects:
[0] the sound the animal makes
[1] the number of times the animal was saved
[2] the number of times the animal was killed
"""
animals = {
    'bear': ['growl', 0, 0],
    'camel': ['snort', 0, 0],
    'cat2': ['meow', 0, 0],
    'cow2': ['moo', 0, 0],
    'dog2': ['woof', 0, 0],
    'elephant': ['trumpet', 0, 0],
    'goat': ['bleat', 0, 0],
    'koala': ['grunt', 0, 0],
    'leopard': ['growl', 0, 0],
    'monkey': ['chatter', 0, 0],
    'mouse': ['squeak', 0, 0],
    'ox': ['moo', 0, 0],
    'penguin': ['coo', 0, 0],
    'pig2': ['oink', 0, 0],
    'poodle': ['yap', 0, 0],
    'rabbit2': ['squeak', 0, 0],
    'rat': ['squeak', 0, 0],
    'rooster': ['cock-a-doodle-do', 0, 0],
    'sheep': ['baa', 0, 0],
    'snake': ['hiss', 0, 0],
    'tiger2': ['growl', 0, 0],
    'water_buffalo': ['moo', 0, 0],
    'wolf': ['howl', 0, 0]
}

# this is the stats per user and the user entries
# are created in the dictionary when the user
# makes his or her first save or kill
animal_stats = {}

# when the bot calls animal_game, save the animal's name
animal_last = None

# the nickname of the user who made the first save or kill.
# this gets reset back to None when the bot reports the winner.
animal_person = None

# also save the nickname before it gets cleared
animal_person_prev = None

# and save the animal that was saved
animal_last = None

# command to save and kill animals. for example,
# !save
# !kill
animal_save_commands = ['save', 'befriend', 'bef']
animal_kill_commands = ['kill', 'bang', 'club', 'ak47', 'shoot']
animal_commands = ['stats', 'animal', 'animals', 'win', 'winner', 'won']
animal_commands += animal_save_commands 
animal_commands += animal_kill_commands 
if debug:
    animal_commands.append('trigger')

def animal_strip(animal):
    """Strip digits from the animal name to make an easier match.

    animal : str
        the name of the animal

    Returns:
        str : the simplified name of the animal
    """
    return animal.strip('0123456789')

def animal_match(animal):
    """This name of an animal that does not have to be an exact match.

    animal : str
        the name of the animal that does not have to be the full
        emoji name

    Returns:
        tuple : (emoji:str, item=list)
    """
    for emoji in animals.keys():
        if emoji.find(animal) != -1:
            return (emoji, animals[emoji])
    return (None, None)

def animal_info(animal):
    """This gets the stats info for a specific animal.

    animal : str
        the name of the animal.
        it does not have to be an exact match of the emoji name.

    Returns:
        tuple : (saved:int, kills:int)
    """
    result = (0, 0,)
    (emoji, item) = animal_match(animal)
    if emoji:
        result = (item[1], item[2])
    return result

def animal_pick():
    """Picks an animal for the animal list at random.

    Returns:
        tuple : (emoji:str, sound:str, saved:int, killed:int)
    """
    emoji = random.choice(animals.keys())
    sound = animals[emoji][0]
    saved = animals[emoji][1]
    killed = animals[emoji][2]
    return (emoji, sound, saved, killed)

def animal_game(item=None):
    """The output that is sent to the chat window by the bot
    at random on a timer.

    Returns:
        str : text
    """
    global animal_person, animal_last
    if debug: print 'animal_game: item=', item
    if debug: print 'animal_game: animal_person=', animal_person
    if debug: print 'animal_game: animal_person_prev=', animal_person_prev
    if debug: print 'animal_game: animal_last=', animal_last
    # set the animal person for the new game
    animal_person = 'newton'
    if item is None:
        item = animal_pick()
    (emoji, sound, saved, killed) = item
    animal_last = emoji
    result = "`%s`   :%s:\n" % (sound.upper(), emoji)
    return result

def animal_game_chime():
    """Called to chime the rooster at the top of the hour.
    
    Returns:
        str : the result of animal_game
    """
    item = ['rooster'] + animals['rooster']
    #print 'animal_game_chime: item=', item
    return animal_game(item)

def animal_save(user):
    """Called when a user makes a save.

    user : str
        the nickname of the user
    """
    global animal_person, animal_person_prev, animal_last
    if debug: print 'animal_save: user=', user
    if debug: print 'animal_save: animal_person=', animal_person
    if debug: print 'animal_save: animal_person_prev=', animal_person_prev
    if debug: print 'animal_save: animal_last=', animal_last
    # if the animal was already saved, then do nothing
    #if animal_person is None or animal_person_prev is None:
    if animal_person is None:
        return None
    animal_person_prev = animal_person = user
    if user not in animal_stats:
        animal_stats[user] = [0, 0]
    # first index is the save stats
    animal_stats[user][0] += 1
    # the second index is the save stats
    if animal_last in animals:
        animals[animal_last][1] += 1
    # clear the animal person for the next game
    animal_person = None
    if debug: print 'animal_save: animal_person_prev(2)=', animal_person_prev
    return animal_person_prev

def animal_kill(user):
    """Called when a user makes a kill.

    user : str
        the nickname of the user
    """
    global animal_person, animal_person_prev
    if debug: print 'animal_kill: user=', user
    if debug: print 'animal_kill: animal_person=', animal_person
    if debug: print 'animal_kill: animal_person_prev=', animal_person_prev
    # if the animal was already saved, then do nothing
    #if animal_person is None or animal_person_prev is None:
    if animal_person is None:
        return None
    animal_person_prev = animal_person = user
    if user not in animal_stats:
        animal_stats[user] = [0, 0]
    # second index is the kill stats
    animal_stats[user][1] += 1
    # the third index is the save stats
    if animal_last in animals:
        animals[animal_last][2] += 1
    # clear the animal person for the next game
    animal_person = None
    if debug: print 'animal_kill: animal_person_prev(2)=', animal_person_prev
    return animal_person_prev

def animal_print_stats(animal=None):
    """Print the stats on a specific animal or all animals.

    animal : str
        the name of an animal or None if all animals

    Returns:
        str : the stats for the animal or animals
    """
    if debug: print 'animal_print_stats: animal=', animal
    result = ''
    if animal:
        (emoji, item) = animal_match(animal)
        if debug: print 'animal_print_stats: emoji=', emoji
        if debug: print 'animal_print_stats: item=', item
        if emoji:
            (saved, killed) = (item[1], item[2])
            animal = animal_strip(emoji).upper()
            result = "\n:%s: %d *%s* saved and %d killed" % (
                animal, saved, animal, killed)

    else:
        for emoji in sorted(animals):
            sound = animals[emoji][0]
            saved = animals[emoji][1]
            killed = animals[emoji][2]
            animal = animal_strip(emoji).upper()
            result += "\n:%s: %d *%s* saved and %d killed" % (
                animal, saved, animal, killed)
    return result

def animal_user_stats(user, arg):
    """Print the stats for a user.

    user : str
        the user nickname
    arg : str
        optional username argument
    
    Returns:
        str : the stats results for the user
    """
    if debug: print 'animal_user_stats: user=', user
    if debug: print 'animal_user_stats: arg=', arg
    result = '\n'
    if debug: print 'animal_user_stats: animal_stats=', animal_stats
    if arg:
        user = arg
    if user in animal_stats:
        (saves, kills) = animal_stats[user]
        result = "%s has saved %d animals and killed %d animals." % \
            (user, saves, kills)
    else:
        result = "%s has neither saved or killed an animal." % user

    top_saves = 0
    top_saves_user = None
    top_kills = 0
    top_kills_user = None
    for user in animal_stats:
        (saves, kills) = animal_stats[user]
        if saves > top_saves:
            top_saves = saves
            top_saves_user = user
        if kills > top_kills:
            top_kills = kills
            top_kills_user = user
    result += "\n\n%s has made %s saves and is a good person." % (top_saves_user, top_saves)
    result += "\n%s has made %s kills and is a bad person." % (top_kills_user, top_kills)
    return result

def animal_winner(user, action=None):
    """Prints who won the game.

    user : str
        the user nickname
    action : str
        None: the user did not win
        'save': the user saved an animal
        'kill': the user killed an animal
        'query': the user is querying to see who won
    
    Returns:
        str : the winner
    """
    if debug: print 'animal_winner: user=', user
    if debug: print 'animal_winner: action=', action
    if debug: print 'animal_winner: animal_person=', animal_person
    if debug: print 'animal_winner: animal_person_prev=', animal_person_prev
    result = ''
    # if animal_person is None, someone already won
    if animal_person:
        if user == animal_person_prev:
            result = "\nYOU WON!!!"
        else:
            if animal_person_prev is None:
                result = "\nThe game hasn't started yet."
            else:
                result = "\n`%s` WON" % animal_person_prev
    else:
        if action is None:
            result = "\nTOO LATE"
        elif action is 'query':
            result = "\n`%s` WON" % animal_person_prev
        elif action is 'save':
            result = "\n%s saved a %s. Good job!" % (animal_person_prev, animal_last)
        elif action is 'kill':
            result = "\n%s killed a %s. You must be hungry." % (animal_person_prev, animal_last)
    return result

def animal_command_handler(user, command, query):
    """This function handles the animal commands.

    user : str
        the user nickname
    command : str
        the animal command
    query : str
        the animal command arguments

    Returns:
        str : the text result
    """
    if debug: print 'animal_command_handler: user=', user
    if debug: print 'animal_command_handler: command=', command
    if debug: print 'animal_command_handler: query=', query
    result = ''
    tokens = query.split(' ')
    if len(tokens) >= 1:
        arg = tokens[0]
    else:
        arg = 'newton'
    if command in animal_save_commands:
        if animal_save(user):
            action = 'save'
        else:
            action = None
        result = animal_winner(user, action=action)
    elif command in animal_kill_commands:
        if animal_kill(user):
            action = 'kill'
        else:
            action = None
        result = animal_winner(user, action=action)
    elif command == 'stats':
        result = animal_user_stats(user, arg)
    elif command == 'animal' or command == 'animals':
        result = animal_print_stats(arg)
    elif command == 'winner' or command == 'win' or command == 'won':
        result = animal_winner(user, action='query')
    elif debug and command == 'trigger':
        if debug: print 'animal_command_handler: TRIGGER'
        result = animal_game()
    return result

def animal_dump():
    """Save an animal in the "database".
    """
    if debug: print 'animal_dump:', animal_database
    data = (animals, animal_stats)
    try:
        pickle.dump(data, open(animal_database, "wb"))
    except Exception as e:
        print 'animal_save: Error:', e

def animal_load():
    """Load the animal stats from the "database".
    """
    global animals, animal_stats
    if debug: print 'animal_load:', animal_database
    try:
        data = pickle.load(open(animal_database, "rb"))
        animals, animal_stats = data
    except Exception as e:
        print 'animal_save: Error:', e

# are we running this script from the command line?
if __name__ == '__main__':
    import sys
    user = 'newton'
    while True:
        print animal_game()
        line = raw_input("? ")
        if not line:
            sys.exit()
        text = line.strip()
        if not text:
            sys.exit()
        if re.search("^!", text):
            words = text.split()
            tokens = []
            for word in words:
                w = word.strip()
                if w:
                    tokens.append(w)
            command = tokens[0][1:].lower()
            query = ' '.join(tokens[1:])
            print animal_command_handler(command, query)
