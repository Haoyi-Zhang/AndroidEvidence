"""Render the manuscript example as a vector PDF."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "artifact/figures"))

def android(output):
    from android_panels import worked as panel
    return panel(output)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path(__file__).with_name('worked-claim.pdf'))
    a=p.parse_args()
    android(a.output)
