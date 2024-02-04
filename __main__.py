#!/usr/bin/env python

import struct
import click
import subprocess
import os
import sys

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

@cli.command()
@click.argument('index', type=int)
def read(index):
    if os.geteuid() != 0:
        click.echo("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        sys.exit(1)

    addr: str = hex(BASE_ADDR + 4 * index)
    click.echo(f"[DEBUG] Running `sudo devmem2m {addr}`")

    try:
        proc = subprocess.run(["sudo", "devmem2m", addr], capture_output=True, timeout=5)
    except subprocess.TimeoutExpired as exc:
        click.echo(f"Timeout of the reading process. Aborting.")
        click.echo(f"Provided stderr:\n{exc.stderr.decode('utf-8')}")
        sys.exit(2)

    if proc.returncode != 0:
        click.echo(f"Problem occured; return code {proc.returncode}")
        click.echo(f"Provided stderr:\n{proc.stderr.decode('utf-8')}")
        sys.exit(3)

    mem_content = proc.stdout.decode("utf-8")
    click.echo(hex2float(mem_content))

@cli.command()
@click.argument('start', type=int)
@click.argument('end', type=int)
def read_range(start, end):
    for i in range(start, end):
        click.echo(f"[{i:<2d}] ", nl=False)  # index info
        read(i)  # this automatically dumps the memory value


if __name__ == "__main__":
    cli()