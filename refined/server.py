import time
from traceback import extract_stack

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
        while keep_going:
            mprint("flooding map")
            err = graspi.flood(self.asa, 59000, [graspi.tagged_objective(self.obj, None)])
            time.sleep(5)
        mprint("exiting flooder")


# flooder(tagged_map).start()

#####################################
# creating objective for negotiation
#####################################
map2 = graspi.objective("map2")
map2.neg = True
map2.synch = False
map2.loop_count = 10
map2.value = value = {'49':['53', '30']}
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
            answer.value = cbor.load(answer.value)
            mprint("cbor value decoded")
            mprint(answer.value)
            _cbor = True
        except:
            _cbor = False
        mprint("objective name {} and value {}".format(self.obj.name, self.obj.value))
        mprint("got request for {}".format(answer.value))

        if answer.value == self.obj.value:
            mprint("synchronized already")
        else:
            mprint("negotiating over {}".format(self.obj.name))
            step = 1
            mprint("in _{}_ step of negotiation".format(step))
            print("*************************")
            answer.value = cbor.loads(answer.value)
            print(answer.value)
            print("*************************")
            self.obj.value.update(answer.value) 
            _r = graspi.negotiate_step(self.handler, nhandler, self.obj, 1000)
            if _old_API:
                err, tmp, answer = _r
                reason = answer
            else:
                err, temp, answer, reason = _r
            mprint("step {}\t gave: err {}, temp {}, answer {}, reason {}"
                                .format(step, err, temp, answer, reason))
            if (not err) and (temp == None):
                mprint("negotiation succeeded")
                mprint("final result\n {}".format(self.obj.value))
            else:
                print("#########################")
                print("negotiation failed\n\t")
                print(graspi.etext[err])
                print(reason)
                print("#########################")
                




while True:
    mprint("listening for negotiation requests")
    err, shandle, answer = graspi.listen_negotiate(asa_handle, map2)
    
    if err:
        mprint("listen_negotiate error\n\t" + graspi.etext[err])
        time.sleep(5)
    else:
        negotiator(asa_handle, map2, shandle, answer).start()
    
    try:
        if not graspi.checkrun(asa_handle, "TD_Server"):
            keep_going = False  
    except:
        pass
