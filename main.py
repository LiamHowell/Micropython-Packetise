# Liam Howell - 4/8/2022 - MIT License

import PiicoDev_Unified # cross-platform compatible sleep function
from machine import Pin,I2C


from ustruct import *
from re import sub


#pic_i2c = PiicoDev_Unified.create_unified_i2c(bus=None, freq=None, sda=None, scl=None)

#print(dir(pic_i2c))

#print(pic_i2c.scan())



piicodev_addr = { #A list of all PiicoDev sensors and possible addresses
    "Atmo": [0x77,0x76],
    "Light": [0x10, 0x48],
    "Laser distance": [0x29],
    "Magnetometer":[0x3C],
    "RGB": [0x08],
    "Smart module alternate address":[range(9,23)]
}

# class PiicoDevBus(I2CBase,addrs):
# 
# 
#     def __init__(self):
#         
#         addr = I2CBase.scan
#         #Loop through each module doing a 'who am i' (Might be a try except trying to read)
#         
#         return 
    


pack_strings = { # "What is being measured": ["Decorator(?) <UNIQUE>", "Type char (ref ustruct)", "Data source"]
        "Batt": ['Z','H','Batt_Sens','ADC'], # CHANGE TO MSG == BATTERY FAULT WARNING, 2ND MSB == LOW CHARGE (The node decides these)
        "Pckts": ['K','H'],
        "Addr": ['A','H'],
        "Fault":["F",'H',['Fault_exists','FLT1','FLT2','...']],
        
        
        "temp": ['T','H','TMP117','BME280'],
        "Press": ['P','H','MS5637','BME280'],
        "Hum": ['H','H','BME280'],
        "Dist": ['D','H','VL53L1X'],
        "Col": ['C','HHH','VEML6040'],
        "Mag": ['M','HHH','QMC6310'],
        "Btn": ['B','IDK WHAT THIS WILL BE','CAP1203','Buttons'],
        "Time": ['N','RV3028'],
        "Buzz": ['OB','Buzzer'],
        "RGB": ['OL','HHH','RGB'],
        "RFID": ['R','MFRC522'],
        "Joystick": ['J','HH', ['ADC1','ADC2'],'Smart Joystick'],
        "OTHER": ['X']
        }



A1 = 123
A2 = 234
# In format, [prefix, type, data]
example_lst = [['Z','H',410], # >4.1V x 10 = 410
               ['K','H',1],   # >Iterates
               ['A','H',123], # When init and a MAC is given an address should be given, there should exist a handshake to change addresses
               ['J','HH',[A1,A2]], # 2 Shorts(x,y) ranging from 0 - 360 (mapped from -180 - 180)
               ]
    
    
    
    
def typeCheck(dat,formatStr='H',enf=True): # Input data, the respective format string(defaults to short) and if it should be enforced(default True) and parsed back
    _enf_f = False
    if formatStr == 'H': # ustruct unsigned Short
        if dat > 0xFFFF or dat < 0x00:
            if enf:
                dat = dat & 0xFFFF
            else:
                _enf_f = True
    return (dat,_enf_f) #Returns new dat and enforce flag
            
            
def constructVars(curr_data, packed_lst):
    if isinstance(curr_data,list):#type(data) = type(list):
        packed_lst += curr_data
    else:
        packed_lst.append(curr_data)



def packetise(list_of_data,debug=False): # Expects a List of lists 
    format_str='<' #Forces little endian
    output_bytes=''
    dat_char=''
    trypack_lst=list()
    
    for items in list_of_data:
        if typeCheck(items[2],items[1])[1] == False: # Checks if it should be a short,
            dat_char += items[0]
            format_str += items[1]
            constructVars(items[2],trypack_lst)
    format_str += '{}s'.format(len(list_of_data)) # Adds space for the 'decorators' at the end of the string
    trypack_lst.append(dat_char)    
    
    output_bytes = pack(format_str,*trypack_lst)

    if debug:
        debug_lst=[dat_char,format_str,trypack_lst,calcsize(format_str)]
        return [format_str,output_bytes,debug_lst]
    
    return format_str,output_bytes


def unpacketise(frmt,outp):
    lst_out = unpack(frmt,outp)
    rtn_lst = list()
    
    pack_form_el = sub( r"([A-Z])", r" \1", lst_out[-1].decode("utf-8")).split()
    for i, vals in enumerate(pack_form_el):
        for (sens, lst) in pack_strings.items():
            if lst[0] == vals:
                rtn_lst.append([vals,list(lst_out[i:i+len(lst[1])])])
    return rtn_lst

    

#############################################################


print(example_lst)

[fmrt, outp] = packetise(example_lst)


other_end_example_lst = unpacketise(fmrt, outp)

print(other_end_example_lst)




''' Some of dis might be contradicatry to the above code

**Module features:
- no arguments - reads simple sensor data and concatinates it into a long string ready to be transmitted
- List or Dict of addresses/sensor names - only return those ones, also would allow custom prefixes(in a list configured as [prefix STR][addr]...)

**Examples:
Device ID - A - 32 bit address, specifies the module this is arriving from, (BONUS: Make a callable function to get other device ID's connected to the 'hub')

Battery voltage/critical data - Z - Usually Lipo Charge - [<ATTENTION/Operational>, reading<% of charge(4.2-> 3.9V,below 3.9 the flag is switched)]


Packet count - X - defaults to 64 max then rolls over

Temp - T - Prioritise TMP117, otherwise BME280 {:.1f}
Pressure - P - Prio MSxxxx sensor otherwise BME280 {:.2f}
Humidity - H - BME280 {:.1f}
Distance - D - VL53L1X - {:.2f}
Colour - C - VEML6040 - FF:FF:FF -> FFFFFF
Magnetometer - Q - QMC6310 - [0-360.0,0-360.0,0-360.0] - to binary(2^9)? OR read angle(0-360) OR 'is open', 'is close' states
Cap touch/Buttons - B - [0,0,1,0] - list of binary states, OPTIONAL [0,0,1,0](curr),[0,0,1,0](prev) - current and previous states

RTC - ???? (TIME?)
Buzzer - ??OB (Output Buzzer) -
RGB - ?? OL (Output Light)
RFID - ????
'''
    
    
    
    
