"""Rebuild every shipped profile asset from its editable sources."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    with tempfile.TemporaryDirectory(prefix='cresmar-profile-') as frames:
        run(sys.executable, 'scripts/generate_links.py')
        run(sys.executable, 'scripts/generate_sections.py')
        run(sys.executable, 'scripts/generate_header.py', '--frames-dir', frames)
        run('node', 'scripts/render_profile.cjs', frames)
        run(sys.executable, 'scripts/encode_gifs.py', frames)


if __name__ == '__main__':
    main()
