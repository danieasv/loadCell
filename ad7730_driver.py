#!/usr/bin/python

import spidev
import time
from gpiozero import Button, LED

#Rasberry Pi GPIO
RESET = 26
RDY = 24
SS = 16
DEBUG = 0


READ_ONLY = 0xFF
CR_SINGLE_WRITE = 0x00
CR_SINGLE_READ = = 0x10
CR_CONTINUOUS_READ_START = 0x20
CR_CONTINUOUS_READ_STOP = 0x30

CR_COMMUNICATION_REGISTER = 0x00 #Write only
CR_STATUS_REGISTER = 0x00 #Read only
CR_DATA_REGISTER = 0x01
CR_MODE_REGISTER =0x02
CR_FILTER_REGISTER = 0x03
CR_DAC_REGISTER = 0x04
CR_OFFSET_REGISTER = 0x05
CR_GAIN_REGISTER = 0x06
CR_TEST_REGISTER = 0x07


MR1_MODE_IDLE = 0x00
MR1_MODE_CONTINUOUS = 0x20 #Standard Operation
MR1_MODE_SINGLE = 0x40
MR1_MODE_STANDBY = 0x60
MR1_MODE_INTERNAL_ZERO_CALIBRATION = 0x80
MR1_MODE_INTERNAL_FULL_CALIBRATION = 0xA0
MR1_MODE_SYSTEM_ZERO_CALIBRATION = 0xC0
MR1_MODE_SYSTEM_FULL_CALIBRATION = 0xE0
MR1_BU_BIPOLAR = 0x00 #+- voltage defined by MR0_RANGE
MR1_BU_UNIPOLAR = 0x10 #0 to voltage deifined by MRO_RANGE
MR1_WL_24_BIT = 0x01
MR1_WL_16_BIT = 0x00

MR0_HIREF_5V = 0x80
MR0_HIREF_2P5V = 0x00
MR0_RANGE_10MV = 0x00
MR0_RANGE_20MV = 0x01
MR0_RANGE_40MV = 0x02
MR0_RANGE_80MV = 0x03
MR0_CHANNEL_1 = 0x00
MR0_CHANNEL_2 = 0x01
MR0_CHANNEL_SHORT_1 = 0x02 #Used for internal noise check
MR0_CHANNEL_NEGATIVE_1_2 = 0x03 #Unknown use
MRO_BURNOUT_ON = 0x04 #Advanced, to check if loadcell is burnt out

FR2_SINC_AVERAGING_2048 = 0x80  #Base sample rate of 50 Hz
FR2_SINC_AVERAGING_1024 = 0x40  #Base sample rate of 100 Hz
FR2_SINC_AVERAGING_512 = 0x20   #Base sample rate of 200 Hz
FR2_SINC_AVERAGING_256 = 0x10   #Base sample rate of 400 Hz

FR1_SKIP_ON = 0x02 #the FIR filter on the part is bypassed
FR1_SKIP_OFF = 0x00
FR1_FAST_ON = 0x01 #FIR is replaced with moving average on large step, sinc filter averages are used to compensate
FR1_FAST_OFF = 0x00

FR0_CHOP_ON = 0x10 #When the chop mode is enabled, the part is effectively chopped at its input and output to remove all offset and offset drift errors on the part.
FR0_CHOP_OFF = 0x00 #Increases sample rate by x3

#DAC Register Values
DACR_OFFSET_SIGN_POSITIVE = 0x00
DACR_OFFSET_SIGN_NEGATIVE = 0x20
DACR_OFFSET_40MV = 0x10
DACR_OFFSET_20MV = 0x08
DACR_OFFSET_10MV = 0x04
DACR_OFFSET_5MV = 0x02
DACR_OFFSET_2P5MV = 0x01
DACR_OFFSET_NONE = 0x00

#current settings
CURRENT_MODE_1_SETTINGS = (MR1_BU_UNIPOLAR | MR1_WL_24_BIT)
CURRENT_MODE_0_SETTINGS = (MR0_HIREF_5V | MR0_RANGE_10MV | MR0_CHANNEL_1)
SETUP_REGISTER = (CR_STATUS_REGISTER | CR_SINGLE_READ )


spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

reset = LED(RESET)
ready = Button(RDY)
chipSelect = LED(SS)

def waitForReady():
	ready.wait_for_release()
	if(DEBUG):
		print(".")
		time.sleep(0.1)
	


def restBoard():
	reset.off()
	time.sleep(0.2)
	reset.on()
	time.sleep(0.2)


def sendByte(input):
	if(DEBUG):
		print("  ->  Transmitting 0x%s \n" %(input.encode('hex')))
	chipSelect.off()
	spi.xfer([input])
	chipSelect.on()
	
def send2Bytes(first,second):
	if(DEBUG):
		print("  ->  Transmitting 0x%s 0x%s \n" %(first.encode('hex')), %(second.encode('hex')))
	chipSelect.off()
	spi.xfer([first,second])
	chipSelect.on()
	
def send3Bytes(first,second,third):
	if(DEBUG):
		print("  ->  Transmitting 0x%s 0x%s 0x%s \n" %(first.encode('hex')), %(second.encode('hex')), %(third.encode('hex')))
	chipSelect.off()
	spi.xfer([first,second,third])
	chipSelect.on()

def readBytes(number):
	chipSelect.off()
	for i in range(number):
		print("0x")
		value = spi.xfer([READ_ONLY])
		print(hex(value), "\n")
	chipSelect.on()


def main():
    print("Starting...")
	if(DEBUG):
		print("Reseting AD7730 \n");
	restBoard()
	
	if(DEBUG):
		print("SETUP Register set to: \n")
		sendByte(SETUP_REGISTER)
		readBytes(1)
	
	if(DEBUG):
		print("Start Continous Mode: \n")
		
	sendByte(CR_SINGLE_WRITE | CR_MODE_REGISTER);
	send2Bytes(MR1_MODE_CONTINUOUS | CURRENT_MODE_1_SETTINGS, CURRENT_MODE_0_SETTINGS);
	waitForReady();	
	
	if(DEBUG):
		print("Continous Mode started \n")
	
	if(DEBUG):
		print("Start continuos read \n")
	
	 sendByte(CR_CONTINUOUS_READ_START | CR_DATA_REGISTER);
	
	if(DEBUG):
		print("Reading started \n")


	while True:
		waitForReady()
		
		chipSelect.off()
		result1 = spi.xfer([0])
		result2 = spi.xfer([0])
		result3 = spi.xfer([0])
		chipSelect.on()
		
		result = result3 + result2*256 + result1*256*256
		print("%d \n", result)
	
if __name__ == '__main__':
    main()
