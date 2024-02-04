#!/usr/bin/env python

import struct
import click
import subprocess

BASE_ADDR = int("0xa000_0000", base=16)

def float2hex(num: float) -> str:
    """ Unpack a Python float into bytes and return them in hex notation."""
    return "".join(f"{c:0>2x}" for c in struct.pack("!f", num))

def hex2float(hex_string: str) -> float:
    """ Take 4 bytes in hex notation representing a float, pack them into the float and return it. """
    hex_string = hex_string.lstrip("0x").replace("_", "")
    return struct.unpack('!f', bytes.fromhex(hex_string))[0]


@click.group()
def cli():
    pass

@cli.command()
@click.argument('num', type=float)
def encode(num):
    click.echo(float2hex(num))

@cli.command()
@click.argument('hex_string')
def decode(hex_string):
    click.echo(hex2float(hex_string))


if __name__ == "__main__":
    cli()