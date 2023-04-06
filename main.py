from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import tkinter as tk
import serial
import threading

import signal

from nidaqmx.constants import AcquisitionType, TaskMode, CountDirection, Edge
from nidaqmx._task_modules.channels.ci_channel import CIChannel
from nidaqmx._task_modules.channel_collection import ChannelCollection
from nidaqmx.constants import AngleUnits
from nidaqmx.constants import AngularVelocityUnits
from nidaqmx.constants import EncoderType

import ctypes
import six
import warnings

from nidaqmx._lib import lib_importer, ctypes_byte_str, c_bool32
from nidaqmx._task_modules.channels.channel import Channel
from nidaqmx._task_modules.export_signals import ExportSignals
from nidaqmx._task_modules.in_stream import InStream
from nidaqmx._task_modules.read_functions import (
    _read_analog_f_64, _read_digital_lines, _read_digital_u_32, _read_ctr_freq,
    _read_ctr_time, _read_ctr_ticks, _read_counter_u_32_ex,
    _read_counter_f_64_ex)
from nidaqmx._task_modules.timing import Timing
from nidaqmx._task_modules.triggers import Triggers
from nidaqmx._task_modules.out_stream import OutStream
from nidaqmx._task_modules.ai_channel_collection import (
    AIChannelCollection)
from nidaqmx._task_modules.ao_channel_collection import (
    AOChannelCollection)
from nidaqmx._task_modules.ci_channel_collection import (
    CIChannelCollection)
from nidaqmx._task_modules.co_channel_collection import (
    COChannelCollection)
from nidaqmx._task_modules.di_channel_collection import (
    DIChannelCollection)
from nidaqmx._task_modules.do_channel_collection import (
    DOChannelCollection)
from nidaqmx._task_modules.write_functions import (
    _write_analog_f_64, _write_digital_lines, _write_digital_u_32,
    _write_ctr_freq, _write_ctr_time, _write_ctr_ticks)
from nidaqmx.constants import (
    AcquisitionType, ChannelType, UsageTypeCI, EveryNSamplesEventType,
    READ_ALL_AVAILABLE, UsageTypeCO, _Save)
from nidaqmx.error_codes import DAQmxErrors
from nidaqmx.errors import (
    check_for_error, is_string_buffer_too_small, DaqError, DaqResourceWarning)
from nidaqmx.system.device import Device
from nidaqmx.types import CtrFreq, CtrTick, CtrTime
from nidaqmx.utils import unflatten_channel_string, flatten_channel_string







def ReadAnalogInput(Dname,ch):
    DD=Dname + '/ai' +str(ch)
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(DD)
        out=task.read()
    return out

def WriteAnalogOutput(Dname,ch,value):
    DD=Dname + '/ao' +str(ch)
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(DD)
        task.write(value)
        
def ReadDigitalInput(Dname,ch):
    DD=Dname + '/port0/line' +str(ch)
    with nidaqmx.Task() as task:
        task.di_channels.add_di_chan(DD)
        out=task.read()
    return out

def WriteDigitalOutput(Dname,ch,value):
    DD=Dname + '/port0/line' +str(ch)
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(DD)
        task.write(value)
       
def ReadAngle(Dname,ch):
    DD=Dname + '/ctr' +str(ch)
    with nidaqmx.Task() as task:
        task.ci_channels.add_ci_ang_encoder_chan(counter = DD, decoding_type = EncoderType.X_4, units=AngleUnits.DEGREES, pulses_per_rev=20)
        ang=task.read()
    return ang


def VoltageOutput(Dname,Vel):
    if Vel>0:
        WriteAnalogOutput(Dname,0,Vel)
        WriteDigitalOutput(Dname,1,True)
        WriteDigitalOutput(Dname,0,False)
    elif Vel<0:
        WriteAnalogOutput(Dname,0,-Vel)
        WriteDigitalOutput(Dname,0,True)
        WriteDigitalOutput(Dname,1,False)

def MotorStop(Dname):
    #WriteDigitalOutput(Dname,0,False)
    #WriteDigitalOutput(Dname,1,False)
    #WriteDigitalOutput(Dname,2,False)
    #WriteDigitalOutput(Dname,3,False)
    WriteDigitalOutput(Dname,4,False)
    WriteDigitalOutput(Dname,5,False)
    #WriteAnalogOutput(Dname,0,0)
    #WriteAnalogOutput(Dname,1,0)
    WriteAnalogOutput(Dname,2,0)
    
def allStop(Dname="Dev4"):
    WriteDigitalOutput(Dname,0,False)
    WriteDigitalOutput(Dname,1,False)
    WriteDigitalOutput(Dname,2,False)
    WriteDigitalOutput(Dname,3,False)
    WriteDigitalOutput(Dname,4,False)
    WriteDigitalOutput(Dname,5,False)

    
def handler(signal, frame):
    MotorStop('Dev4')
    #ser.close
    sys.exit(0)

def grip(LoopT=10, LoopI=10, torqueT=1.6, torqueI=1.1):
    signal.signal(signal.SIGINT, handler)
    Dname='Dev4'
    maxLoop = max(LoopT, LoopI)
    print(maxLoop)
    
    with nidaqmx.Task() as taskCNTIndex, nidaqmx.Task() as taskAOIndex, nidaqmx.Task() as taskDO0Index, nidaqmx.Task() as taskDO1Index,\
        nidaqmx.Task() as taskCNTThumb, nidaqmx.Task() as taskAOThumb, nidaqmx.Task() as taskDO0Thumb, nidaqmx.Task() as taskDO1Thumb:

        taskAOIndex.ao_channels.add_ao_voltage_chan('Dev4/ao1')
        taskDO0Index.do_channels.add_do_chan('Dev4/port0/line2')
        taskDO1Index.do_channels.add_do_chan('Dev4/port0/line3')
        taskCNTIndex.ci_channels.add_ci_ang_encoder_chan(counter = 'Dev4/ctr1', decoding_type = EncoderType.X_4, units=AngleUnits.DEGREES, pulses_per_rev=512, initial_angle=0.0)        

        taskAOThumb.ao_channels.add_ao_voltage_chan('Dev4/ao0')
        taskDO0Thumb.do_channels.add_do_chan('Dev4/port0/line0')
        taskDO1Thumb.do_channels.add_do_chan('Dev4/port0/line1')
        taskCNTThumb.ci_channels.add_ci_ang_encoder_chan(counter = 'Dev4/ctr0', decoding_type = EncoderType.X_4, units=AngleUnits.DEGREES, pulses_per_rev=512, initial_angle=0.0)

        POSIndex=[0 for i in range(LoopI)]
        VELIndex=[0 for i in range(LoopI)]
        OOIndex=[0 for i in range(LoopI)]
        taskAOIndex.start()
        taskDO0Index.start()
        taskDO1Index.start()
        taskCNTIndex.start()
        VelIndex=0
        PangIndex=0
    
        POSThumb=[0 for i in range(LoopT)]
        VELThumb=[0 for i in range(LoopT)]
        OOThumb=[0 for i in range(LoopT)]
        taskAOThumb.start()
        taskDO0Thumb.start()
        taskDO1Thumb.start()
        taskCNTThumb.start()
        VelThumb=0
        PangThumb=0

        TIME=[0 for i in range(maxLoop)]
        A=time.time()
        for i in range(maxLoop):
          # Index
          if i < LoopI:
            angIndex=taskCNTIndex.read()
            VelIndex=0.95*VelIndex+0.05*(angIndex-PangIndex)/10
            PangIndex=angIndex
            ooIndex= torqueI

            if ooIndex>0:
              if ooIndex>10:
                  ooIndex=10
              taskAOIndex.write(ooIndex)
              taskDO0Index.write(True)
              taskDO1Index.write(False)
            else:
              if ooIndex<-10:
                  ooIndex=-10
              taskAOIndex.write(-ooIndex)
              taskDO1Index.write(True)
              taskDO0Index.write(False)

            POSIndex[i]=angIndex
            VELIndex[i]=VelIndex
          
          # Thumb
          if i < LoopT:
            angThumb=taskCNTThumb.read()
            VelThumb=0.95*VelThumb+0.05*(angThumb-PangThumb)/10
            PangThumb=angThumb
            ooThumb=torqueT

            if ooThumb>0:
              if ooThumb>10:
                ooThumb=10
              taskAOThumb.write(ooThumb)
              taskDO0Thumb.write(True)
              taskDO1Thumb.write(False)
            else:
                if ooThumb<-10:
                  ooThumb=-10
                taskAOThumb.write(-ooThumb)
                taskDO1Thumb.write(True)
                taskDO0Thumb.write(False)
            POSThumb[i]=angThumb
            VELThumb[i]=VelThumb
          
          TIME[i]=time.time()-A
    
def wrist(torque, LoopN=300):
  with nidaqmx.Task() as taskCNT, nidaqmx.Task() as taskAO, nidaqmx.Task() as taskDO0, nidaqmx.Task() as taskDO1, nidaqmx.Task():
    taskAO.ao_channels.add_ao_voltage_chan('Dev4/ao2')
    taskDO0.do_channels.add_do_chan('Dev4/port0/line4')
    taskDO1.do_channels.add_do_chan('Dev4/port0/line5')
    taskCNT.ci_channels.add_ci_ang_encoder_chan(counter = 'Dev4/ctr2', decoding_type = EncoderType.X_4, units=AngleUnits.DEGREES, pulses_per_rev=512, initial_angle=0.0) 

    POSWrist=[0 for i in range(LoopN)]
    VELWrist=[0 for i in range(LoopN)]
    OOWrist=[0 for i in range(LoopN)]
    taskAO.start()
    taskDO0.start()
    taskDO1.start()
    taskCNT.start()
    VelWrist=0
    PangWrist=0

    TIME=[0 for i in range(LoopN)]
    A=time.time()
    for i in range(LoopN):
      angWrist = taskCNT.read()
      VelWrist=0.95*VelWrist+0.05*(angWrist-PangWrist)/10
      PangWrist=angWrist
      ooWrist=torque #torque for wrist = 0.2/10
      
      if ooWrist>0:
        if ooWrist>10:
          ooWrist=10
        taskAO.write(ooWrist)
        taskDO0.write(True)
        taskDO1.write(False)
      else:
        if ooWrist<-10:
            ooWrist=-10
        taskAO.write(-ooWrist)
        taskDO1.write(True)
        taskDO0.write(False)

      POSWrist[i]=angWrist
      VELWrist[i]=VelWrist
      TIME[i]=time.time()-A

    taskAO.stop()
    taskDO0.stop()
    taskDO1.stop()
    taskCNT.stop()

    MotorStop("Dev4")

    """
    OOWrist=[-0.4*(POSWrist[i]-DangWrist)-310*VELWrist[i] for i in range(LoopN)]
    plt.figure("Wrist")
    plt.plot(TIME,OOWrist, "b")
    plt.plot(TIME,POSWrist, "r")
    plt.plot(TIME,VELWrist, "g")
      """
      
def start_torque():
    torques_string = torque_textfield.get("1.0", tk.END)
    torques_list = torques_string.split("\n")

    for torque in torques_list:
        try:
            torque_float = float(torque)
            print(torque_float)
            if abs(torque_float) > 0.2:
                print(f"{torque} is too high")
            else:
                wrist(torque_float)
        except ValueError:
            pass
    MotorStop("Dev4")

def start_stage():
    ser = serial.Serial('COM6',38400,timeout=4)
    if not ser.isOpen():
        ser.open()

    XSpeedTable = b"AXI1:SELectSPeed 6\r"
    YSpeedTable = b"AXI2:SELectSPeed 6\r"

    ser.write(XSpeedTable)
    ser.write(YSpeedTable)

    commands_string = stage_textfield.get("1.0", tk.END)
    commands_list = commands_string.split("\n")

    for command in commands_list:
        if "," in command: #run simultaneous
            x, y = list(map(int, command.split(",")))
            DoubleActionCommand(ser,x,y)
        elif "X" in command:
            x = int(command[1:])
            SingleActionCommand(ser,x,1)
        elif "Y" in command:
            y = int(command[1:])
            SingleActionCommand(ser,y,2)
        else:
            print("Unknown command.")
    print("start")
    ser.close()

def start_all():
    t = threading.Thread(target=start_torque)
    s = threading.Thread(target=start_stage)

    t.start()
    s.start()


def SingleActionCommand(ser,pos,N):
    com="AXI"+str(N)+":GOABS "+str(pos)+"\r"
    motion="AXI"+str(N)+":MOTION?\r"
    bcom=com.encode()
    bmotion=motion.encode()
    ser.write(bcom)
    read=b'1'
    while True:
        ser.write(bmotion)
        while read!='\r':
            tread=read #save previous read in tread
            read = ser.read().decode()
        read=b'1'

        if tread == "0": #compare previous read, read contains "\r"
            print("Done")
            break

def DoubleActionCommand(ser,pos1,pos2):
    com1="AXI1:GOABS "+str(pos1)+"\r"
    com2="AXI2:GOABS "+str(pos2)+"\r"
    motion1="AXI1:MOTION?\r"
    motion2="AXI2:MOTION?\r"
    bcom1=com1.encode()
    bcom2=com2.encode()
    bmotion1=motion1.encode()
    bmotion2=motion2.encode()
    ser.write(bcom1)
    ser.write(bcom2)
    read=b'1'
    while True:
        ser.write(bmotion1)
        while read!='\r':
            tread=read
            read = ser.read().decode()
        read=b'1'
#        print(N, tread)
            #time.sleep(0.1)
        if tread == "0":
                break
    while True:
        ser.write(bmotion2)
        while read!='\r':
            tread=read
            read = ser.read().decode()
        read=b'1'
#        print(N, tread)
            #time.sleep(0.1)
        if tread == "0":
                print("Done")
                break

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Robotic Control - Drawing Arm")
    window.geometry("400x300")
    window.columnconfigure(0, minsize=250)
    window.rowconfigure([0, 1], minsize=100)
    
    label = tk.Label(
        text="Hello, Tkinter",
        foreground="red",  # Set the text color to white
        bg="white"  # Set the background color to black
    )
    
    stop_button = tk.Button(
        text="Stop",
        width=5,
        height=1,
        bg="blue",
        fg="yellow",
        command=allStop
    )
    
    tf = tk.Frame()
    tf.pack(fill=tk.X, ipadx=5, ipady=5)

    stage_textfield = tk.Text(
        width=20, 
        height=20,
        master=tf
    )
    stage_textfield.pack(side=tk.LEFT, ipadx=10)

    torque_textfield = tk.Text(
        width=20, 
        height=20,
        master=tf
    )
    torque_textfield.pack(side=tk.LEFT, ipadx=10)
    
    buttons = tk.Frame()
    buttons.pack(fill=tk.X)
    torque_start_button = tk.Button(
        text="Start Torque",
        width=7,
        height=2,
        bg="blue",
        fg="yellow",
        command=start_torque,
        master=buttons
    )
    stage_start_button = tk.Button(
        text="Start Stage",
        width=7,
        height=2,
        bg="blue",
        fg="yellow",
        command=start_stage,
        master=buttons
    )

    everything_start_button = tk.Button(
        text="Start everything",
        width=7,
        height=2,
        bg="blue",
        fg="yellow",
        command=start_all,
        master=buttons       
    )

    stop_button = tk.Button(
        text="Stop",
        width=7,
        height=2,
        bg="blue",
        fg="yellow",
        command=allStop,
        master=buttons
    )
    
    grip_start_button = tk.Button(
        text="Start grip",
        width=7,
        height=2,
        bg="blue",
        fg="yellow",
        command=grip,
        master=buttons
    )
    torque_start_button.pack(side=tk.LEFT, padx=5, pady=5)
    everything_start_button.pack(side=tk.LEFT, padx=5, pady=5)
    stop_button.pack(side=tk.LEFT, padx=5, pady=5)
    grip_start_button.pack(side=tk.LEFT, padx=5, pady=5)
    stage_start_button.pack(side=tk.LEFT, padx=5, pady=5)

    signal.signal(signal.SIGINT, handler)
    window.mainloop()
