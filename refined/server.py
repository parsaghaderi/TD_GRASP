import time

from Briggs import dump_some
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
import cbor
import random
try: 
    import networkx as nx
except:
    print("can't import networkx; installing networkx")
    import os
    os.system('python3 -m pip install networkx')
keep_going = True
#########################
# utility print function
#########################
def mprint(msg):
    print("\n#######################")
    print(msg)
    print("#######################\n")


#########################
#check grasp
#########################
try:
    graspi.checkrun
except:
    #not running under ASA loader
    graspi.tprint("========================")
    graspi.tprint("ASA Gray is starting up.")
    graspi.tprint("========================")
    graspi.tprint("Gray is a demonstration Autonomic Service Agent.")
    graspi.tprint("It tests out several basic features of GRASP, and")
    graspi.tprint("then runs indefinitely as one side of a negotiation.")
    graspi.tprint("It acts as a client, asking for money.")
    graspi.tprint("The sum requested is random for each negotiation,")
    graspi.tprint("and some GRASP features are used at random.")
    graspi.tprint("On Windows or Linux, there should be a nice window")
    graspi.tprint("that displays the negotiation process.")
    graspi.tprint("========================")

###############################
#registering objective and ASA
###############################
mprint("registering asa and objective")
err, asa_handle = graspi.register_asa("TD_Server")
if not err:
    mprint("ASA registered successfully")
else:
    mprint("Cannot register ASA:\n\t" + graspi.etext[err])
    mprint("exiting now.")
    exit()

map = graspi.objective("map")
map.neg = False
map.synch = True
map.loop_count = 10 #TODO change to 4
map.value = {'49':['53', '30']}
err = graspi.register_obj(map)
if not err:
    mprint("Objective registered successfully")
else:
    mprint("Cannot register Objective:\n\t"+ graspi.etext[err])
    mprint("exiting now.")
    exit()

#creating tagged objective
tagged_map = graspi.tagged_objective(map, asa_handle)

#pass a tagged objective
class flooder(threading.Thread):
    def __init__(self, tagged):
        self.obj = tagged.objective
        self.asa = tagged.source
        self.tagged = tagged
    def run(self):
        while keep_going:
            err = graspi.flood(self.asa, 59000, [self.tagged])
            time.sleep(5)
        mprint("exiting flooder")
dump_some()
flooder(tagged_map).start()