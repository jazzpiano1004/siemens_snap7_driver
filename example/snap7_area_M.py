import snap7
import time
import sys
import argparse









if __name__ == '__main__':

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--address", help="IP Address of target PLC", action="store", type=str, default="0.0.0.0")
    ap.add_argument("-r", "--rack", help="Rack number of target PLC", action="store", type=int, default=0)
    ap.add_argument("-s", "--slot", help="Slot number of target PLC", action="store", type=int, default=0)
    args = vars(ap.parse_args())


   
    # create snap7 client object
    client = snap7.client.Client()

    # connect to PLC
    PLC_ip_address = args["address"]
    rack_num = args["rack"]
    slot_num = args["slot"]
    timeout = 0
    print("connect to PLC : {}".format(PLC_ip_address))
    while client.get_connected() == False and timeout < 50:
        try:
            client.connect(PLC_ip_address, rack_num, slot_num)
        except Exception as e:
            continue
        timeout += 1
        time.sleep(0.1)
        if timeout == 50:
            print("PLC connect timeout")

    if client.get_connected() == True:
        print("Read from area MK : Merk (M)")
        try:
           pos = int(input("start_pos of M : "))
           while True:
              area = snap7.types.S7AreaMK
              read_value = client.read_area(area=area, dbnumber=0, start=pos, size=1)
              print(read_value)
              time.sleep(1)
        except KeyboardInterrupt:
            print("Read exit")

        print("Write to area MK : Merk (M)")
        try:
           while True:
               user_input = input("start_pos of M, write_value: ")
               if user_input != 'q':
                   pos, write_value =  user_input.split(',')
                   pos = int(pos)
                   import struct
                   write_value = struct.pack('i', int(write_value))
                   print(pos)
                   print(write_value)
                   print(type(write_value))
                   area = snap7.types.S7AreaMK
                   client.write_area(area=area, dbnumber=0, start=pos, data=write_value)
               else:
                   print("Write exit")
                   sys.exit(0)
        except KeyboardInterrupt:
            print("Write exit")
