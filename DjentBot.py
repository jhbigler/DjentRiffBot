#!/usr/bin/python3

import os
import numpy as np
#import facebook as fb
#import pprint as ppr
import random
import json
import twitter
import html

__description__ = """
A bot that generates a 'Djent' riff and posts to social media
"""

DIR = os.path.dirname(os.path.realpath(__file__))

FRETS_FILE = "{}/config/frets.json".format(DIR)
REP_FILE = "{}/config/repetitions.json".format(DIR)
EFFECTS_FILE = "{}/config/effects.txt".format(DIR)
PATTERNS_FILE = "{}/config/patterns.json".format(DIR)
AUTH_FILE = "{}/auth.json".format(DIR)

def gen_frets():
    with open(FRETS_FILE, "r") as f:
        frets = json.loads(f.read())
    total_weight = sum([frets[s] for s in frets.keys()])
    return {"values":[int(s) for s in frets.keys()], \
            "weights":[frets[s]/total_weight for s in frets.keys()]}

def gen_reps():
    with open(REP_FILE, "r") as f:
        reps = json.loads(f.read())
    total_weight = sum([reps[s] for s in reps.keys()])
    return {"values":[int(s) for s in reps], \
            "weights":[reps[s]/total_weight for s in reps.keys()]}

def gen_patterns():
    with open(PATTERNS_FILE, "r") as f:
        patterns = json.loads(f.read())
    total_weight = sum([patterns[s] for s in patterns.keys()])
    return {"values":[p for p in patterns.keys()], \
            "weights":[patterns[p]/total_weight for p in patterns.keys()]} 

def gen_effects():
    with open(EFFECTS_FILE, "r") as f:
        effects = [e.strip() for e in f]
    return effects

FRETS = gen_frets()
EFFECTS = gen_effects()
PATTERNS = gen_patterns()
REPS = gen_reps()

def grab_n():
    return np.random.choice(REPS["values"],size=1,p=REPS["weights"])[0]

def grab_fret(min = 0):

    #Some funkiness if we need to grab a fret larger than 0 or more
    if(min > 0):
        pop = list(filter(lambda x: x >= min, FRETS["values"]))
        weights = FRETS["weights"][len(FRETS["values"]) - len(pop):]
        #We then need to make sure the weights add up to 1
        multiplier = 1/sum(weights)
        weights = [multiplier * w for w in weights]
        
    else:
        pop = FRETS["values"]
        weights = FRETS["weights"]
    return np.random.choice(pop,\
            size=1,\
            p=weights)[0]

def grab_two_frets():
    return np.random.choice(FRETS["values"],size=2, replace=False, p=FRETS["weights"])\
            .tolist()

def effect():
    return np.random.choice(EFFECTS,size=1)[0]

def fret_n():
    n = grab_n()
    fret = grab_fret()
    return "{}".format(fret) * n

def fret_hammer():
    return "^".join(["{}".format(f) for f in grab_two_frets()])

def fret_bend():
    return "{}b".format(grab_fret(min=1))

def grab_patterns():
    num = random.randint(5,10)
    return np.random.choice(PATTERNS["values"], size=num, p=PATTERNS["weights"])\
            .tolist()

FUNCS = {
    "effect":effect,
    "fret_n":fret_n,
    "fret_hammer":fret_hammer,
    "fret_bend":fret_bend
    }

def post_to_twitter(auth,post):
    api = twitter.Api(**auth)
    return  api.PostUpdate(post)

if(__name__ == "__main__"):

    riff = "-".join([FUNCS[p]() for p in grab_patterns()])
    auth = {}
    with open(AUTH_FILE,"r") as f:
        auth = json.loads(f.read())

    status = post_to_twitter(auth, riff)
    print(html.unescape(status.text))
