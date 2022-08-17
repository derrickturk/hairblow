import re
import subprocess
import sys
import zmq

from pathlib import Path
from typing import Any, NoReturn

STAMP_RE = re.compile(rb'[a-zA-Z_][a-zA-Z0-9._-]+')

def server(ctx: zmq.Context[zmq.Socket[Any]], sck: zmq.Socket[Any]) -> NoReturn:
    sck.bind('tcp://*:7777')
    while True:
        msg = sck.recv()
        if STAMP_RE.fullmatch(msg) is not None:
            ('stamps' / Path(msg.decode('ascii'))).touch()
            r = subprocess.run(['make', '-j', '4'], capture_output=True)
            if r.returncode == 0:
                sys.stdout.write(r.stdout.decode('utf-8'))
                sck.send_string('OK')
            else:
                sys.stderr.write(r.stderr.decode('utf-8'))
                sck.send_string(f'ERROR: make failed (status {r.returncode})')
        else:
            sck.send_string('NAUGHTY: invalid stamp name')

def main(argv: list[str]) -> int:
    with zmq.Context() as ctx:
        with ctx.socket(zmq.REP) as sck:
            server(ctx, sck)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
