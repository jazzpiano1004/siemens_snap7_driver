import snap7
import struct



class snap7_client():

    def __init__(self, ip_address, rack, slot):
        self.client = snap7.client.Client()
        self.ip_address = ip_address
        self.rack = rack
        self.slot = slot

    def connect(self):
        if self.client.get_connected() == False:
            ret = self.client.connect(self.ip_address, self.rack, self.slot)
            return ret
        else:
            return True

    def get_plc_state(self):
        ret = self.client.get_cpu_state()
        return ret

    def set_plc_state(self, cmd:str):
        ret = None
        if cmd == 'stop':
            ret = self.client.plc_stop()
        elif cmd == 'cold start':
            ret = self.client.plc_cold_start()
        elif cmd == 'hot start':
            ret = self.client.plc_hot_start()
        return ret
    
    def readbyte_area_I(self, address):
        area = snap7.types.S7AreaPE
        bytearr = self.client.read_area(area=area, dbnumber=0, start=address, size=1)
        val = bytearr[0]
        return val

    def readbit_area_I(self, address, bit):
        byte = self.readbyte_area_I(address)
        val = (byte & (2**bit)) >> bit
        return val

    def readbyte_area_Q(self, address):
        area = snap7.types.S7AreaPA
        bytearr = self.client.read_area(area=area, dbnumber=0, start=address, size=1)
        val = bytearr[0]
        return val

    def readbit_area_Q(self, address, bit):
        byte = self.readbyte_area_Q(address)
        val = (byte & (2**bit)) >> bit
        return val

    def writebyte_area_Q(self, address, byteval):
        bytearr = struct.pack('i', byteval)
        area = snap7.types.S7AreaPA
        self.client.write_area(area=area, dbnumber=0, start=address, data=bytearr)

    def writebit_area_Q(self, address, bit, bitval):
        curr_val = self.readbyte_area_Q(address)
        if bitval != 0:
            tmp = curr_val | 2**bit
        else:
            tmp = curr_val & ~(2**bit)
        self.writebyte_area_Q(address, tmp)

    def readbyte_area_M(self, address):
        area = snap7.types.S7AreaMK
        bytearr = self.client.read_area(area=area, dbnumber=0, start=address, size=1)
        val = bytearr[0]
        return val

    def readbit_area_M(self, address, bit):
        byte = self.readbyte_area_M(address)
        val = (byte & (2**bit)) >> bit
        return val

    def writebyte_area_M(self, address, byteval):
        bytearr = struct.pack('i', byteval)
        area = snap7.types.S7AreaMK
        self.client.write_area(area=area, dbnumber=0, start=address, data=bytearr)

    def writebit_area_M(self, address, bit, bitval):
        curr_val = self.readbyte_area_M(address)
        if bitval != 0:
            tmp = curr_val | 2**bit
        else:
            tmp = curr_val & ~(2**bit)
        self.writebyte_area_M(address, tmp)
    
    def read_DB(self, db_number, address, dtype):
        if dtype == 'BOOL':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=1)
            if int(bytearr[0]) != 0:
                read_val = True
            else:
                read_val = False
            return read_val

        elif dtype == 'BYTE':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=1)
            read_val = (struct.unpack('>B', bytearr))[0]
            return read_val
        
        elif dtype == 'WORD':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=2)
            read_val = (struct.unpack('>H', bytearr))[0]
            return read_val

        elif dtype == 'INT':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=2)
            read_val = (struct.unpack('>h', bytearr))[0]
            return read_val

        elif dtype == 'DINT':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=4)
            read_val = (struct.unpack('>i', bytearr))[0]
            return read_val

        elif dtype == 'CHAR':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=1)
            read_val = bytearr.decode('UTF-8')
            return read_val

        elif dtype == 'REAL':
            bytearr = self.client.db_read(db_number=db_number, start=address, size=4)
            read_val = (struct.unpack('>f', bytearr))[0]  
            return read_val

        else:
            return None

    def write_DB(self, db_number, address, dtype, val):
        if dtype == 'BOOL':
            bytearr = struct.pack('?', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        elif dtype == 'BYTE':
            bytearr = struct.pack('>B', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        elif dtype == 'WORD':
            bytearr = struct.pack('>H', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        elif dtype == 'INT':
            bytearr = struct.pack('>h', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)
        
        elif dtype == 'DINT':
            bytearr = struct.pack('>i', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        elif dtype == 'CHAR':
            bytearr = val.encode('UTF-8')
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        elif dtype == 'REAL':
            bytearr = struct.pack('>f', val)
            self.client.db_write(db_number=db_number, start=address, data=bytearr)

        else:
            return None



if __name__ == '__main__':
    
    import time
    import argparse
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--address", help="IP Address of target PLC", action="store", type=str, default="0.0.0.0")
    ap.add_argument("-r", "--rack", help="Rack number of target PLC", action="store", type=int, default=0)
    ap.add_argument("-s", "--slot", help="Slot number of target PLC", action="store", type=int, default=0)
    ap.add_argument("-t", "--type", help="Test type (c, i, q, m, db)", action="store", type=str, default='c')
    args = vars(ap.parse_args())


    dev = snap7_client(ip_address=args["address"], rack=args["rack"], slot=args["slot"])
    print("connect to plc ...")
    while not dev.connect():
        time.sleep(0.1)
    print("connected!\n")
    
    if args["type"] == 'c':
        print("get, set state of PLC testing")
        while True:
            current_state = dev.get_plc_state()
            print("cur=" + str(current_state))
            set_state = input("\tset state : ")
            if set_state != 'q':
                dev.set_plc_state(set_state)
            else:
                break
            time.sleep(0.1)

    elif args["type"] == 'i':
        print("Read from area PE : Process Input (I)")
        try:
            while True:
                user_input = input("start_address of I, bit : ")
                if user_input == 'q':
                    print("Read exit")
                    break
                else:
                    user_input = user_input.split(',')
                    addr = int(user_input[0])
                    bit  = int(user_input[1])
                    read_val = dev.readbit_area_I(addr, bit)
                    print(read_val, type(read_val))
               
        except KeyboardInterrupt:
            print("Read exit")

    elif args["type"] == 'q':
        print("Read from area PA : Process Output (Q)")
        try:
            while True:
                user_input = input("Q address, bit : ")
                if user_input == 'q':
                    print("Read exit")
                    break
                else:
                    user_input = user_input.split(',')
                    addr = int(user_input[0])
                    bit  = int(user_input[1])
                    read_val = dev.readbit_area_Q(addr, bit)
                    print(read_val, type(read_val))
        except KeyboardInterrupt:
            print("Read exit")

        print("Write to area PA : Process Output (Q)")
        try:
           while True:
               user_input = input("Q addres, bit, value : ")
               if user_input != 'q':
                   user_input = user_input.split(',')
                   addr = int(user_input[0])
                   bit  = int(user_input[1])
                   write_val = int(user_input[2])
                   dev.writebit_area_Q(addr, bit, write_val)
               else:
                   print("Write exit")
                   break
        except KeyboardInterrupt:
            print("Write exit")

    elif args["type"] == 'db':
        print("Read from area DB")
        try:
            while True:
                user_input = input("DB num, DB address, Datatype : ")
                if user_input == 'q':
                    print("Read exit")
                    break
                else:
                    user_input = user_input.split(',')
                    db_num = int(user_input[0])
                    addr = int(user_input[1])
                    dtype = user_input[2]
                    read_val = dev.read_DB(db_num, addr, dtype)
                    print(read_val, type(read_val))
        except KeyboardInterrupt:
            print("Read exit")

        print("Write to area DB")
        try:
            while True:
                user_input = input("DB num, DB address, Datatype, Val : ")
                if user_input == 'q':
                    print("Read exit")
                    break
                else:
                    user_input = user_input.split(',')
                    db_num = int(user_input[0])
                    addr = int(user_input[1])
                    dtype = user_input[2]
                    if dtype != 'CHAR':
                        write_val = eval(user_input[3])
                    else:
                        write_val = user_input[3]
                    dev.write_DB(db_num, addr, dtype, write_val)

        except KeyboardInterrupt:
            print("Write exit")
