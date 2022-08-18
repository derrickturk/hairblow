import multiprocessing as mp
import re
import sys
import zmq

from multiprocessing.synchronize import Event
from pathlib import Path
from subprocess import Popen
from typing import Any, NoReturn

STAMP_RE = re.compile(rb'[a-zA-Z_][a-zA-Z0-9._-]+')

def spawner(do_make: Event) -> None:
    makes: list[Popen[bytes]] = []
    while True:
        # if no running makes, wait for signal, else wait up to 10s
        launch = do_make.wait(None if len(makes) == 0 else 10.0)

        if launch:
            do_make.clear()
            # TODO: collect output to a pipe or temp file,
            #   so that the e-mail nastygram can be specific
            makes.append(Popen(['make', '-j', '4'],
              stdout=sys.stdout, stderr=sys.stderr))

        done: list[Popen[bytes]] = []
        for m in makes:
            ret = m.poll()
            if ret is not None:
                done.append(m)
                if ret != 0:
                    print(f'BAD! ({ret}) [send an email]', file=sys.stderr)
        for d in done:
            makes.remove(d)

def server(ctx: zmq.Context[zmq.Socket[Any]], sck: zmq.Socket[Any],
  do_make: Event) -> NoReturn:
    sck.bind('tcp://*:7777')
    while True:
        msg = sck.recv()
        if STAMP_RE.fullmatch(msg) is not None:
            ('stamps' / Path(msg.decode('ascii'))).touch()
            do_make.set()
            sck.send_string('OK')
        else:
            sck.send_string('NAUGHTY: invalid stamp name')

def main(argv: list[str]) -> int:
    do_make = mp.Event()
    p = mp.Process(target=spawner, args=(do_make,))
    p.start()
    with zmq.Context() as ctx:
        with ctx.socket(zmq.REP) as sck:
            server(ctx, sck, do_make)
    p.join()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
