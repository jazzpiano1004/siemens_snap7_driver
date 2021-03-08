import snap7
import time



if __name__ == '__main__':
    client = snap7.client.Client()



    # connect to PLC
    rack_num = 0
    slot_num = 0
    timeout = 0
    while client.get_connected() == False and timeout < 50:
        try:
            client.connect('192.168.5.111', rack_num, slot_num)
        except Exception as e:
            continue
        timeout += 1
        time.sleep(0.1)
        if timeout == 50:
            print("PLC connect timeout")

    if client.get_connected() == True:
        print("testing read from area PE : Process Input (I)")
        while True:
            area = snap7.types.S7AreaPE
            data = client.read_area(area=area, dbnumber=0, start=0, size=1)
            print(data)
            time.sleep(1)
