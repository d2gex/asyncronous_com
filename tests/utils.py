from os.path import join
from pathlib import Path

path = Path(__file__).resolve()
ROOT = path.parents[1]
TEST = join(ROOT, 'tests')
