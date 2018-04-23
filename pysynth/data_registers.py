#!/usr/bin/env python
'''
======================================
data_registers.py
======================================
Author:     Bobby Smith
Description:
    A handy tool for manipulating bit fields within a larger register and
    for managing sets of registers

Example Usage:

    To load from an xml file:
    >>> from data_registers import data_registers
    >>> reg_map = data_regsiter.RegisterMap(xml_file="tests/lmx2594.xml")

    To create manually and write to xml file:
    >>> from data_registers import data_registers
    >>> reg_map = data_regsiter.RegisterMap()   # empty RegisterMap
    >>> reg1 = data_register.DataRegister("TEST_REG1", 0x0F, num_bits=16, desc="sample register")
    >>> reg1.add_bit_field("BF1", 0, 7, value=0x0A, desc='bit field 1')
    >>> reg1.add_bit_field("BF2", 8, 15, value=0x11, desc='bit field 2')
    >>> reg2 = data_register.DataRegister("TEST_REG2", 0x01, num_bits=16, desc="another sample register")
    >>> reg2.add_bit_field("FENCER_LEAKAGE", 0, 4, value=0x10, desc='leakage in the fencer valve')
    >>> reg2.add_bit_field("EN_SELF_DESTRUCT", 5, 5, value=0x0, desc='set to blow up and kill everyone')
    >>> reg_map.add_address(reg1)
    >>> reg_map.add_address(reg2)
    >>> reg_map.write_map_to_xml("my_reg_map.xml")
'''
import os
import math
import collections
import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

class RegisterMap(dict):
    """ Dummy class for holding a list of Registers which are
        dynamically added as properties. The keys are address registers
        and the values are registers at the address.
    """
    def __init__(self, xml_file=None, reg_map_name="REG_MAP_NAME", num_bits=32):
        super(RegisterMap, self).__init__()
        if xml_file is None:
            self.name = reg_map_name
            self.num_bits = num_bits
        else:
            num_bits = self.load_map_from_xml(xml_file=xml_file)
        self.num_bits = num_bits

    # PROPERTIES
    @property
    def addresses(self):
        """ return  all of the address in the RegisterMap
        """
        return self.keys()

    # METHODS
    def load_map_from_xml(self, xml_file):
        root = xml.etree.ElementTree.parse(xml_file).getroot()
        regs = root.findall('register')
        try:
            self.name = root.attrib['name']
        except Exception as e:
            print(e)
        for reg in regs:
            # print(reg.attrib)
            addr = eval(reg.attrib['address'])
            if 'num_bits' not in reg.keys():
                bits = eval(root.attrib['num_bits'])
            else:
                bits = eval(reg.attrib['num_bits'])
            reg_desc = reg.text
            new_reg = DataRegister(reg.attrib['name'], addr, bits, desc=reg_desc)
            fields = reg.findall('field')
            for field in fields:
                # print(field.attrib)
                if ":" not in field.attrib['bits']:   # single bit field
                    lo_bit = int(field.attrib['bits'])
                    hi_bit = lo_bit
                else:
                    bit_str = field.attrib['bits'].split(":")
                    hi_bit = int(bit_str[0])
                    lo_bit = int(bit_str[1])
                desc_str = ' '.join(field.text.strip().split())
                # desc_str = field._escape_attr(text,'utf-8')
                new_reg.add_bit_field(field.attrib['name'], lo_bit, hi_bit, desc=desc_str)
            if 'default_value' in reg.keys():
                new_reg.load_reg_value(eval(reg.attrib['default_value']))
            # the keys of RegisterMap are the register addresses
            self.add_register(new_reg, addr)
        number_of_bits = int(root.attrib['num_bits'])
        return number_of_bits

    def write_map_to_xml(self, out_file=None, reg_map_name=None):
        """ write a current register map out to a file or simply print if file not provided
        """
        # top_line = str("register_map name=" + str(reg_map_name) + " num_bits=16")
        top = Element("register_map")
        if reg_map_name is None:
            top = Element("register_map", {'name':self.name, 'num_bits':'16'})
        else:
            top = Element("register_map", {'name':reg_map_name, 'num_bits':'16'})

        for addr in self.addresses:
            addr_str = ("{0:#04x}").format(addr)
            def_value = ("{0:#06x}").format(self[addr].value)
            name_str = self[addr].name
            reg_elem = SubElement(top, 'register', {'name':name_str, \
                                                 'address':addr_str,
                                                 'default_value':def_value
                                                })
            reg_elem.text = self[addr].description
            for b_f in self[addr].bitfields:
                if b_f.num_bits == 1:
                    bit_str = str(b_f.bit_offset)
                else:
                    lo_bit = b_f.bit_offset
                    hi_bit = lo_bit + b_f.num_bits - 1
                    bit_str = str(hi_bit) + ":" + str(lo_bit)
                bitfield_elem = SubElement(reg_elem, 'field', {'name':b_f.name,
                                                               'bits':bit_str})
                bitfield_elem.text = b_f.description
            # reg_elem.text = "\n    "
            # field = SubElement(child,'field', {'name': "FIELD_NAME",
            #                                    'bits':"HI_BIT:LO_BIT"})
        rough_string = tostring(top, 'utf-8')
        reparsed = minidom.parseString(rough_string)

        xml_str = reparsed.toprettyxml(indent="    ")
        if out_file != None:
            if isinstance(out_file, str):
                out_file = open(out_file, 'w')
            out_file.write(xml_str)
            out_file.close()
            pass

    def add_register(self, new_reg, addr=None):
        """ add a Register
        """
        if addr is None:
            addr = new_reg.address
        self[addr] = new_reg
        # add every bitfield as a property accessible from
        # the RegisterMap object
        for b_f in new_reg.bitfields:
            if hasattr(self, b_f.name):     # this field already exists, create unique
                print(b_f.name + " is not unique. Adding reg_address to the end (" + hex(b_f.register_address) + ")")
                bf_name = b_f.name + "_" + hex(b_f.register_address)
            else:
                bf_name = b_f.name
            self.__setattr__(bf_name, b_f)

    def delete_register(self, addr):
        """ delete a Register
        """
        del self[addr]

class DataRegister(object):
    """
    Basic construct for DataRegister package
    """
    def __init__(self, name, address, num_bits=32, desc=None):
        self.bitfields = []
        self.name = name
        self.address = address
        self.num_bits = num_bits
        self.value = 0
        self.description = desc

    def load_reg_value(self, val):
        """ update the register value and the values of all bit fields.
        """
        self.value = val
        for b in self.bitfields:
            b.value = self.read_bit_field(b)

    def update_bit_field(self, bitfield):
        """
        sets the value of a bit field
        """
        self.value = (self.value & (~bitfield.mask) | (bitfield.value << bitfield.bit_offset))

    def read_bit_field(self, bitfield):
        """
        returns the value of a bit field
        """
        return (self.value & bitfield.mask) >> bitfield.bit_offset

    def get_hex(self):
        """
        :Returns:
        (str) hex value with all of the
        leading 0's, except without the leading '0x'
        """
        num_nibbles = int(math.ceil(float(self.num_bits)/4))
        val = hex(self.value).split('x')
        val = val[1].zfill(num_nibbles)
        return val

    def get_binary(self):
        """
        :Returns:
        (str) binary value with all of the
        leading 0's, except without the leading '0b'
        """
        val = bin(self.value).split('b')
        val = val[1].zfill(self.num_bits)
        return val

    def add_bit_field(self, name, start_bit, stop_bit, value=0, desc=None):
        """ add a bit field to the register
        :Parameters:
        name (str) - name of the bit field
        start_bit (int) - the position of the lowest bit in the register
        stop_bit (int) - the position of the highest bit in the register
        """
        num_bits = (stop_bit - start_bit) + 1
        bf = BitField(start_bit, num_bits, def_value=value, desc=desc, parent=self)
        bf.set_name(name)
        self.bitfields.append(bf)
        self.__setattr__(name, bf)
        eval("self.update_bit_field( self."+str(name)+")")

    def set_bit_field_value(self, name, value):
        """ set the value of a bit field within the DataRegister
        :Parameters:
        name (str) - name of the BitField
        value (int) - desired value of the BitField
        """
        eval("self." + str(name) + ".set_value("+str(value)+")")
        eval("self.update_bit_field( self."+str(name)+")")

    def get_bit_field_value(self, name):
        """ return the value of a BitField within the DataRegister
        :Parameters:
        name (str) - name of the BitField
        """
        ret = eval("self."+str(name)+".get_value()")
        return ret

    def get_bit_state(self, offset):
        """ return the state of the bit at offset as bool
        """
        return get_bit(self.value, offset)

    def set_bit_state(self, offset, state):
        """
        set the state of the bit at offset as bool
            Parameters
                offset (int) - bit position
                state (bool) - desired state of bit
        """
        new_val = set_bit(self.value, offset)
        self.load_reg_value(new_val)

    def get_int(self):
        """ return the value of the register as int if possible, that is the register
        value can be expressed as an int. Raise exception otherwise.
        """
        if self.num_bits > 32:
            raise Exception("int not valid. register has "+str(self.num_bits)+" bits.")
        else:
            return int(self.value)

    def get_bytes(self):
        """ return the value of the register as a bytearray. NOT IMPLEMENTED
        """
        pass

class BitField(object):
    def __init__(self,
                 bit_offset,
                 num_bits,
                 def_value=0,
                 desc=None,
                 parent=None):
        """
        :Parameters:
        bit_offset (int) - the LSB location of the field within the register.
                    for instance, a BitField with 3 bits starting at bit 10 of the register
                    will take up bits 10, 11 and 12 (indeces begin at bit 0).
        num_bits (int) - number of bits in the field
        """
        self.parent = parent
        self.bit_offset = bit_offset
        self.num_bits = num_bits
        self.mask = (2**num_bits - 1) << self.bit_offset
        self.set_value(def_value)
        self.description = desc

    @property
    def value(self):
        """ the int value of the BitField
        """
        return self.get_value()
    @value.setter
    def value(self, val):
        self.set_value(val)

    @property
    def register_address(self):
        """ the address of the register where this BitField resides
        """
        if self.parent is None:
            return None
        else:
            return self.parent.address

    def get_value(self):
        """ return the current value of the BitField
        """
        return self._value

    def set_value(self, val):
        """ update the value of the BitField
        """
        if val > 2**(self.num_bits) -1:
            raise ValueError("bit field contains " + \
                              str(self.num_bits) +\
                              " bits. " + str(val) +" is too large.")
        else:
            self._value = val
            if self.parent != None:
                self.parent.update_bit_field(self)

    def set_name(self, name):
        """ set the name property """
        self.name = name

#############################
###### COMMON METHODS
#############################

def set_bit(int_type, offset):
    """ set the bit at offset in int_type
        Parameters
            int_type (int) - integer to be manipulated
            offset (int) - bit offset, 0 is LSB
        Returns and integer with the correct bit set

        Example Usage
            >>> set_bit(0x08,0)
            >>> 9
    """
    mask = 1 << offset
    return (int_type | mask)

def clear_bit(int_type, offset):
    """ clear the bit at offset in int_type
        Parameters
            int_type (int) - integer to be manipulated
            offset (int) - bit offset, 0 is LSB
        Returns and integer with the correct bit cleared

        Example Usage
            >>> clear_bit(0x09,0)
            >>> 8
    """
    mask = ~(1 << offset)
    return abs(int_type & mask)

def get_bit(int_type, offset):
    """ return state of bit in int_type at offset
        Parameters
            int_type (int) - integer to be manipulated
            offset (int) - bit offset, 0 is LSB
        Returns True if set, False otherwise

        Example Usage
            >>> test_bit(0x09,0)
            >>> True
            >>> test_bit(0x08,0)
            >>> False
    """
    mask = 1 << offset
    return bool(int_type & mask)

def diff_reg_maps(file_1, file_2, out_file=None):
    """ compare two RegisterMaps and return differences to std_out and file (if provided)
    """
    if out_file != None:
        if isinstance(out_file, str):
            out_file = open(out_file, 'w')
    f_head, file1_name = os.path.split(file_1)
    f_head, file2_name = os.path.split(file_2)
    reg_map_1 = RegisterMap(file_1)
    reg_map_2 = RegisterMap(file_2)

    reg_1_not_reg2 = set(reg_map_1.addresses).difference(set(reg_map_2.addresses))
    reg_2_not_reg1 = set(reg_map_2.addresses).difference(set(reg_map_1.addresses))

    common_regs = set(reg_map_1.addresses).intersection(set(reg_map_2.addresses))
    for reg_addr in common_regs:
        if reg_map_1[reg_addr].value != reg_map_2[reg_addr].value:
            print("{:=<{width}}".format("", width=100))
            addr_str = "{0:#08x}".format(reg_addr)
            dat = [addr_str, 'FIELD', file1_name, file2_name]
            print("{:<{width}}"
                  "{:<{width}}"
                  "{:<{width}}"
                  "{:<{width}}"
                  .format(*dat, width=25))
            if out_file != None:
                out_file.write("{:=<{width}}\n".format("", width=100))
                out_file.write("{:<{width}}"
                               "{:<{width}}"
                               "{:<{width}}"
                               "{:<{width}}"
                               "\n"
                           .format(*dat, width=25))
            diff_registers(reg_map_1[reg_addr], reg_map_2[reg_addr], out_file=out_file)

def diff_registers(reg_1, reg_2, out_file=None):
    """ print to std_out and file (optionally) the difference between two registers
        Parameters
            reg_1 (data_register.DataRegister)
            reg_2 (data_register.DataRegister)
            out_file (file-object or str)
    """
    if out_file != None:
        if isinstance(out_file, str):
            out_file = open(out_file, 'w')
    bf_1_names = []
    for b_f in reg_1.bitfields:
        bf_1_names.append(b_f.name)
    bf_2_names = []
    for b_f in reg_2.bitfields:
        bf_2_names.append(b_f.name)
    # set of all bitfield names from both registsers
    master_name_set = set(bf_1_names) | set(bf_2_names)

    reg_equal = True
    reg_values = {}
    for bf_name in master_name_set:
        try:
            val1_str = "{0:#08x}".format(reg_1.__dict__[bf_name].value)
        except KeyError:     # field exists in reg_2, but not reg_1
            val1_str = "NULL"
            reg_equal = False
        try:
            val2_str = "{0:#08x}".format(reg_2.__dict__[bf_name].value)
        except KeyError:     # field exists in reg_1, but not reg_2
            val2_str = "NULL"
            reg_equal = False
        if val1_str != val2_str:
            reg_equal = False
        reg_values[bf_name] = (val1_str, val2_str)

    if not reg_equal:
        # dat = ['ADDR', 'FIELD', 'REG_1', 'REG_2']
        # print("{:<{width}}"
        #       "{:<{width}}"
        #       "{:<{width}}"
        #       "{:<{width}}"
        #       .format(*dat, width=25))
        # if out_file != None:
        #     out_file.write("{:<{width}}"
        #                    "{:<{width}}"
        #                    "{:<{width}}"
        #                    "{:<{width}}"
        #                    "\n"
        #                    .format(*dat, width=25))
        for k in reg_values:
            # addr_str = "{0:#08x}".format(reg_1.address)
            if reg_values[k][0] != reg_values[k][1]:
                dat = ["", k, reg_values[k][0], reg_values[k][1]]
                print("{:<{width}}"
                      "{:<{width}}"
                      "{:<{width}}"
                      "{:<{width}}"
                      .format(*dat, width=25))
                if out_file != None:
                    out_file.write("{:<{width}}"
                                   "{:<{width}}"
                                   "{:<{width}}"
                                   "{:<{width}}"
                                   "\n"
                                   .format(*dat, width=25))
