import serial
import time
from ev import ev
import os
import ev3.ev3dev as ev3dev
import ev3dev as evCORE
import sys
#+ = close

screen = evCORE.Lcd()

try:
    color = ev3dev.LegoSensor(port=4)
    color.mode = 'COL-COLOR'
except BaseException:
    pass

try:
    button = ev3dev.LegoSensor(port=3)
except BaseException: pass




def insideinit():
    global A, B, C, D, allm
    letters = 'ABCD'
    A = ev(port='A')
    B = ev(port='B')
    C = ev(port='C')
    D = ev(port='D')
    A.absolute = True
    B.absolute = True
    C.absolute = True
    D.absolute = True
    A.position = 0
    B.position = 0
    C.position = 0
    D.position = 0


insideinit()


#for a in letters:
#    eval('MOTORS_'+a+" = ev(port='"+a+"')")
 #   eval('\tMOTORS_'+a+'.absolute = True')
  #  eval('\tMOTORS_'+a+'.position = 0')
 
#MOTORS_A = ev(port='D')
#MOTORS_A.absolute = True
#MOTORS_A.position = 0

#AB = [MOTORS_A, MOTORS_B]
#CD = [MOTORS_C, MOTORS_D]

allm = [B, C, D, A]
#42-35
USE_SP = 3
LUCK = D


#color.mode = 'COL-COLOR'
N_COLORS = 10
N_COLORS_STOP = 0.9
CLAW_MOTOR = C
m_mark = {"N":1, "M":5, "G":2, "P":3, "S":6}


def run(speed, motors):
    for motor in motors:
        motor.write_value('estop', '0')
        motor.write_value('reset', '1')
        motor.run_forever(speed_sp=speed)


def push():
    for i in range(2*2):
        direct(90 +  (-180)*((i+1)%2), [LUCK], NNIUD=0.4)
        time.sleep(0.5)

def navigate(x, motors, speed):
    x = m_mark[x]
    run(speed, motors)
    colorarray = []
    while True:
        pp = color.value0
        colorarray.append(pp)
        if len(colorarray) < N_COLORS: continue
        del(colorarray[0])
        if colorarray.count(x)/N_COLORS >= N_COLORS_STOP:
#            print('COLOR DONE')
            for motor in motors:
                motor.write_value('stop_mode', 'hold')
                motor.stop()
            direct(-80, [CLAW_MOTOR])
            run(0, [CLAW_MOTOR])
            push()
            run(-speed, motors)
            while not button.value0: pass
            for motor in motors: motor.stop()
            return
#        print('NO', colorarray)

        



def deviation_list(lst):
    average = sum(lst)/len(lst)
    return([abs(i-average) for i in lst])



def direct(speed, motors, NNIUD=1):
    hh = [[] for i in range(len(motors))]
    stopn = 0
#    print("DIRECT MOTORS", motors)
    for motor in motors:
 #       print(motor.port)
        motor.run_forever(speed_sp=0)
        motor.write_value('estop', '0')
        motor.stop()
        motor.write_value('reset', '1')
        motor.run_forever(speed)
    while True:
#        try:
 #           if button.value0:
  #              for motor in motors: 
   #                 if motor is not None: motor.write_value('stop_mode', 'hold')
    #            
     #           return
      #  except BaseException: pass

        for ind, motor in enumerate(motors):
            if motor is None: continue

            while True:
                try:
                    hh[ind].append(motor.position)
                    break
                except BaseException as e: print('YO', e)

            if len(hh[ind]) > USE_SP:
                del(hh[ind][0])
                ans = deviation_list(hh[ind])
                if sum(ans) / len(ans) < NNIUD: 
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
  #      print(ch, end='')
        rv += ch
        if ch=='\r' or ch=='':
            return rv


#navigate("N", [A, B], 50)

port = serial.Serial("/dev/tty_in1", baudrate=115200, timeout=3.0)

print('START LISTEN')
while True:
    msg = " ".join(readlineCR(port).strip().upper().split())
   
    if len(msg) == 0: continue

    screen.reset()
    screen.draw.text((0,0), msg)
    screen.update()

    print('RCV', msg)
    if msg == 'PING':
       port.write(bytes('OK\r', encoding='ascii'))

    if msg.startswith('FREE'):
   #     print('FREE', msg)
       # os.system('sudo bash /home/mstop.sh')
        motor = eval(msg.split('_')[1])
        motor.write_value('estop', '1')
        #motor.stop()
	
        continue

    if msg.startswith('NAVIGATE'):
    #    print('NAVIG', msg)
        cmd = msg.split('_')
        if cmd[1] == 'NONE': 
            push()
            continue

        q = []
        for i in cmd[2]: q.append(eval(i))
        navigate(cmd[1], q, int(cmd[3]) )
        port.write(bytes('OK\r', encoding='ascii'))


    if msg == 'INIT':
        insideinit()
        direct(0, allm.copy())

  #      for motor in allm: motor.write_value('estop', '0')
#        print('INIT DONE')
        continue
 
    rcv = msg.split('_')
 #   print(rcv)

 

    if rcv[0].startswith('MR'):
        XY = []
        for i in rcv[0][2:]:
            XY.append(eval(i))

        try:
            speed = -int(rcv[1])
        except BaseException as e:
            port.write(bytes('ER\r', encoding='ascii'))
            print('err 0', e)
            continue

        direct(speed, XY)    

        port.write(bytes('OK\r', encoding='ascii'))
