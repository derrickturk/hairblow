import os
import sys
import zmq.auth

from pathlib import Path

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f'Usage: {argv[0]} keypair-name', file=sys.stderr)
        return 1

    this_dir = Path(__file__).parent
    cert_dir = this_dir / 'certs'
    pubkey_dir = this_dir / 'public_keys'
    prvkey_dir = this_dir / 'private_keys'

    zmq.auth.create_certificates(this_dir / 'certs', argv[1])
    for key in cert_dir.iterdir():
        if key.suffix == '.key_secret':
            key.rename(prvkey_dir / key.name)
        elif key.suffix == '.key':
            key.rename(pubkey_dir / key.name)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
