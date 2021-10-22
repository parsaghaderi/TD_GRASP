import time
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
import cbor #read about it. 
import random

#import networkx as nx 
#TODO: since networkX might not be accessible to all nodes and its not
#a defult python module, later convert networkx to a simple dictionary. 
# but for now, for the simplicity and better undersanding and better 
# visualization, we prefer to use networkX since it provides lots of utility 
#functions for handling graph related objects. 


############################
# STATES OF ASA
############################
global state
global VISITED
global Parent

############################
# Registering ASA and Objects
############################

err, asa_handle = graspi.register_asa("TD")
if not err:
    print("ASA registered OK")
else:
    print("can't register ASA: "+ graspi.etext[err])

topology = graspi.objective("topology")
topology.neg = False
topology.synch = True

err = graspi.register_obj(asa_handle, topology)
if not err:
    print("object registered correctly")
else:
    print("cannot register the object: "+graspi.etext[err])

class flooder(threading.Thread):
    """Thread to flood EX1 repeatedly"""
    global keep_going
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while keep_going:
            time.sleep(60)
            obj1.value = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC from Briggs")
            err = graspi.flood(asa_handle, 59000, [graspi.tagged_objective(topology,None)])
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

flooder().start()