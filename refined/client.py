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
import sys
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
    graspi.tprint("ASA client is starting up.")
    graspi.tprint("========================")


###############################
#registering objective and ASA
###############################
mprint("registering asa and objective")
err, asa_handle = graspi.register_asa("TD_client")
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

#############################
#synchronizing map
#############################
class sync(threading.Thread):
    def __init__(self, tagged):
        threading.Thread.__init__(self)
        self.obj = tagged.objective
        self.asa = tagged.source
        self.tagged = tagged
    def run(self):
        while True:
            if keep_going:
                mprint("synchronizing map objective")
                err, result = graspi.synchronize(self.asa, self.obj, None, 5000)
                if not err:
                    
                    print("#########################\n")
                    print("map synchronized\n\t")
                    print(result.value)
                    # self.tagged.objective = result 
                    print("#########################\n")
                    # break
                    time.sleep(3)
                else:
                    mprint("cannot synchronize value\n\t"+graspi.etext[err])
            time.sleep(1)

tagged_map = graspi.tagged_objective(map, asa_handle)
sync(tagged_map).start()

################################
# negotiation
################################
map2 = graspi.objective("map2")
map2.neg = True
map2.synch = False
map2.loop_count = 10
map2.value = {sys.argv[1]:sys.argv[2:]}
err = graspi.register_obj(asa_handle, map2)
if not err:
    mprint("object registered successfully")
else:
    mprint("cannot register objective "+graspi.etext[err])
    mprint("exiting now")
    exit()
failcnt =0
_cbor = True
mprint("start negotiation")
while keep_going:
    _, ll = graspi.discover(asa_handle, map2, 10000, flush=True)
    
    if ll ==[]:
        mprint("discovery failed")
        mprint("exiting now")
        exit()
    print("###############################")
    print("discovered locator \n\t")
    print(ll[0].locator)
    print("###############################")

    print("###############################")
    print("list of discovered locator\n\t")
    for x in ll:
        print(x.locator)
    print("###############################")
    if _cbor:
        map2.value=cbor.dumps(map2.value)
        mprint("value encoded")
    if _old_API:
        mprint("old_api true")
        err, nhandle, answer = graspi.req_negotiate(asa_handle, map2, ll[0], None)
        reason = answer
    else:
        mprint("old_api false")#√
        err, nhandle, answer, reason = graspi.request_negotiate(asa_handle, map2, ll[0], None)#√
    
    if err:
        if err==graspi.errors.declined and reason!="":
            _e = reason
        else:
            _e = graspi.etext[err]
        mprint("request_negotiate error: "+ _e)
        failcnt+=1
        print("########################")
        print("fail count:\n\t")
        print(failcnt)
        print("########################")

        time.sleep(5)
    elif (not err) and nhandle:
        
        mprint("requested {}".format(answer.name))#√
        if _cbor:
            mprint(answer.value)#√
        map2.value = cbor.loads(map2.value)#√
        mprint("peer offered {}".format(answer.value))#√
        map2.value.update(answer.value)#√

        mprint("updated value for map2 {}".format(map2.value))#√
        #answer.value = cbor.dumps(map2.value) #TODO
        _r = graspi.negotiate_step(asa_handle, nhandle, answer, 1000)
        if _old_API:
            err, temp, answer = _r
            reason = answer
        else:
            err, temp, answer, reason = _r
        if _cbor and (not err):
            try:
                answer.value = cbor.loads(answer.value)
            except:
                pass
        if (not err) and temp == None:
            mprint("negotiation succeeded")
            mprint("updated value of answer: "+answer.value)
            map2.value = answer.value
        else:
            mprint("negotiation error "+graspi.etext[err])
            mprint("exiting now")
            exit()
        err = graspi.end_negotiate(asa_handle, nhandle, True)
        if not err:
            print("##############################################")
            print("negotiation ended successfully with answer\n\t")
            print(map2.value)
            print("##############################################\n")
        else:
            mprint("end negotiation error: "+graspi.etext[err])
        
    else:
        err = graspi.end_negotiate(asa_handle, nhandle, True)
        if not err:
            print("##############################################")
            print("negotiation ended successfully with answer\n\t")
            print(map2.value)
            print("##############################################\n")
        else:
            mprint("end negotiation error: "+graspi.etext[err])

