# Siemens Snap7 Driver for THOpenSCADA project
This repository is used for develop a python driver for a Siemens' SNAP7 protocol and python-snap7 is used. This python driver will be used later in THOpenSCADA project.
Link of python-snap7 : https://python-snap7.readthedocs.io/en/latest/index.html

The list of main functionality for this driver
- Control RUN state of PLC (STOP, COLD START, HOT START)
- Read/Write Area I, Q, M, DB of snap7

# Tested hardward
- VIPA CPU313 PLC

# How to run and test driver
Run only snap7_driver.py file. Ignore the example folder as it's for an experiment only.<br />

```bash
python snap7_driver.py -h
python snap7_driver.py -a <IP address of PLC> -t <test function>
python snap7_driver.py -a 192.168.5.110 -t db
```
