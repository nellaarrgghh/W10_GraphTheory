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
    """Solve an N x N assignment matrix using the Kuhn-Munkres steps from W11."""
    size = len(cost_matrix)
    if size == 0:
        return [], []

    work = [row[:] for row in cost_matrix]
    steps = []

    for r in range(size):
        row_min = min(work[r])
        for c in range(size):
            work[r][c] -= row_min
    steps.append(('Row reduction', [row[:] for row in work], None, None))

    for c in range(size):
        col_min = min(work[r][c] for r in range(size))
        for r in range(size):
            work[r][c] -= col_min
    steps.append(('Column reduction', [row[:] for row in work], None, None))

    while True:
        row_match, col_match = _max_zero_matching(work)
        covered_rows, covered_cols = _min_line_cover(work, row_match, col_match)
        line_count = sum(covered_rows) + sum(covered_cols)
        steps.append((
            f'Zero cover ({line_count}/{size} lines)',
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


def solve_transportation(costs, supplies, demands):
    """Reduce a transportation instance to bipartite matching via unit splitting."""
    total_supply = sum(supplies)
    total_demand = sum(demands)
    adj_supplies = list(supplies)
    adj_demands = list(demands)
    adj_costs = [row[:] for row in costs]
    balance_note = 'Balanced (total supply equals total demand)'

    # Pad unbalanced instances with a zero-cost dummy row or column so every unit matches.
    if total_supply > total_demand:
        diff = total_supply - total_demand
        adj_demands.append(diff)
        for row in adj_costs:
            row.append(0)
        balance_note = f'Unbalanced: added dummy destination with demand {diff}'
    elif total_demand > total_supply:
        diff = total_demand - total_supply
        adj_supplies.append(diff)
        adj_costs.append([0] * len(adj_demands))
        balance_note = f'Unbalanced: added dummy source with supply {diff}'

    row_map = [i for i, s in enumerate(adj_supplies) for _ in range(s)]
    col_map = [j for j, d in enumerate(adj_demands) for _ in range(d)]

    expanded_matrix = [
        [adj_costs[r_orig][c_orig] for c_orig in col_map]
        for r_orig in row_map
    ]

    row_match, steps = hungarian(expanded_matrix)

    m, n = len(costs), len(costs[0])
    allocation = [[0] * len(adj_demands) for _ in range(len(adj_supplies))]
    for unit_r, unit_c in enumerate(row_match):
        allocation[row_map[unit_r]][col_map[unit_c]] += 1

    total_cost = sum(
        allocation[i][j] * costs[i][j]
        for i in range(m)
        for j in range(n)
    )

    return {
        'allocation': allocation,
        'real_shape': (m, n),
        'total_cost': total_cost,
        'balance_note': balance_note,
        'expanded_size': len(expanded_matrix),
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
    """Read either an m x n assignment cost matrix or a supply/demand transportation file."""
    lines = []
    for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
        clean = raw.split('#', 1)[0].strip()
        if clean:
            lines.append(clean)
    if not lines:
        raise ValueError('Input file is empty; expected m n on the first line')

    m, n = _parse_int_list(lines[0], 2, 'Header line (m n)')
    if m <= 0 or n <= 0:
        raise ValueError('Number of sources and destinations must be positive')

    remaining = lines[1:]
    if len(remaining) == m:
        supplies = [1] * m
        demands = [1] * n
        cost_lines = remaining
    elif len(remaining) == m + 2:
        supplies = _parse_int_list(remaining[0], m, 'Supply line')
        demands = _parse_int_list(remaining[1], n, 'Demand line')
        if any(s <= 0 for s in supplies) or any(d <= 0 for d in demands):
            raise ValueError('Supplies and demands must be positive integers')
        cost_lines = remaining[2:]
    else:
        raise ValueError(
            f'Expected {m} cost rows (unit assignment) or 2 supply/demand lines + {m} cost rows, '
            f'found {len(remaining)} lines after header'
        )

    costs = [
        _parse_int_list(row_line, n, f'Cost row {idx + 1}')
        for idx, row_line in enumerate(cost_lines)
    ]
    if any(c < 0 for row in costs for c in row):
        raise ValueError('Transportation costs cannot be negative')
    return costs, supplies, demands


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
    print('Enter a transportation or assignment problem.')
    print('Press Ctrl+C to cancel.')
    m, n = _prompt_int_list('Sources and destinations (m n): ', 2)
    mode = input('Unit assignment (1) or custom supplies/demands (2)? [1/2]: ').strip()
    if mode == '2':
        supplies = _prompt_int_list(f'Supplies ({m} positive integers): ', m)
        demands = _prompt_int_list(f'Demands ({n} positive integers): ', n)
    else:
        supplies = [1] * m
        demands = [1] * n
    costs = [
        _prompt_int_list(f'Cost row {i + 1}/{m} ({n} non-negative integers): ', n, allow_zero=True)
        for i in range(m)
    ]
    return costs, supplies, demands


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
        description='Solve the Transportation Problem using the Hungarian matching algorithm'
    )
    parser.add_argument(
        'input', type=Path, nargs='?',
        help='Optional problem file; omit to enter values interactively'
    )
    parser.add_argument(
        '--steps', action='store_true',
        help='Print intermediate Hungarian reduction and zero-cover matrices'
    )
    args = parser.parse_args()

    try:
        costs, supplies, demands = (
            read_problem(args.input) if args.input else read_interactive()
        )
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, '\nInput cancelled.\n')
    except (OSError, ValueError) as error:
        parser.error(str(error))

    result = solve_transportation(costs, supplies, demands)
    m, n = result['real_shape']
    allocation = result['allocation']

    print(f'Input: {args.input.name if args.input else "interactive"}')
    print(f'Sources: {m} (supplies: {" ".join(map(str, supplies))})')
    print(f'Destinations: {n} (demands: {" ".join(map(str, demands))})')
    print(f'Status: {result["balance_note"]}')
    print(f'Expanded Matching Size: {result["expanded_size"]} x {result["expanded_size"]}')

    if args.steps:
        print('\nHungarian Algorithm Steps:')
        for idx, (title, mat, cov_r, cov_c) in enumerate(result['steps'], start=1):
            print(f'[{idx}] {title}:')
            print(_format_matrix(mat, cov_r, cov_c))

    print('\nOptimal Shipments:')
    unit_mode = all(s == 1 for s in supplies) and all(d == 1 for d in demands) and m == n
    for i in range(len(allocation)):
        for j in range(len(allocation[0])):
            shipped = allocation[i][j]
            if shipped == 0:
                continue
            if i < m and j < n:
                unit_cost = costs[i][j]
                if unit_mode:
                    print(f'  Source {i + 1} -> Destination {j + 1}: cost {unit_cost}')
                else:
                    subtotal = shipped * unit_cost
                    print(
                        f'  Source {i + 1} -> Destination {j + 1}: '
                        f'{shipped} unit(s) x {unit_cost} = {subtotal}'
                    )
            elif i >= m:
                print(
                    f'  Dummy Source -> Destination {j + 1}: '
                    f'{shipped} unfulfilled unit(s) (cost 0)'
                )
            else:
                print(
                    f'  Source {i + 1} -> Dummy Destination: '
                    f'{shipped} surplus unit(s) (cost 0)'
                )

    print(f'Minimum Total Cost: {result["total_cost"]}')


if __name__ == '__main__':
    main()
