import argparse
from collections import deque
from pathlib import Path


def _zero_candidates(row, col_match):
    size = len(row)
    unmatched = [c for c in range(size - 1, -1, -1) if row[c] == 0 and col_match[c] == -1]
    matched = [c for c in range(size - 1, -1, -1) if row[c] == 0 and col_match[c] != -1]
    return iter(unmatched + matched)


def _max_zero_matching(matrix):
    size = len(matrix)
    row_match = [-1] * size
    col_match = [-1] * size

    for r in range(size):
        visited = [False] * size
        # Prefer unmatched zero columns first to avoid unnecessary augmentations.
        stack = [(r, _zero_candidates(matrix[r], col_match))]
        parent = {}
        matched_col = -1

        while stack and matched_col == -1:
            curr_r, cols = stack[-1]
            c = next(cols, None)
            if c is None:
                stack.pop()
                continue
            if visited[c]:
                continue
            visited[c] = True
            parent[c] = curr_r
            next_r = col_match[c]
            if next_r == -1:
                matched_col = c
            else:
                stack.append((next_r, _zero_candidates(matrix[next_r], col_match)))

        if matched_col != -1:
            c = matched_col
            while c != -1:
                r_prev = parent[c]
                next_c = row_match[r_prev]
                row_match[r_prev] = c
                col_match[c] = r_prev
                c = next_c

    return row_match, col_match


def _min_line_cover(matrix, row_match, col_match):
    # Konig's theorem: alternating reachability from unmatched rows yields a
    # minimum vertex cover of all zero entries using (unvisited rows) U (visited cols).
    size = len(matrix)
    visited_rows = [r == -1 for r in row_match]
    visited_cols = [False] * size
    queue = deque(r for r, m in enumerate(row_match) if m == -1)

    while queue:
        r = queue.popleft()
        for c in range(size):
            if matrix[r][c] == 0 and not visited_cols[c]:
                visited_cols[c] = True
                next_r = col_match[c]
                if next_r != -1 and not visited_rows[next_r]:
                    visited_rows[next_r] = True
                    queue.append(next_r)

    covered_rows = [not v for v in visited_rows]
    covered_cols = visited_cols
    return covered_rows, covered_cols


def hungarian(cost_matrix):
    size = len(cost_matrix)
    if size == 0:
        return [], []

    work = [row[:] for row in cost_matrix]
    steps = [('Initial cost matrix (N x N)', [row[:] for row in work], None, None)]

    for r in range(size):
        row_min = min(work[r])
        for c in range(size):
            work[r][c] -= row_min
    steps.append(('Row reduction (subtract row minimums)', [row[:] for row in work], None, None))

    for c in range(size):
        col_min = min(work[r][c] for r in range(size))
        for r in range(size):
            work[r][c] -= col_min
    steps.append(('Column reduction (subtract column minimums)', [row[:] for row in work], None, None))

    while True:
        row_match, col_match = _max_zero_matching(work)
        covered_rows, covered_cols = _min_line_cover(work, row_match, col_match)
        line_count = sum(covered_rows) + sum(covered_cols)
        steps.append((
            f'Cover all zeros ({line_count}/{size} lines)',
            [row[:] for row in work],
            covered_rows,
            covered_cols,
        ))
        if line_count == size:
            return row_match, steps

        min_uncovered = min(
            work[r][c]
            for r in range(size) if not covered_rows[r]
            for c in range(size) if not covered_cols[c]
        )
        for r in range(size):
            for c in range(size):
                if not covered_rows[r] and not covered_cols[c]:
                    work[r][c] -= min_uncovered
                elif covered_rows[r] and covered_cols[c]:
                    work[r][c] += min_uncovered
        steps.append((
            f'Adjust uncovered elements (min uncovered = {min_uncovered})',
            [row[:] for row in work],
            None,
            None,
        ))


def solve_assignment(costs):
    """Solve a dynamic m x n assignment matrix by padding to N x N if rectangular."""
    m = len(costs)
    n = len(costs[0])
    size = max(m, n)

    padded = [
        [costs[r][c] if (r < m and c < n) else 0 for c in range(size)]
        for r in range(size)
    ]

    if m == n:
        shape_note = f'Square matrix ({m} x {n})'
    elif m < n:
        shape_note = f'Rectangular ({m} x {n}): padded with {n - m} zero-cost dummy row(s) to {size} x {size}'
    else:
        shape_note = f'Rectangular ({m} x {n}): padded with {m - n} zero-cost dummy column(s) to {size} x {size}'

    row_match, steps = hungarian(padded)

    assignments = []
    total_cost = 0
    for r, c in enumerate(row_match):
        if r < m and c < n:
            cost = costs[r][c]
            total_cost += cost
            assignments.append((r, c, cost, 'matched'))
        elif r < m and c >= n:
            assignments.append((r, c, 0, 'dummy_col'))
        elif r >= m and c < n:
            assignments.append((r, c, 0, 'dummy_row'))

    return {
        'assignments': assignments,
        'original_shape': (m, n),
        'padded_size': size,
        'shape_note': shape_note,
        'total_cost': total_cost,
        'steps': steps,
    }


def _parse_int_list(line, expected_len, label):
    try:
        values = list(map(int, line.split()))
    except ValueError:
        raise ValueError(f'{label} must contain only integers') from None
    if len(values) != expected_len:
        raise ValueError(f'{label} must contain {expected_len} integers, found {len(values)}')
    return values


def read_problem(path):
    """Read an m x n cost matrix from a text file."""
    lines = []
    for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
        clean = raw.split('#', 1)[0].strip()
        if clean:
            lines.append(clean)
    if not lines:
        raise ValueError('Input file is empty; expected "m n" on the first line')

    m, n = _parse_int_list(lines[0], 2, 'Header line (m n)')
    if m <= 0 or n <= 0:
        raise ValueError('Matrix dimensions m and n must be positive integers')

    remaining = lines[1:]
    if len(remaining) != m:
        raise ValueError(f'Expected {m} cost rows after header, found {len(remaining)}')

    costs = [
        _parse_int_list(row_line, n, f'Row {idx + 1}')
        for idx, row_line in enumerate(remaining)
    ]
    if any(c < 0 for row in costs for c in row):
        raise ValueError('Matrix costs/distances cannot be negative')
    return costs


def _prompt_int_list(prompt, expected_len, allow_zero=False):
    while True:
        try:
            values = _parse_int_list(input(prompt), expected_len, 'Input')
            if allow_zero and any(v < 0 for v in values):
                raise ValueError('Values cannot be negative')
            if not allow_zero and any(v <= 0 for v in values):
                raise ValueError('Values must be positive integers')
            return values
        except ValueError as error:
            print(error)


def read_interactive():
    print('Hungarian Algorithm - Dynamic m x n Assignment Solver (MBG Kitchen to School)')
    print('Press Ctrl+C to cancel.')
    m, n = _prompt_int_list('Matrix size (m rows / kitchens, n columns / schools): ', 2)
    costs = [
        _prompt_int_list(f'Row {i + 1}/{m} ({n} non-negative integers): ', n, allow_zero=True)
        for i in range(m)
    ]
    return costs


def _format_matrix(matrix, covered_rows=None, covered_cols=None):
    width = max(len(str(val)) for row in matrix for val in row) + 2
    lines = []
    for r, row in enumerate(matrix):
        row_mark = '-' if (covered_rows and covered_rows[r]) else ' '
        cells = []
        for c, val in enumerate(row):
            col_mark = '|' if (covered_cols and covered_cols[c]) else ' '
            cells.append(f'{val:>{width}}{col_mark}')
        lines.append(f'  {row_mark} ' + ' '.join(cells))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Solve a dynamic m x n assignment problem using the Hungarian Algorithm (Kuhn-Munkres)'
    )
    parser.add_argument(
        'input', type=Path, nargs='?',
        help='Optional matrix file; omit to enter dimensions and values interactively'
    )
    parser.add_argument(
        '--no-steps', action='store_true',
        help='Hide intermediate Hungarian reduction and zero-cover matrices'
    )
    parser.add_argument(
        '--steps', action='store_true',
        help='Show intermediate Hungarian reduction and zero-cover matrices (default)'
    )
    parser.add_argument(
        '--row-label', default='MBG Kitchen',
        help='Label for row entities (default: "MBG Kitchen")'
    )
    parser.add_argument(
        '--col-label', default='School',
        help='Label for column entities (default: "School")'
    )
    args = parser.parse_args()

    try:
        costs = read_problem(args.input) if args.input else read_interactive()
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, '\nInput cancelled.\n')
    except (OSError, ValueError) as error:
        parser.error(str(error))

    result = solve_assignment(costs)
    m, n = result['original_shape']

    print(f'Input: {args.input.name if args.input else "interactive"}')
    print(f'Dimensions: {m} {args.row_label}(s) x {n} {args.col_label}(s)')
    print(f'Matrix Status: {result["shape_note"]}')

    if not args.no_steps:
        print('\nHungarian Algorithm Steps:')
        for idx, (title, mat, cov_r, cov_c) in enumerate(result['steps'], start=1):
            print(f'[{idx}] {title}:')
            print(_format_matrix(mat, cov_r, cov_c))

    print('\nOptimal Assignment:')
    for r, c, cost, status in result['assignments']:
        if status == 'matched':
            print(f'  {args.row_label} {r + 1} -> {args.col_label} {c + 1} : {cost} km')
        elif status == 'dummy_col':
            print(f'  {args.row_label} {r + 1} -> Unassigned (Dummy {args.col_label} {c + 1}) : 0 km')
        elif status == 'dummy_row':
            print(f'  Unassigned (Dummy {args.row_label} {r + 1}) -> {args.col_label} {c + 1} : 0 km')

    print(f'Minimum Total Distance / Cost: {result["total_cost"]} km')


if __name__ == '__main__':
    main()
