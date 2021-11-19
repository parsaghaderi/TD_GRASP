import time
from traceback import extract_stack
import sys
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
import sys

def mprint(msg):
    print("\n#######################")
    print(msg)
    print("#######################\n")

try:
    graspi.checkrun
except:
    #not running under ASA loader
    graspi.tprint("========================")
    graspi.tprint("ASA server is starting up.")
    graspi.tprint("========================")

mprint("registering election asa")
err, asa_handle = graspi.register_asa("election")
if not err:
    mprint("ASA registered successfully")
else:
    mprint("Cannot register ASA:\n\t" + graspi.etext[err])
    mprint("exiting now.")
    exit()
KEEP_GOING=True
random.seed(1024)
poll = random.random()

leader = graspi.objective("election")
leader.value = False
leader.synch = False
leader.dry = True
leader.neg = True
leader.loop_count = 10

err = graspi.register_obj(asa_handle, leader)

if not err:
    mprint("objective registered successfully")
else:
    mprint("can't register objective")
    exit()

tagged_leader = graspi.tagged_objective(leader, asa_handle)

class flooder(threading.Thread):
    def __init__(self, tagged):
        threading.Thread.__init__(self):
        self.obj=  tagged.objective
        self.asa = tagged.source
        self.tagged = tagged
    def run(self):
        while KEEP_GOING:
            mprint("election started")
            err = graspi.flood(self.asa, 59000, [graspi.tagged_objective(self.obj, None)])
            time.sleep(1)
        mprint("exiting election")
        if leader.value == True:
            mprint("you're the leader")
        else:
            mprint("you're not the leader")
flooder(tagged_leader).start()

class negotiator(threading.Thread):
    def __init__(self, shandle, nobj):
        threading.Thread.__init__(self, daemon=True)
        self.shandle = shandle
        self.nobj = nobj

    def run(self):
        answer = self.nobj
        shandle = self.shandle

        try:
            answer.value=cbor.loads(answer.value)
            mprint("cbor value decoded - {}".format(answer.value))
            
            _cbor= True
        except:
            _cbor = False
        
        if answer.dry:
            if answer.value > poll:
                leader.value = False
                mprint("you're not leader")
                mprint("{} is leader".format(shandle))
                KEEP_GOING = False
                err = graspi.end_negotiate(asa_handle, shandle, True)
                if not err:
                    mprint("end_negotiation error {}".format(graspi.etext[err]))
            else:
                mprint("between you and {}, you're the leader".format(shandle))
                leader.value = True
        else:
                mprint("object not for dry run")
                err = graspi.end_negotiate(asa_handle, shandle, True)
                if not err:
                    mprint("end_negotiation error {}".format(graspi.etext[err]))

time.sleep(10)

while KEEP_GOING:
    err, shandle, answer = graspi.listen_negotiate(asa_handle, leader)
    if err:
        mprint("listen_negotiation error: {}".format(graspi.etext[err]))
    else:
        negotiator(shandle, answer).start()
        