import cbor
import cbor2
import threading
import time
import datetime
import grasp

#utility function
def pr(msg):
    print("############################")
    print("#" + msg)
    print("############################")

#registering ASA
err, asa_handle = grasp.register_asa("flooder")
if not err:
    pr("ASA registered ok")
else:
    pr("can't register ASA")

#registering obj1 for flood
obj = grasp.objective("TD")
obj.loop_count = 10
obj.sync = True

err = grasp.register_obj(asa_handle, obj)
if not err:
    pr("objective registered ok")
else:
    pr("can't register objective")
    exit()


#flood function 
class flooder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            time.sleep(20)
            obj.value = {'49':['30', '53']}
            grasp.flood(asa_handle, 59000, grasp.tagged_objective(obj, None))#TODO: change to asa_handle and see what happens
            
flooder().start()
pr("Flooding obj1 forever")

#listening for synchronization

obj.value = {'49':['30', '53']}
err = grasp.listen_synchronize(asa_handle, obj)
pr("listening for sync request for obj")