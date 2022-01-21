from server_lib import *

LAST_UPDATE = os.stat(MAP_PATH).st_mtime
MY_ADDRESS, NEIGHBORS = readmap(MAP_PATH)
keep_going = True

print("*to autonomic network and beyond!*")
value = {MY_ADDRESS:NEIGHBORS}
err, asa_handle = ASA_REG("TD_Server")
map, err = OBJ_REG("map", value, False, True, 10, asa_handle)
if err:
    exit()

#creating tagged objective
tagged_map = TAG_OBJ(map, asa_handle)

flooder(tagged_map, asa_handle).start()

map2, err = OBJ_REG("map2",  value, True, False, 10, asa_handle)
if err:
    exit()


observer_server(LAST_UPDATE, map).start()


while True:
    mprint("listening for negotiation requests")
    err, shandle, answer = graspi.listen_negotiate(asa_handle, map2)
    
    if err:
        mprint("listen_negotiate error\n\t" + graspi.etext[err])
        time.sleep(5)
    else:
        mprint("listen negotiation succeed")
        negotiator(asa_handle, map2, shandle, answer, map, tagged_map).start()
        
    try:
        if not graspi.checkrun(asa_handle, "TD_Server"):
            keep_going = False  
    except:
        pass
