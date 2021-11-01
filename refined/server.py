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
import cbor
import random
try: 
    import networkx as nx
except:
    print("can't import networkx; installing networkx")
    import os
    os.system('python3 -m pip install networkx')
keep_going = True

print("to the code and beyond!")
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
    graspi.tprint("ASA server is starting up.")
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
err = graspi.register_obj(asa_handle, map)
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
        threading.Thread.__init__(self)
        self.obj = tagged.objective
        self.asa = tagged.source
        self.tagged = tagged
        
    def run(self):
        while True:
            mprint("flooding map")
            err = graspi.flood(self.asa, 59000, [graspi.tagged_objective(self.obj, None)])
        mprint("exiting flooder")

flooder(tagged_map).start()