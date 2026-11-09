"""Render the claim taxonomy, release path, assurance graph and survey coverage."""
import argparse
from pathlib import Path

def ladder(output):
    from android_panels import taxonomy as panel
    return panel(output)


def lifecycle(output):
    from android_panels import lifecycle as panel
    return panel(output)


def assurance(output):
    from android_panels import assurance as panel
    return panel(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path(__file__).resolve().parent)
    output = parser.parse_args().outdir
    output.mkdir(parents=True, exist_ok=True)
    for name, draw in [('claim-ladder', ladder), ('mobile-lifecycle', lifecycle),
                       ('assurance-pattern', assurance)]:
        draw(output / (name+'.pdf'))
    from draw_review_coverage import render as coverage
    coverage(output/'review-coverage.pdf')
    from draw_lineage_histories import draw
    draw(output/'lineage-histories.pdf')
    print('Generated conceptual and review-coverage vector figures.')


if __name__ == '__main__':
    main()
