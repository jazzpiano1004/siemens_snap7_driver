# Import from driver
"""
from pymodbus.client.asynchronous.serial import (AsyncModbusSerialClient as ModbusClient)
from pymodbus.client.asynchronous.tcp import (AsyncModbusTCPClient as ModbusTCPClient)
from pymodbus.client.asynchronous import schedulers
"""
from drivers.siemens_snap7.snap7_driver import *
from asyncio.futures import TimeoutError
from tag.models import Tag

# Import from worker.py
from drivers.worker import UpdateTag


class SyncSiemensSnap7():
    action_list=[]
    ACTION_READ=0
    ACTION_WRITE=1
    UNIT = 0x02
    is_aborted=False
    VALUE2SIZE={"float":2,
            "int":2,
            }
    def __init__(self,port,loop):
        self.port_name=port.detail['port']
        self.action_dict=dict()
        self.port=port
        self.loop=loop

    def Create_Connection(self):
        port = self.port
        client = snap7_client(ip_address=port.detail['address'], rack=port.detail['rack'], slot=port.detail['slot'])
        if not client.get_connected():
            client.connect()
        return client

    def ReadAll(self,pool):
        from tag.models import Device
        for device in Device.objects.filter(port=self.port):
            client=self.Create_Connection()
            for tag in Tag.objects.filter(device=device):
                log.info('read: '+tag.full_name)
                self.loop.run_until_complete(self.ReadTag(pool,client,tag.full_name))
            client.close()

    async def CheckResponseAndUpdateTag(self,pub,tag,response):
        log.info('Is read error:'+str(response.isError()))
        if response.isError():
            pass
        else:
            value = str(self.Decode(response.registers,tag.value_type))
            await UpdateTag(pub,tag,value)

    async def ReadTag(self,pool,client,tag):
        from tag.models import Tag
        from datetime import datetime
        pub=pool.pub
        t=Tag.objects.get(full_name=tag)
        log.info('device: '+t.device.address+'  tag_address: '+t.address)
        
        #client.framer.resetFrame()
        tag_type_db = {
                'S7AreaDB BOOL':'BOOL', 
                'S7AreaDB BYTE':'BYTE', 
                'S7AreaDB WORD':'WORD', 
                'S7AreaDB INT':'INT', 
                'S7AreaDB DINT':'DINT',
                'S7AreaDB REAL':'REAL',
                'S7AreaDB CHAR':'CHAR'
                }
        if t.type in ['S7AreaPE', 'S7AreaPA', 'S7AreaMK']:
            log.info("Read S7AreaPE (I)")
            # Address has 2 components, Area address and bit
            # t.address = address, bit
            t_addr = t.address.split(',')
            addr = int(t_addr[0])
            bit  = int(t_addr[1])
            if t.type == 'S7AreaPE':
                rr = client.readbit_area_I(addr, bit)
            elif t.type == 'S7AreaPA':
                rr = client.readbit_area_Q(addr, bit)
            elif t.type == 'S7AreaMK':
                rr = client.readbit_area_M(addr, bit)
            await self.CheckResponseAndUpdateTag(pub,t,rr)
        elif t.type in tag_type_db:
            log.info("Read S7AreaDB (DB) : Type {}".format(tag_type_db[t.type]))
            # Address for db has 2 components, db number and address
            # t.address = db number, address
            t_addr = t.address.split(',')
            db_num  = int(t_addr[0])
            db_addr = int(t_addr[1])
            rr = client.read_DB(db_num, db_addr, tag_type_db.get(t.type))
            await self.CheckResponseAndUpdateTag(pub,t,rr)
        else:
            log.info("Unknown or unimplemented Read function.")

        
    def __done(self,future,text=''):
        log.info(text+"Done !!!")
        
    def WriteTag(self,tag,value):
        client=self.Create_Connection()
        log.info('siemens snap7 write ') 
        from tag.models import Tag
        t=Tag.objects.get(full_name=tag)
        log.info('device:'+t.device.address+'  address:'+t.address+'  value:'+str(value))

        if t.type in ['S7AreaPE', 'S7AreaPA', 'S7AreaMK']:
            # Address has 2 components, Area address and bit
            # t.address = address, bit
            t_addr = t.address.split(',')
            addr = int(t_addr[0])
            bit  = int(t_addr[1])
            if t.type == 'S7AreaPE':
                client.writebit_area_I(addr, bit, value)
            elif t.type == 'S7AreaPA':
                client.writebit_area_Q(addr, bit, value)
            elif t.type == 'S7AreaMK':
                client.writebit_area_M(addr, bit, value)
            error=0
        elif t.type in tag_type_db:
            # Address for db has 2 components, db number and address
            # t.address = db number, address
            t_addr = t.address.split(',')
            db_num  = int(t_addr[0])
            db_addr = int(t_addr[1])
            client.write_DB(db_num, db_addr, tag_type_db.get(t.type), value)
            error=0
        else:
            error=-1
        log.info('isError '+str(error))
        client.close()
        return error

    def RedisWrite(self):
        pass
    def Decode(self,registers,value_type):
        value=self.Decode_Raw(registers,value_type)
        log.info(str(value))
        return value
    def Decode_Raw(self,registers,value_type):
        log.info('raw value :'+str(registers[0]))
        if value_type == 'float':
            from pymodbus.payload import BinaryPayloadDecoder
            from pymodbus.constants import Endian
            decoder = BinaryPayloadDecoder.fromRegisters(registers,byteorder=Endian.Big,wordorder=Endian.Big)
            return decoder.decode_32bit_float()
        elif value_type == 'int':
            from pymodbus.payload import BinaryPayloadDecoder
            decoder = BinaryPayloadDecoder.fromRegisters(registers)
            return decoder.decode_16bit_uint()
        else:
            return registers[0]






from drivers.datapool import WorkerPool,get_scada_redis_client
from drivers.worker import Device_SetTag_Response




class SiemensSnap7Pool(WorkerPool):
    def __init__(self,tags=set(),siemens_snap7=None):
        self.tags=set(tags)
        self.siemens_snap7=siemens_snap7
    async def connect(self):
        self.pub = await get_scada_redis_client()
        self.sub= await get_scada_redis_client()
        await self.add_tags(self.tags)
    async def add_tag(self,tag):
        print('addtag',tag)
        key='settag2:'+tag
        channel = await self.sub.subscribe(key)
        self.tags.add(tag)
        asyncio.ensure_future(self.async_reader(self.pub,channel[0],self.siemens_snap7))
    async def async_reader(self,pub, channel, siemens_snap7):
        while await channel.wait_message():
            #msg = await channel.get(encoding='utf-8')
            msg = await channel.get()#encoding='utf-8')
            # ... process message ...
            print("message in {}: {}".format(channel.name, msg))
            import json 
            request=json.loads(msg.decode())
            tag=channel.name.decode()
            tag_name=channel.name[8:].decode()
            print(tag,tag_name)
            value=request['value']
            response=siemens_snap7.WriteTag(tag_name,value)
            RETURN_CODE2STRING={
                    0:'SUCCESS',
                    1:'ERROR',
                    -1:'',
                    }
            response_status=RETURN_CODE2STRING.get(response,'UNKNOWN')
            await Device_SetTag_Response(pub,request,tag_name,status=response_status)
        print('channel unsub',channel.name)



       

@app.task(bind=True,base=scada_task,abortable=True)
def snap7_task(self,port_id):
    print('task id: '+self.request.id)
    from tag.models import Port
    loop=asyncio.get_event_loop()
    p=Port.objects.get(id=port_id)
    tags=Tag.objects.filter(device__port=p).values_list('full_name',flat=True)
    print('tags  :',tags)
    s=SyncSiemensSnap7(p,loop)
    pool=SiemenSnap7Pool(tags=tags,siemens_snap7=s)
    asyncio.ensure_future(pool.connect())

    while not self.is_aborted():
        #print('main loop')
        loop.run_until_complete(asyncio.sleep(1)) 
        s.ReadAll(pool)
    print("snap7 port"+str(port_id)+" good bye ja.")
