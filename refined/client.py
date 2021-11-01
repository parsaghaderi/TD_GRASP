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

if keep_going:
    mprint("synchronizing map objective")
    err, result = graspi.synchronize(asa_handle, map, None, 5000)
    if not err:
        mprint("map synchronized; map value: " + result.value)
    else:
        mprint("cannot synchronize value\n\t"+graspi.etext[err])
        mprint("exiting now")
        exit()