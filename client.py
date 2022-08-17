import re
import sys
import zmq

from typing import Any

STAMP_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9._-]+')

def client(ctx: zmq.Context[zmq.Socket[Any]], sck: zmq.Socket[Any], stamp: str
  ) -> str:
    sck.send_string(stamp)
    return sck.recv().decode('utf-8')

def main(argv: list[str]) -> int:
    if len(argv) != 2 or not STAMP_RE.fullmatch(argv[1]):
        print(f'Usage: {argv[0]} stamp-name', file=sys.stderr)
        return 1
    with zmq.Context() as ctx:
        with ctx.socket(zmq.REQ) as sck:
            sck.connect('tcp://localhost:7777')
            ret = client(ctx, sck, argv[1])
            if ret != 'OK':
                print(f'Error: {ret}', file=sys.stderr)
                return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
