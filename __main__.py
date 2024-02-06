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
    click.echo(float2hex(num))

@cli.command()
@click.argument('hex_string')
def decode(hex_string):
    click.echo(hex2float(hex_string))

def _read(index: int):
    if os.geteuid() != 0:
        click.echo("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        sys.exit(1)

    addr: str = hex(BASE_ADDR + 4 * index)
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

    mem_content = proc.stdout.decode("utf-8").strip().upper()
    if mem_content == "DEADFEED":
        click.echo("Indexing out of range! DEAD FEED")
        return  # not exit because of read_range

    # let the ValueErrors pass to user
    click.echo(hex2float(mem_content))

@cli.command()
@click.argument('index', type=int)
def read(index):
    _read(index)

@cli.command()
@click.argument('start', type=int)
@click.argument('end', type=int)
def read_range(start, end):
    for i in range(start, end):
        click.echo(f"[{i:<2d}] ", nl=False)  # index info
        _read(i)  # this automatically dumps the memory value


if __name__ == "__main__":
    cli()