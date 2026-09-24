"""Conservative finite coverage accounting; not a novelty or literature oracle."""
from __future__ import annotations
from itertools import combinations
from typing import Sequence

Cell = int | None


def validate(matrix: Sequence[Sequence[Cell]]) -> tuple[int, int]:
    if not matrix or not matrix[0]:
        raise ValueError('coverage matrix must have at least one row and column')
    m, n = len(matrix), len(matrix[0])
    if m > 450 or n > 32 or m*n > 5000:
        raise ValueError('coverage matrix exceeds the bounded audit envelope')
    for row in matrix:
        if len(row) != n:
            raise ValueError('ragged coverage matrix')
        for cell in row:
            if cell is not None and (type(cell) is not int or cell not in (0,1)):
                raise ValueError('cells must be integer 0, integer 1, or None')
    return m, n


def boolean_coverage(matrix: Sequence[Sequence[int]]) -> tuple[bool, bool]:
    """(one review covers every column, union covers every column)."""
    direct = any(all(x == 1 for x in row) for row in matrix)
    mosaic = all(any(row[j] == 1 for row in matrix) for j in range(len(matrix[0])))
    return direct, mosaic


def status(low: bool, high: bool) -> str:
    if low and not high:
        raise ValueError('non-monotone bounds')
    return 'covered' if low else ('undetermined' if high else 'gap')


def summarize(matrix: Sequence[Sequence[Cell]]) -> dict:
    m,n = validate(matrix)
    low = [[0 if x is None else x for x in row] for row in matrix]
    high = [[1 if x is None else x for x in row] for row in matrix]
    ld,lm = boolean_coverage(low)
    ud,um = boolean_coverage(high)
    known = [j for j in range(n) if any(row[j] == 1 for row in matrix)]
    absent = [j for j in range(n) if all(row[j] == 0 for row in matrix)]
    return {'rows':m,'columns':n,'direct':status(ld,ud),'mosaic':status(lm,um),
            'direct_lower':ld,'direct_upper':ud,'mosaic_lower':lm,'mosaic_upper':um,
            'known_covered_columns':known,'definitely_absent_columns':absent,
            'unknown_cells':sum(x is None for row in matrix for x in row)}


def minimal_known_cover(matrix: Sequence[Sequence[Cell]]) -> list[int] | None:
    """Small diagnostic only; bounded to <=16 reviews, enumerated by cardinality."""
    m,n = validate(matrix)
    if m>16:
        raise ValueError('minimal cover enumeration is limited to 16 rows')
    for k in range(1,m+1):
        for chosen in combinations(range(m),k):
            if all(any(matrix[i][j] == 1 for i in chosen) for j in range(n)):
                return list(chosen)
    return None
