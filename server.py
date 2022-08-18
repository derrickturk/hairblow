import asyncio
import re
import sys
import zmq
import zmq.asyncio
import zmq.auth
import zmq.auth.asyncio

from pathlib import Path
from subprocess import PIPE
from typing import cast, NoReturn

STAMP_RE = re.compile(rb'[a-zA-Z_][a-zA-Z0-9._-]+')

async def server(ctx: zmq.asyncio.Context) -> NoReturn:
    this_dir = Path(__file__).parent
    pubkey_dir = this_dir / 'public_keys'
    prvkey_dir = this_dir / 'private_keys'

    auth = zmq.auth.asyncio.AsyncioAuthenticator(ctx)
    auth.start()
    auth.allow('127.0.0.1')
    auth.configure_curve(domain='*', location=pubkey_dir)

    sck = ctx.socket(zmq.REP)
    sck.curve_publickey, sck.curve_secretkey = zmq.auth.load_certificate(
      prvkey_dir / 'server.key_secret')
    sck.curve_server = True
    sck.bind('tcp://*:7777')

    makes = set()
    while True:
        msg = cast(bytes, await sck.recv())
        if STAMP_RE.fullmatch(msg) is not None:
            ('stamps' / Path(msg.decode('ascii'))).touch()
            make_task = asyncio.create_task(do_make())
            makes.add(make_task)
            make_task.add_done_callback(makes.discard)
            sck.send_string('OK')
        else:
            sck.send_string('NAUGHTY: invalid stamp name')

async def do_make() -> None:
    make = await asyncio.create_subprocess_exec('make', '-j', '4',
      stdout=PIPE, stderr=PIPE)
    stdout, stderr = await make.communicate()
    if make.returncode != 0:
        # TODO: email
        print(f'BAD! ({make.returncode}) [send an email]', file=sys.stderr)
        sys.stderr.write(stderr.decode('utf-8'))
    else:
        sys.stdout.write(stdout.decode('utf-8'))

async def main(argv: list[str]) -> int:
    ctx = zmq.asyncio.Context()
    await server(ctx)
    return 0

if __name__ == '__main__':
    sys.exit(asyncio.run(main(sys.argv)))
