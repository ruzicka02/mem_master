#!/usr/bin/env python

import struct
import click
import subprocess
import os
import sys

from math import nan

BASE_R_ADDR = int("0xa000_0000", base=16)
BASE_W_ADDR = int("0xa100_0000", base=16)

def float2hex(num: float) -> str:
    """ Unpack a Python float into bytes and return them in hex notation."""
    return "".join(f"{c:0>2x}" for c in struct.pack("!f", num))

def hex2float(hex_string: str) -> float:
    """
    Take 4 bytes in hex notation representing a float, pack them into the float and return it.

    Possible exceptions:
    - ValueError, if the string on input contains non-hex characters or the length is not valid
    """
    # remove spaces/underscores and strip ws (possible newline)
    hex_string = hex_string.replace("_", "").replace(" ", "").strip()

    # strip 0x at the beginning (lstrip would remove zeros at the beginning)
    if len(hex_string) >= 2 and hex_string[0] == "0" and hex_string[1] in ["x", "X"]:
        hex_string = hex_string[2:]

    if len(hex_string) != 8:
        raise ValueError(f"Exactly 8 hex-digits (4 bytes) expected, got {len(hex_string)}")

    if (invalid_chars := set(hex_string) - set("1234567890abcdefABCDEF")) != set():
        raise ValueError(f"Unexpected (non-hex) character on input {invalid_chars}")

    return struct.unpack('!f', bytes.fromhex(hex_string))[0]


@click.group()
def cli():
    pass

@cli.command()
@click.argument('num', type=float)
def encode(num):
    """Perform the conversion from a floating point to hex (32-bit)."""
    click.echo(float2hex(num))

@cli.command()
@click.argument('hex_string')
def decode(hex_string):
    """Perform the conversion from hex (32-bit) to a floating point."""
    click.echo(hex2float(hex_string))

def _read_raw(index: int, write_segment: bool) -> str:
    if os.geteuid() != 0:
        click.echo("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        sys.exit(1)

    base_addr: int = BASE_R_ADDR if not write_segment else BASE_W_ADDR
    addr: str = hex(base_addr + 4 * index)
    #  click.echo(f"[DEBUG] Running `sudo devmem2m {addr}`")

    try:
        proc = subprocess.run(["sudo", "devmem2m", addr], capture_output=True, timeout=5)
        # proc = subprocess.run(["echo", addr], capture_output=True, timeout=5)
    except subprocess.TimeoutExpired as exc:
        click.echo(exc)
        if exc.stderr is not None and exc.stderr != b'':
            click.echo(f"Provided stderr:\n{exc.stderr.decode('utf-8')}")
        sys.exit(2)

    if proc.returncode != 0:
        click.echo(f"Problem occured; return code {proc.returncode}")
        if proc.stderr is not None and proc.stderr != b'':
            click.echo(f"Provided stderr:\n{proc.stderr.decode('utf-8')}")
        sys.exit(3)

    return proc.stdout.decode("utf-8").strip().upper()


def _read(index: int, write_segment: bool) -> float:
    mem_content = _read_raw(index, write_segment)

    if mem_content == "DEADFEED":
        # click.echo("Indexing out of range! DEAD FEED")
        return nan  # not exit because of read_range

    # let the ValueErrors pass to user
    return hex2float(mem_content)

@cli.command()
@click.argument('index', type=int)
@click.option('-w', '--write-segment', is_flag=True, default=False, help="Read from the segment for writing")
def read(index, write_segment):
    """Read one value (4B) from given index in memory, convert it to float and print it."""
    click.echo(_read(index, write_segment))

@cli.command()
@click.argument('index', type=int)
@click.option('-w', '--write-segment', is_flag=True, default=False, help="Read from the segment for writing")
def read_raw(index, write_segment):
    """Read one value (4B) from given index in memory and print it."""
    click.echo(_read_raw(index, write_segment))

@cli.command()
@click.argument('start', type=int)
@click.argument('end', type=int)
@click.option('-w', '--write-segment', is_flag=True, default=False, help="Read from the segment for writing")
def read_range(start, end, write_segment):
    """Read a range of values (4B) from given indexes in memory, convert them to float and print them."""
    for i in range(start, end):
        click.echo(f"[{i:<2d}] {_read(i, write_segment)}")

@cli.command()
@click.argument('start', type=int)
@click.argument('end', type=int)
@click.option('-w', '--write-segment', is_flag=True, default=False, help="Read from the segment for writing")
def read_raw_range(start, end, write_segment):
    """Read a range of values (4B) from given indexes in memory and print them."""
    for i in range(start, end):
        click.echo(f"[{i:<2d}] {_read_raw(i, write_segment)}")


def _write_raw(index: int, hex_value: str) -> str:
    if os.geteuid() != 0:
        click.echo("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        sys.exit(1)

    addr: str = hex(BASE_W_ADDR + 4 * index)
    #  click.echo(f"[DEBUG] Running `sudo devmem2m {addr} {hex_value}`")

    try:
        proc = subprocess.run(["sudo", "devmem2m", addr, hex_value], capture_output=True, timeout=5)
        # proc = subprocess.run(["echo", addr], capture_output=True, timeout=5)
    except subprocess.TimeoutExpired as exc:
        click.echo(exc)
        if exc.stderr is not None and exc.stderr != b'':
            click.echo(f"Provided stderr:\n{exc.stderr.decode('utf-8')}")
        sys.exit(2)

    if proc.returncode != 0:
        click.echo(f"Problem occured; return code {proc.returncode}")
        if proc.stderr is not None and proc.stderr != b'':
            click.echo(f"Provided stderr:\n{proc.stderr.decode('utf-8')}")
        sys.exit(3)

    return proc.stdout.decode("utf-8").strip().upper()


def _write(index: int, num: float) -> float:
    hex_value: str = "0x" + float2hex(num)
    mem_content = _write_raw(index, hex_value)

    # what was actually written to memory (double -> float -> double)
    feedback = hex2float(mem_content)
    return feedback


@cli.command()
@click.argument('index', type=int)
@click.argument('num', type=float)
def write(index, num):
    """Write the given float to the memory on given index."""
    feedback = _write(index, num)

    if abs(feedback - num) < 1e-5:
        click.echo("Success!")
    else:
        click.echo(f"{feedback} written")

@cli.command()
@click.argument('index', type=int)
@click.argument('hex_string')
def write_raw(index, hex_string):
    """Write the given value (4B) to the memory on given index."""
    mem_feedback = _write_raw(index, hex_string)
    click.echo(f"0X{mem_feedback} written")

if __name__ == "__main__":
    cli()