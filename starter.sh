#/usr/bin/bash
cd /home/asm_ev3
if ![/bin/ps awx | /bin/grep mm.py] then  /bin/python3 mm.py; fi
