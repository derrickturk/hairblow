import re
import sys
import zmq
import zmq.auth

from pathlib import Path
from typing import Any

STAMP_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9._-]+')

def client(ctx: zmq.Context[zmq.Socket[Any]], stamp: str, pk_file: Path) -> str:
    this_dir = Path(__file__).parent
    pubkey_dir = this_dir / 'public_keys'

    with ctx.socket(zmq.REQ) as sck:
        sck.curve_publickey, sck.curve_secretkey = zmq.auth.load_certificate(
          pk_file)
        sck.curve_serverkey, _ = zmq.auth.load_certificate(
          pubkey_dir / 'server.key')
        with sck.connect('tcp://localhost:7777'):
            sck.send_string(stamp)
            if sck.poll(2000) != 0:
                return sck.recv().decode('utf-8')
            else:
                raise RuntimeError(
                  'Unable to communicate with server (check credentials?)')

def main(argv: list[str]) -> int:
    if len(argv) != 3 or not STAMP_RE.fullmatch(argv[1]):
        print(f'Usage: {argv[0]} stamp-name pk-file', file=sys.stderr)
        return 1

    with zmq.Context() as ctx:
        ret = client(ctx, argv[1], Path(argv[2]))
        if ret != 'OK':
            print(f'Error: {ret}', file=sys.stderr)
            return 1

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
