#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
_old_API = False
try:
    import graspi
except:
    print("Cannot find the RFC API module graspi.py.")
    print("Will run with only the basic grasp.py module.")
    _old_API = True
    try:
        import grasp as graspi
    except:
        print("Cannot import grasp.py")
        time.sleep(10)
        exit()
import threading
import datetime
import cbor
import random

####################################
# Flood EX1 repeatedly
####################################

class flooder(threading.Thread):
    """Thread to flood EX1 repeatedly"""
    global keep_going
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while keep_going:
            time.sleep(60)
            obj1.value = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC from Briggs")
            err = graspi.flood(asa_handle, 59000, [graspi.tagged_objective(obj1,None)])
            if err:
                graspi.tprint("Flood failure:",graspi.etext[err])
            time.sleep(5)
            if _old_API:
                if graspi.test_mode:
                    dump_some()
            else:
                if graspi.grasp.test_mode:
                    dump_some()
        graspi.tprint("Flooder exiting")


###################################
# Print obj_registry and flood cache
###################################

def dump_some():
    graspi.dump_all(partial=True)
    time.sleep(5)

######################
# Main code starts
######################                

global _prng, reserves, asa_handle

try:
    graspi.checkrun
except:
    #not running under ASA loader
    graspi.tprint("==========================")
    graspi.tprint("ASA Briggs is starting up.")
    graspi.tprint("==========================")
    graspi.tprint("Briggs is a demonstration Autonomic Service Agent.")
    graspi.tprint("It tests out several basic features of GRASP, and")
    graspi.tprint("then runs indefinitely as one side of a negotiation.")
    graspi.tprint("It acts as the banker, giving out money, and can")
    graspi.tprint("handle multiple overlapping negotiations.")
    graspi.tprint("The sum available is random for each negotiation,")
    graspi.tprint("and the negotiation timeout is changed at random.")
    graspi.tprint("On Windows or Linux, there should be a nice window")
    graspi.tprint("that displays the negotiation process.")
    graspi.tprint("==========================")

    time.sleep(8) # so the user can read the text
    
_prng = random.SystemRandom() # best PRNG we can get
keep_going = True

####################################
# Register ASA/objectives
####################################

err,asa_handle = graspi.register_asa("Briggs")
if not err:
    graspi.tprint("ASA Briggs registered OK")
else:
    graspi.tprint("Cannot register ASA:", graspi.etext[err])
    keep_going = False
    
obj1 = graspi.objective("EX1")
obj1.loop_count = 4
obj1.synch = True

err = graspi.register_obj(asa_handle,obj1)
if not err:
    graspi.tprint("Objective EX1 registered OK")
else:
    graspi.tprint("Cannot register objective:", graspi.etext[err])
    keep_going = False

dump_some()

flooder().start()
graspi.tprint("Flooding EX1 for ever")

