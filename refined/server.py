from server_lib import *
_old_API = False
#TODO: delete this part
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


LAST_UPDATE = os.stat('/etc/TD_map/neighbors.map').st_mtime
MY_ADDRESS, NEIGHBORS = readmap(MAP_PATH)
keep_going = True

print("to the code and beyond!")

err, asa_handle = ASA_REG("TD_Server")
map, err = OBJ_REG("map", {MY_ADDRESS:NEIGHBORS}, False, True, 10, asa_handle)
if err:
    exit()

#creating tagged objective
tagged_map = TAG_OBJ(map, asa_handle)

flooder(tagged_map, asa_handle).start()


#####################################
# creating objective for negotiation
#####################################
# map2 = graspi.objective("map2")
# map2.neg = True
# map2.synch = False
# map2.loop_count = 10
# map2.value = {MY_ADDRESS:NEIGHBORS}
# err = graspi.register_obj(asa_handle, map2)
# if not err:
#     mprint("objective map2 registered correctly")
# else:
#     mrpint("cannot register map2\n\t" + graspi.etext[err])
#     mprint("exiting now")
    
#     exit()

map2, err = OBJ_REG("map2",  {MY_ADDRESS:NEIGHBORS}, True, False, 10, asa_handle)
if err:
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
        global map
        global map2
        global tagged_map
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
                end_err = graspi.end_negotiate(asa_handle, nhandler, False, reason=None)
                mprint("negotiation succeeded")
                mprint("final result\n {}".format(self.obj.value))
                map.value = self.obj.value
                tagged_map.objective.value = map.value
                if not end_err:
                    mprint("negotiation session ended")
            else:
                print("#########################")
                print("negotiation failed\n\t")
                print(graspi.etext[err])
                print(reason)
                print("#########################")
                
observer_server(LAST_UPDATE, map).start()
while True:
    mprint("listening for negotiation requests")
    err, shandle, answer = graspi.listen_negotiate(asa_handle, map2)
    
    if err:
        mprint("listen_negotiate error\n\t" + graspi.etext[err])
        time.sleep(5)
    else:
        mprint("listen negotiation succeed")
        negotiator(asa_handle, map, shandle, answer).start()
        
    try:
        if not graspi.checkrun(asa_handle, "TD_Server"):
            keep_going = False  
    except:
        pass
