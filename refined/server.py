import time
from traceback import extract_stack
import sys
import os
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

MAP_PATH = '/etc/TD_map/neighbors.map'
def readmap(path):
    file = open(path)
    l = file.readlines()
    l = [int(item) for item in l]
    return l[0], l[1:]


LAST_UPDATE = os.stat('/etc/TD_map/neighbors.map').st_mtime
MY_ADDRESS, NEIGHBORS = readmap(MAP_PATH)


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
map.value = {MY_ADDRESS:NEIGHBORS}
err = graspi.register_obj(asa_handle, map)
if not err:
    mprint("Objective registered successfully")
else:
    mprint("Cannot register Objective:\n\t"+ graspi.etext[err])
    mprint("exiting now.")
    exit()

#creating tagged objective
tagged_map = graspi.tagged_objective(map, asa_handle)
# from sync_server import flooder
#pass a tagged objective
#TODO change here - separate
class flooder(threading.Thread):
    def __init__(self, tagged):
        threading.Thread.__init__(self)
        self.obj = tagged.objective
        self.asa = tagged.source
        self.tagged = tagged
        
    def run(self):
        while keep_going:
            mprint("flooding map")
            err = graspi.flood(self.asa, 59000, [graspi.tagged_objective(self.obj, None)])
            time.sleep(5)
        mprint("exiting flooder")


flooder(tagged_map).start()
#####################################
# creating objective for negotiation
#####################################
map2 = graspi.objective("map2")
map2.neg = True
map2.synch = False
map2.loop_count = 10
map2.value = {MY_ADDRESS:NEIGHBORS}
err = graspi.register_obj(asa_handle, map2)
if not err:
    mprint("objective map2 registered correctly")
else:
    mrpint("cannot register map2\n\t" + graspi.etext[err])
    mprint("exiting now")
    
    exit()

####################
#negotiating objective
####################
class negotiator(threading.Thread):
    #handler and obj for this asa
    #nhandler and nobj for negotiator asa and obj
    def __init__(self,handler, obj, nhandler, nobj):
        threading.Thread.__init__(self, daemon = True)
        self.handler = handler
        self.obj = obj
        self.nhandler = nhandler
        self.nobj = nobj

    def run(self):
        mprint("starting negotiation")
        answer = self.nobj
        nhandler = self.nhandler
        try:
            answer.value = cbor.loads(answer.value)
            mprint("cbor value decoded")#√
            mprint(answer.value)#√
            mprint("current value of objective")#√
            mprint(self.obj.value)#√
            _cbor = True
        except:
            _cbor = False
        mprint("objective name {} and value {}".format(self.obj.name, self.obj.value))#√
        mprint("got request for objective {}".format(answer.name))#√
        if answer.value == self.obj.value:
            mprint("synchronized already")#√
        else:
            mprint("negotiating over {}".format(self.obj.name))#√
            step = 1
            mprint("in _{}_ step of negotiation".format(step))#√
            mprint("answer value is {}".format(answer.value))#√
            self.obj.value.update(answer.value) #√
            mprint(self.obj.value)#√
            
            _r = graspi.negotiate_step(self.handler, nhandler, self.obj, 1000)
            if _old_API:
                err, tmp, answer = _r
                reason = answer
                mprint("old API true")
            else:
                err, temp, answer, reason = _r
                mprint("old API false")#√
            mprint("step {}\t gave: err {}, temp {}, answer {}, reason {}"
                                .format(step, err, temp, answer, reason))
            if (graspi.etext[err] == "OK"):
                end_err = graspi.end_negotiate(asa_handle, nhandler, False, reason=None)
                mprint("negotiation succeeded")
                mprint("final result\n {}".format(self.obj.value))
                map.value = self.obj.value
                if not end_err:
                    mprint("negotiation session ended")
            else:
                print("#########################")
                print("negotiation failed\n\t")
                print(graspi.etext[err])
                print(reason)
                print("#########################")
                


class observer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global LAST_UPDATE
        if os.stat('/etc/TD_map/neighbors.map').st_mtime == LAST_UPDATE:
            global MY_ADDRESS
            global NEIGHBORS
            global map2
            global map
            MY_ADDRESS, NEIGHBORS = readmap(MAP_PATH)
            map2.value[MY_ADDRESS] = NEIGHBORS
            map.value[MY_ADDRESS] = NEIGHBORS
            mprint("local map changed")
            mprint(cbor.loads(map2.value))
            LAST_UPDATE = os.stat('/etc/TD_map/neighbors.map').st_mtime
            time.sleep(5)
            

while True:
    mprint("listening for negotiation requests")
    err, shandle, answer = graspi.listen_negotiate(asa_handle, map2)
    
    if err:
        mprint("listen_negotiate error\n\t" + graspi.etext[err])
        time.sleep(5)
    else:
        mprint("listen negotiation succeed")
        negotiator(asa_handle, map2, shandle, answer).start()
        observer().start()
    try:
        if not graspi.checkrun(asa_handle, "TD_Server"):
            keep_going = False  
    except:
        pass
