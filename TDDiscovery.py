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

############################
# Registering ASA and object
############################
err, asa_handle = graspi.register_asa("TD_Discovery")
if not err:
    print("ASA registered OK")
else:
    print("can not register ASA: "+graspi.etext[err])

topology = graspi.objective("topology")
topology.synch = True
topology.neg = False

err = graspi.register_obj(asa_handle, topology, overlap=True)
if not err:
    print("Object registered OK!")
else:
    print("cannot register object: "+graspi.etext[err])

err, result = graspi.synchronize(asa_handle, topology, None, 5000)
if not err:
    print("synchronized objective: "+result.value)
else:
    print("can't synchronize objective: "+graspi.etext[err])
    