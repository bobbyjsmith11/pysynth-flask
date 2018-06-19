#!usr/bin/env python
"""
----------
control.py
----------
    :Description:
        Uses the cp2130 to control 5Gx
    :Pinout:
        :SPI (uses spidev0):
        :GPIO for PLL:
            LOCK_DETECT - pin 15
        :GPIO for RX filter:
            A - pin 7
            B - pin 11
            C - pin 13
            D - pin 16
            E - pin 18
        :GPIO for LO filter:
            A - pin 27
            B - pin 29
            C - pin 31
            D - pin 33
            E - pin 32
"""
import cp2130
from cp2130.data import *
import struct
import time

LOCK_DETECT = 15    # GPIO pin for lock detect
PLL_RESET = 13      # CE on ADF5356

# GPIO pins for RX filter
RX_PINS = [7,
           11,
           13,
           16,
           18]

# GPIO pins for LO filter
LO_PINS = [29,
           31,
           33,
           37,
           32]

def configure_all():
    setup_lock_detect()
    # configure_rx_filter_bits()
    setup_pll_reset()

class Cp2130SpiDevice(object):
    """
    """
    def __init__(self):
        self.chip = cp2130.find()
        time.sleep(0.1)
        self.chip.channel0.clock_frequency = 500000
        self.chip.channel1.clock_frequency = 500000

    def set_attenuator(self, val):
        """ set the HMC1018 attenuator
        :Args: 
            :val (int): from 0 to 31
        """
        val = ~val & 0x1F       # one's complement
        b = struct.pack('>B', val)
        ret = self.chip.channel1.write(b)
        return ret

    def write_int(self, val):
        b = struct.pack('>I', val)
        ret = self.chip.channel0.write(b)
        # time.sleep(0.1)
        return ret

    def read_int(self, addr):
        pass
    
    def reset_pll(self):
        self.disable_pll()
        time.sleep(0.1)
        self.enable_pll()

    def disable_pll(self):
        self.set_gpio(2, False)
        self.set_lock_detect_led(self.read_lock_detect())

    def enable_pll(self):
        self.set_gpio(2, True)
        self.set_lock_detect_led(self.read_lock_detect())

    def read_lock_detect(self):
        return(self.get_gpio(3))

    def set_lock_detect_led(self, state):
        """ set the lock detect LED (D6)on the CP2130-EK to 
        indicate the lock status
        :args:
            :state (bool): True = ON, False = OFF
        """
        self.set_gpio(5, not(state))

    def set_filter(self, band):
        """
        """
        self.set_gpio(6, band & (1 << 0))   # bit A
        self.set_gpio(7, band & (1 << 1))   # bit B
        self.set_gpio(8, band & (1 << 2))   # bit C
        self.set_gpio(9, band & (1 << 3))   # bit D
        self.set_gpio(10, band & (1 << 4))  # bit E


    def set_gpio(self, ch, val):
        """ 
        set the state of the gpio
        :Args:
            :ch (int): channel 0-10
            :val (bool):      
        """
        if val:
            state = LogicLevel.HIGH
        else:
            state = LogicLevel.LOW
        self.chip.__getattribute__("gpio" + str(ch)).value = state

    def get_gpio(self, ch):
        """
        return the state of the gpio
        :Args:
            :ch (int): channel 0-10
        :Returns: bool
        """
        val = self.chip.__getattribute__("gpio" + str(ch)).value
        if val.value:
            return True
        else:
            return False

    def _program_otp_pin_settings(self):
        """ 
        writes the ONE TIME PROGRAMMBLE memory on the CP2130 to configure
        the pins to the approprate settings
        """
        lock = self.chip.lock
        pins = self.get_otp_pin_settings()
        self.chip.pin_config = pins 
        print(lock)

    def get_otp_pin_settings(self):
        """ get the pin_config object with the following settings
        PIN         DEFAULT CONFIG                  DESIRED CONFIG
        gpio0       cs_n                            cs_n
        gpio1       cs_n                            cs_n
        gpio2       cs_n                            cs_n            use as a reset for the ADF5355 
        gpio3       RTR active low input            GPIO Input      use for lock detect on the ADF5355
        gpio4       event counter input             GPIO Input      unused
        gpio5       clock output                    cs_n            used to drive LED lock indicator on eval board
        gpio6       GPIO input                      cs_n            FLT ctrl
        gpio7       GPIO Output                     cs_n            FLT ctrl 
        gpio8       SPI activity output             cs_n            FLT ctrl 
        gpio9       SUSPEND output                  cs_n            FLT ctrl
        gpio10      SUSPEND_N output                cs_n            FLT ctrl

        default config =                    PinConfig(pin_config('\x03\x03\x03\x04\x04\x04\x00\x02\x04\x04\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
        config after OTP programming =      PinConfig(pin_config('\x03\x03\x03\x04\x04\x03\x03\x03\x03\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
        """
        pins = self.chip.pin_config
        # pins.gpio3 leave as is
        # pins.gpio4 leave as is
        pins.gpio5.function = GPIO5Mode.CS5_n 
        pins.gpio6.function = GPIO6Mode.CS6_n 
        pins.gpio7.function = GPIO7Mode.CS7_n 
        pins.gpio8.function = GPIO8Mode.CS8_n 
        pins.gpio9.function = GPIO9Mode.CS9_n 
        pins.gpio10.function = GPIO10Mode.CS10_n 
        return pins



if __name__ == '__main__':
    
    pass 







