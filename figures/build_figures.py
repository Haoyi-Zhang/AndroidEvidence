"""Draw the three claim/evidence diagrams directly as embedded-font vectors.

These are conceptual relations from the manuscript, not measured outcomes.
No TeX executable or external drawing service is used.
"""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams.update({
    'font.family': 'STIXGeneral', 'font.size': 9.5, 'text.usetex': False,
    'mathtext.fontset': 'stix', 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'savefig.transparent': False,
})


def canvas(width, height):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(0, width), ylim=(0, height))
    ax.set_axis_off()
    return fig, ax


def box(ax, x, y, width, height, text, *, evidence=False, shade=.96):
    ax.add_patch(FancyBboxPatch(
        (x-width/2, y-height/2), width, height,
        boxstyle='round,pad=0.015,rounding_size=0.02',
        linewidth=.65, edgecolor='.22', facecolor=str(shade),
        linestyle=(0, (3, 2)) if evidence else '-', zorder=2))
    ax.text(x, y, text, ha='center', va='center', linespacing=1.12,
            zorder=3)


def arrow(ax, start, end, *, dashed=False):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle='-|>', mutation_scale=8,
        linewidth=.7, color='.24', linestyle=(0, (3, 2)) if dashed else '-',
        shrinkA=0, shrinkB=0, zorder=1))


def routed_arrow(ax, points, *, dashed=False):
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color='.24',
                linewidth=.7, linestyle=(0, (3, 2)) if dashed else '-', zorder=1)
    arrow(ax, points[-2], points[-1], dashed=dashed)


def save(fig, output):
    fig.savefig(output, format='pdf', metadata={'Creator': 'Matplotlib',
                                               'CreationDate': None,
                                               'ModDate': None})
    plt.close(fig)


def ladder(output):
    fig, ax = canvas(6.35, 3.88)
    labels = [
        'L0  Identity: observed bytes or a cryptographic digest are equal.',
        'L1  Composition: contains a component, resource,\nor recognizable code region.',
        'L2  Resemblance: shared features or behavior\nunder a stated transformation model.',
        'L3  Derivation: transformed from another object or a shared\nhistorical ancestor; direction is explicit.',
        'L4  Process provenance: recorded principals and steps\nbind input materials to an output artifact.',
        'L5  Authorization: a policy-recognized principal\napproved the transformation or release.',
        'L6  Behavioral assurance: a security, privacy, or functional\nproperty holds in a stated model.',
    ]
    centers = [.31 + .54*i for i in range(7)]
    for i, (y, label) in enumerate(zip(centers, labels)):
        box(ax, 3.50, y, 5.52, .43, label, shade=.97-.025*i)
        if i:
            arrow(ax, (3.50, centers[i-1]+.23), (3.50, y-.23))
    ax.text(.26, 1.94, 'Different propositions and assumptions',
            rotation=90, ha='center', va='center')
    save(fig, output)


def lifecycle(output):
    fig, ax = canvas(6.35, 4.55)
    xs = [1.05, 3.02, 4.99]
    top, first_evidence, bottom, last_evidence = 4.12, 3.04, 1.85, .75
    stages = ['Source and\nspecification', 'Dependency\nresolution',
              'Generation, build,\nshrink, package']
    evidence = ['Repository history\nand review',
                'Resolver log, SBOM,\ncomponent evidence',
                'Attestations and\nreproducibility']
    bottom_stages = ['Installed\nbehavior', 'Store and\nupdate', 'Sign and\napprove']
    bottom_evidence = ['Static, dynamic,\npolicy evidence',
                       'Transparency and\nfreshness',
                       'Delegation and\nrelease signature']
    for x, stage, ev, lower, lev in zip(xs, stages, evidence, bottom_stages, bottom_evidence):
        box(ax, x, top, 1.64, .56, stage)
        box(ax, x, first_evidence, 1.64, .67, ev, evidence=True, shade=1)
        box(ax, x, bottom, 1.64, .56, lower)
        box(ax, x, last_evidence, 1.64, .67, lev, evidence=True, shade=1)
        arrow(ax, (x, first_evidence+.35), (x, top-.30), dashed=True)
        arrow(ax, (x, last_evidence+.35), (x, bottom-.30), dashed=True)
    for left, right in zip(xs, xs[1:]):
        arrow(ax, (left+.84, top), (right-.84, top))
        arrow(ax, (right-.84, bottom), (left+.84, bottom))
    routed_arrow(ax, [(5.83, top), (6.15, top), (6.15, bottom), (5.83, bottom)])
    save(fig, output)


def assurance(output):
    fig, ax = canvas(6.35, 4.95)
    left, right = 1.67, 4.70
    top, claims, supporting, evidence, bottom = 4.56, 3.58, 2.64, 1.62, .60
    box(ax, 3.18, top, 5.45, .57,
        'Released APK is an authorized product of process P\nand satisfies property Q', shade=.92)
    box(ax, left, claims, 2.55, .66,
        'APK digest is the product of\ndeclared source, dependencies\nand build steps')
    box(ax, right, claims, 2.55, .66,
        'The exact APK digest satisfies\nproperty Q in the stated\nanalysis model')
    box(ax, left, supporting, 2.55, .57,
        'Principals and release step\nare authorized by policy')
    box(ax, right, supporting, 2.55, .57,
        'Artifact/component relations\nmatch the declared lineage')
    box(ax, left, evidence, 2.55, .67,
        'Attestations, source/resolver\nrecords, reproducible build', evidence=True, shade=.91)
    box(ax, right, evidence, 2.55, .67,
        'Code, graph, resource, UI,\nversion and behavior evidence', evidence=True, shade=.91)
    box(ax, left, bottom, 2.55, .67,
        'Delegation, signatures,\ntransparency and freshness', evidence=True, shade=.91)
    box(ax, right, bottom, 2.55, .67,
        'Static, dynamic, formal\nand policy analyses', evidence=True, shade=.91)
    arrow(ax, (left, claims+.35), (2.33, top-.30))
    arrow(ax, (right, claims+.35), (4.02, top-.30))
    arrow(ax, (left, supporting+.30), (left, claims-.35))
    arrow(ax, (right-.4, supporting+.30), (left+.55, claims-.35))
    routed_arrow(ax, [(left-1.29, evidence), (.24, evidence), (.24, claims),
                      (left-1.29, claims)], dashed=True)
    routed_arrow(ax, [(left-1.29, bottom), (.10, bottom), (.10, supporting),
                      (left-1.29, supporting)], dashed=True)
    arrow(ax, (right, evidence+.35), (right, supporting-.30), dashed=True)
    routed_arrow(ax, [(right+1.29, bottom), (6.23, bottom), (6.23, claims),
                      (right+1.29, claims)], dashed=True)
    save(fig, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path(__file__).resolve().parent)
    output = parser.parse_args().outdir
    output.mkdir(parents=True, exist_ok=True)
    for name, draw in [('claim-ladder', ladder), ('mobile-lifecycle', lifecycle),
                       ('assurance-pattern', assurance)]:
        draw(output / (name+'.pdf'))
    print('Generated three conceptual vector figures.')


if __name__ == '__main__':
    main()
