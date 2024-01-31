#!/usr/bin/env python

import struct

def float2hex(num: float) -> str:
    """ Unpack a Python float into bytes and return them in hex notation."""
    return "".join(f"{c:0>2x}" for c in struct.pack("!f", num))

def hex2float(hex_string: str) -> float:
    """ Take 4 bytes in hex notation representing a float, pack them into the float and return it. """
    return struct.unpack('!f', bytes.fromhex(hex_string))[0]

