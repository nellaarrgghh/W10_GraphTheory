def solve_sudoku(board):
    """Solves Sudoku using graph coloring and recursive backtracking."""
    empty = find_unassigned_vertex(board)
    if not empty:
        return True  # All vertices colored successfully
    
    row, col = empty

    # Try colors (numbers 1 through 9)
    for color in range(1, 10):
        if is_safe(board, row, col, color):
            board[row][col] = color  # Assign color
            
            if solve_sudoku(board):
                return True
                
            board[row][col] = 0  # Backtrack (reset color)
            
    return False

def find_unassigned_vertex(board):
    """Finds the next unassigned cell (vertex with color 0)."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def is_safe(board, row, col, color):
    """Checks if assigning a color violates any adjacency constraints (row, col, box)."""
    # Check row adjacency
    if color in board[row]:
        return False

    # Check column adjacency
    if color in [board[i][col] for i in range(9)]:
        return False

    # Check 3x3 box adjacency
    box_row, box_col = row - row % 3, col - col % 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == color:
                return False

    return True

def parse_sudoku_string(s):
    """Converts an 81-character string (using '0' or '.' for blanks) into a 9x9 grid."""
    s = s.replace(".", "0").replace(" ", "").replace("\n", "")
    return [[int(s[r * 9 + c]) for c in range(9)] for r in range(9)]

def print_pretty_board(board):
    """Prints the solved Sudoku board in a clean grid format."""
    print("\nSolved Sudoku Board:")
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("- - - + - - - + - - -")
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            row_str += str(board[r][c]) + " "
        print(row_str)

if __name__ == "__main__":
    # Take input as an 81-character string (0 or . for empty cells)
    puzzle_input = input("Enter 81-character Sudoku string: ").strip()
    
    if not puzzle_input:
        print("No input was given.")
    else:
        grid =  parse_sudoku_string(puzzle_input)

        if solve_sudoku(grid):
            print_pretty_board(grid)
        else:
            print("No solution exists for this puzzle.")