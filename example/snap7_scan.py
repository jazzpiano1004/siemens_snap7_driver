import snap7
import time
import argparse





if __name__ == '__main__':

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--address", help="IP Address of target PLC", action="store", type=str, default="0.0.0.0")
    args = vars(ap.parse_args())
    
    client = snap7.client.Client()
    rack_num = 0
    slot_num = 0
    ip_address = args["address"]
    connected_val_pair = []
    while True:
        if client.get_connected() == False:
            try:
                print("connect to {}, rack={}, num={}".format(ip_address, rack_num, slot_num))
                client.connect(ip_address, rack_num, slot_num) #('IP-address', rack, slot)
            
            except Exception as e:
                rack_num += 1
                if rack_num >= 3:
                    slot_num += 1
                    if slot_num >= 9:
                        slot_num = 0
                continue
        else:
            print('connected at {}, {}'.format(rack_num, slot_num))
            connected_val_pair.append((rack_num, slot_num))

        time.sleep(1)

