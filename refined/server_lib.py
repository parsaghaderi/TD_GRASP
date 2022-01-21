#libraries
import time
from traceback import extract_stack
import sys
import os
from typing import List
import threading
import cbor
import random
try: 
    import networkx as nx
except:
    print("can't import networkx; installing networkx")
    import os
    os.system('python3 -m pip install networkx')
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

MAP_PATH = '/etc/TD_map/neighbors.map'


#########################
# utility function for reading info from map; 
# later this info will be received from ACP
#########################
def readmap(path):
    file = open(path)
    l = file.readlines()
    l = [int(item) for item in l]
    return l[0], l[1:]

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


#########################
#Registering ASA 
#########################
def ASA_REG(name):
    mprint("registering asa and objective")
    err, asa_handle = graspi.register_asa(name)
    if not err:
        mprint("ASA registered successfully")
        return err, asa_handle
    else:
        mprint("Cannot register ASA:\n\t" + graspi.etext[err])
        mprint("exiting now.")


#########################
#Registering objectives
#########################
def OBJ_REG(name, value, neg, synch, loop_count, ASA):
    obj = graspi.objective(name)
    obj.value = value
    obj.neg = neg
    obj.synch = synch
    obj.loop_count = loop_count
    err = graspi.register_obj(ASA, obj)
    if not err:
        mprint("Objective registered successfully")
    else:
        mprint("Cannot register Objective:\n\t"+ graspi.etext[err])
        mprint("exiting now.")
    return obj, err
        
def TAG_OBJ(obj, ASA):
    return graspi.tagged_objective(obj, ASA)


#########################
#flooder thread
#########################
class flooder(threading.Thread):
    def __init__(self, tagged, asa):
        threading.Thread.__init__(self)
        self.tagged = tagged
        self.asa = asa

    def run(self):
        while True:
            mprint("flooding map")
            err = graspi.flood(self.asa, 59000, [graspi.tagged_objective(self.tagged.objective, None)])
            time.sleep(1)
        

#########################
#observer thread for server
#########################
class observer_server(threading.Thread):
    def __init__(self, last_update, map):
        threading.Thread.__init__(self)
        self.map = map
        self.last_update = last_update
        
    def run(self):
        while True:
            if os.stat(MAP_PATH).st_mtime != self.last_update:
                mprint("map updated")
                self.last_update = os.stat(MAP_PATH).st_mtime
                map_address, neighbors = readmap(MAP_PATH)
                self.map.value[map_address] = neighbors


####################
#negotiating objective for server
####################
#TODO save the value of neg and synch objetive in a sepaarate variable so that
class negotiator(threading.Thread):
    #handler and obj for this asa - neg should be on for objectives. that's why we can't use the same objective.
    #nhandler and nobj for negotiator asa and obj
    def __init__(self,handler, obj, nhandler, nobj, synch, tagged):
        threading.Thread.__init__(self, daemon = True)
        self.handler = handler
        self.obj = obj #map neg
        self.nhandler = nhandler
        self.nobj = nobj #answer
        self.sync_obj =synch #map sync
        self.tagged = tagged #tagged_objective

    def run(self):
        global _old_API
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
                end_err = graspi.end_negotiate(self.handler, nhandler, False, reason=None)
                mprint("negotiation succeeded")
                mprint("final result\n {}".format(self.obj.value))
                self.sync_obj.value = self.obj.value
                self.tagged.objective.value = self.sync_obj.value
                if not end_err:
                    mprint("negotiation session ended")
            else:
                print("#########################")
                print("negotiation failed\n\t")
                print(graspi.etext[err])
                print(reason)
                print("#########################")