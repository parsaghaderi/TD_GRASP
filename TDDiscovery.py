import cbor
import cbor2
import grasp
import time

#utility function
def pr(msg):
    print("\n############################")
    print("#" + msg)
    print("############################\n")


#register asa
err, asa_handle = grasp.register_asa("flooder")
if not err:
    pr("ASA registered ok")
else:
    pr("can't register ASA")

#register objetive
obj = grasp.objective("TD")
obj.loop_count = 10
obj.synch = True

err = grasp.register_obj(asa_handle, obj)
if not err:
    pr("objective registered ok")
else:
    pr("can't register objective")
    exit()
time.sleep(30)
#try synchronize
pr("synchronizing")
err, result = grasp.synchronize(asa_handle, obj, None, 5000)
if not err:
    pr("synchronized objective")
    pr(result.value)
else:
    pr("couldn't synchronize objective")
    exit()
