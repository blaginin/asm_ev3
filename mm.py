import serial
import time
from ev import ev
import os


def insideinit():
    global A, B, C, D, allm
    letters = 'ABCD'
    A = ev(port='A')
    B = ev(port='B')
    C = ev(port='C')
    D = ev(port='D')
#MOTORS_A = ev(port='D')

    A.absolute = True
    B.absolute = True
    C.absolute = True
    D.absolute = True

    A.position = 0
    B.position = 0
    C.position = 0
    D.position = 0

#for a in letters:
#    eval('MOTORS_'+a+" = ev(port='"+a+"')")
 #   eval('\tMOTORS_'+a+'.absolute = True')
  #  eval('\tMOTORS_'+a+'.position = 0')
 
#MOTORS_A = ev(port='D')
#MOTORS_A.absolute = True
#MOTORS_A.position = 0

#AB = [MOTORS_A, MOTORS_B]
#CD = [MOTORS_C, MOTORS_D]

#A2
#b5
#c4
#d3

    allm = [B, C, D]
#42-35
insideinit()
USE_SP = 3

def deviation_list(lst):
    average = sum(lst)/len(lst)
    return([abs(i-average) for i in lst])



def direct(speed, motors):
    hh = [[] for i in range(len(motors))]
    stopn = 0
    print("DIRECT MOTORS", motors)
    for motor in motors:
        print(motor.port)
        motor.run_forever(speed_sp=0)
        motor.write_value('estop', '0')
        motor.write_value('reset', '1')
        motor.run_forever(speed)
    while True:
        for ind, motor in enumerate(motors):
            if motor is None: continue
#            print(hh, ind, motors)
            hh[ind].append(motor.position)
            if len(hh[ind]) > USE_SP:
                del(hh[ind][0])
                ans = deviation_list(hh[ind])
            #print(ans)
                if sum(ans) / len(ans) < 1: 
                     motor.write_value('stop_mode', 'hold')
                     motors[ind] = None
                     stopn += 1
                     if stopn == len(motors): return
                     break

                
def readlineCR(port):
    rv = ""
    while True:
        ch = port.read()
        ch = ch.decode(encoding='ascii')
        rv += ch
        if ch=='\r' or ch=='':
            return rv

port = serial.Serial("/dev/tty_in1", baudrate=115200, timeout=3.0)

print('START LISTEN')
while True:
    msg = readlineCR(port).strip().upper()

    if len(msg) == 0: continue

    if msg == 'PING':
       port.write(bytes(msg+'_PONG', encoding='ascii'))

    if msg.startswith('FREE'):
        print('FREE', msg)
       # os.system('sudo bash /home/mstop.sh')
        motor = eval(msg.split('_')[1])
        motor.write_value('estop', '1')
        #motor.stop()
	
        continue

    if msg == 'INIT':
        insideinit()
        direct(50, allm.copy())

  #      for motor in allm: motor.write_value('estop', '0')
        print('INIT DONE')
        continue
 
    rcv = msg.split('_')
    print(rcv)

 

    if rcv[0].startswith('MR'):
        XY = []
        for i in rcv[0][2:]:
            XY.append(eval(i))

        try:
            speed = -int(rcv[1])
        except BaseException as e:
            port.write(bytes(msg+'_ERR', encoding='ascii'))
            print('err 0', e)
            continue


     #   print('MRAB', MOTORS_A)
        direct(speed, XY)
        #direct(-speed, MOTORS_B)
        port.write(bytes(msg+'_SLEEP', encoding='ascii'))
       # print(msg+'_SLEEP')
        #

#time.sleep(3)
       # direct(-speed, MOTORS_A)
        print(msg+'_OK')
        port.write(bytes(msg+'_OK', encoding='ascii'))
