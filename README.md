# Week 10: Matching and Coloring

Informatics ITS Graph Theory class Group 6

| Name | NRP |
| --- | --- |
| Naila Sa'ada Cahyani | 5025251258 |
| Lina Fatima Azzahra Badr | 5025251168 |

---

## A. Hungarian Algorithm (Kuhn-Munkres) — Dynamic $m \times n$ MBG Kitchen-to-School Assignment

### 1. Short explanation about algorithm
The **Hungarian Algorithm (Kuhn-Munkres Algorithm)** finds a minimum-cost one-to-one matching in a weighted bipartite graph. In this implementation, we recreate the lecture's Hungarian Algorithm workflow for a **dynamic $m \times n$ matrix size** and apply it to the **Makan Bergizi Gratis (MBG)** catering distribution problem—assigning $m$ **MBG Kitchens (Dapur SPPG)** to $n$ **Target Schools** to minimize total delivery distance (in km):

1. **Construct & Dynamically Pad the Cost Matrix ($N \times N$):** Given any $m \times n$ distance matrix ($m$ kitchens, $n$ schools), if $m \neq n$, the matrix is automatically padded with zero-cost dummy rows ($m < n$) or dummy columns ($m > n$) to form a square $N \times N$ matrix where $N = \max(m, n)$.
2. **Subtract Row Minimums:** Subtract the smallest entry in each row from all entries in that row.
3. **Subtract Column Minimums:** Subtract the smallest entry in each column from all entries in that column.
4. **Cover All Zeros with Minimum Lines:** Using maximum bipartite matching on the zero entries and König's theorem, cover all zeros using the minimum number of horizontal and vertical lines. If the number of lines equals $N$, an optimal assignment of zeros exists (proceed to Step 6).
5. **Adjust Uncovered Elements:** Find the smallest uncovered value, subtract it from every uncovered element, add it to every doubly covered element (intersection of horizontal and vertical lines), and return to Step 4.
6. **Determine the Optimal Assignment:** Select $N$ independent zero entries (one per row and column) and map them back to the original $m$ MBG kitchens and $n$ schools.

### 2. Prerequisite to run the code, if any
- Python 3.10 or newer.
- No external libraries are needed; the script uses only Python's standard library (`argparse`, `collections`, `pathlib`).

### 3. Instructions to run the code
Ensure your terminal is inside the `W10` directory:

```sh
cd W10
```

#### Run with sample input files:
```sh
# 1. MBG 5x5 square case (5 MBG Kitchens assigned to 5 Schools)
python3 hungarian.py samples/mbg_5x5.txt

# 2. MBG 3x4 rectangular case (3 MBG Kitchens, 4 Schools -> dynamic dummy row padding)
python3 hungarian.py samples/mbg_3x4.txt

# 3. MBG 4x3 rectangular case (4 MBG Kitchens, 3 Schools -> dynamic dummy column padding)
python3 hungarian.py samples/mbg_4x3.txt

# 4. Original 4x4 Bulldozer case from the W11 lecture slides
python3 hungarian.py samples/bulldozer.txt --row-label Bulldozer --col-label "Construction Site"
```

#### Run interactively (custom dynamic $m \times n$ matrix):
```sh
python3 hungarian.py
```
Enter any matrix dimensions `m n` followed by each row of distances:
```text
Hungarian Algorithm - Dynamic m x n Assignment Solver (MBG Kitchen to School)
Press Ctrl+C to cancel.
Matrix size (m rows / kitchens, n columns / schools): 3 3
Row 1/3 (3 non-negative integers): 12 8 11
Row 2/3 (3 non-negative integers): 7 14 9
Row 3/3 (3 non-negative integers): 10 6 13
```

### 4. Result of sample run

#### Sample 1: MBG $5 \times 5$ Assignment (`samples/mbg_5x5.txt`)
Assigning 5 MBG Kitchens (SPPG) to 5 Schools with delivery distances in km:
```text
$ python3 hungarian.py samples/mbg_5x5.txt
Input: mbg_5x5.txt
Dimensions: 5 MBG Kitchen(s) x 5 School(s)
Matrix Status: Square matrix (5 x 5)

Hungarian Algorithm Steps:
[1] Initial cost matrix (N x N):
      18    12    12    14    16 
      10    22    14    17    21 
      24    16    15    19    22 
       9    25    19    21    24 
      21    14    11    17    19 
[2] Row reduction (subtract row minimums):
       6     0     0     2     4 
       0    12     4     7    11 
       9     1     0     4     7 
       0    16    10    12    15 
      10     3     0     6     8 
[3] Column reduction (subtract column minimums):
       6     0     0     0     0 
       0    12     4     5     7 
       9     1     0     2     3 
       0    16    10    10    11 
      10     3     0     4     4 
[4] Cover all zeros (3/5 lines):
  -    6|    0     0|    0     0 
       0|   12     4|    5     7 
       9|    1     0|    2     3 
       0|   16    10|   10    11 
      10|    3     0|    4     4 
[5] Adjust uncovered elements (min uncovered = 1):
       7     0     1     0     0 
       0    11     4     4     6 
       9     0     0     1     2 
       0    15    10     9    10 
      10     2     0     3     3 
[6] Cover all zeros (4/5 lines):
  -    7|    0     1     0     0 
       0|   11     4     4     6 
  -    9|    0     0     1     2 
       0|   15    10     9    10 
  -   10|    2     0     3     3 
[7] Adjust uncovered elements (min uncovered = 4):
      11     0     1     0     0 
       0     7     0     0     2 
      13     0     0     1     2 
       0    11     6     5     6 
      14     2     0     3     3 
[8] Cover all zeros (5/5 lines):
  -   11     0     1     0     0 
  -    0     7     0     0     2 
  -   13     0     0     1     2 
  -    0    11     6     5     6 
  -   14     2     0     3     3 

Optimal Assignment:
  MBG Kitchen 1 -> School 5 : 16 km
  MBG Kitchen 2 -> School 4 : 17 km
  MBG Kitchen 3 -> School 2 : 16 km
  MBG Kitchen 4 -> School 1 : 9 km
  MBG Kitchen 5 -> School 3 : 11 km
Minimum Total Distance / Cost: 69 km
```

#### Sample 2: Dynamic Rectangular $3 \times 4$ MBG Assignment (`samples/mbg_3x4.txt`)
When there are fewer MBG kitchens than schools ($3 \times 4$), the solver pads a zero-cost dummy kitchen row to form a $4 \times 4$ matrix:
```text
$ python3 hungarian.py samples/mbg_3x4.txt
Input: mbg_3x4.txt
Dimensions: 3 MBG Kitchen(s) x 4 School(s)
Matrix Status: Rectangular (3 x 4): padded with 1 zero-cost dummy row(s) to 4 x 4

Hungarian Algorithm Steps:
[1] Initial cost matrix (N x N):
      12     7     9    14 
       8    11     6    10 
      15     9     8    11 
       0     0     0     0 
...
[8] Cover all zeros (4/4 lines):
  -   4    0    3    6 
  -   0    4    0    2 
  -   5    0    0    1 
  -   0    1    2    0 

Optimal Assignment:
  MBG Kitchen 1 -> School 2 : 7 km
  MBG Kitchen 2 -> School 1 : 8 km
  MBG Kitchen 3 -> School 3 : 8 km
  Unassigned (Dummy MBG Kitchen 4) -> School 4 : 0 km
Minimum Total Distance / Cost: 23 km
```

#### Sample 3: Dynamic Rectangular $4 \times 3$ MBG Assignment (`samples/mbg_4x3.txt`)
When there are more MBG kitchens than schools ($4 \times 3$), the solver pads a zero-cost dummy school column to form a $4 \times 4$ matrix:
```text
$ python3 hungarian.py samples/mbg_4x3.txt
Input: mbg_4x3.txt
Dimensions: 4 MBG Kitchen(s) x 3 School(s)
Matrix Status: Rectangular (4 x 3): padded with 1 zero-cost dummy column(s) to 4 x 4

Optimal Assignment:
  MBG Kitchen 1 -> Unassigned (Dummy School 4) : 0 km
  MBG Kitchen 2 -> School 1 : 7 km
  MBG Kitchen 3 -> School 3 : 6 km
  MBG Kitchen 4 -> School 2 : 7 km
Minimum Total Distance / Cost: 20 km
```

#### Summary of Sample Results:
| Input File | Case Description | Original Size ($m \times n$) | Padded Size ($N \times N$) | Minimum Total Distance |
| :--- | :--- | :---: | :---: | :---: |
| `samples/mbg_5x5.txt` | 5 MBG Kitchens to 5 Schools | $5 \times 5$ | $5 \times 5$ | **69 km** |
| `samples/mbg_3x4.txt` | 3 MBG Kitchens to 4 Schools (dummy row) | $3 \times 4$ | $4 \times 4$ | **23 km** |
| `samples/mbg_4x3.txt` | 4 MBG Kitchens to 3 Schools (dummy column) | $4 \times 3$ | $4 \times 4$ | **20 km** |
| `samples/bulldozer.txt` | 4 Bulldozers to 4 Sites (W11 slide baseline) | $4 \times 4$ | $4 \times 4$ | **275 km** |

---

## B. Graph Coloring using a Recursive Backtracking Algorithm

### 1. Short explanation about algorithm
For this assignment, the Sudoku puzzle is modeled as a graph vertex coloring problem where the 81 grid cells act as vertices, the numbers 1 until 9 act as vertex colors, and the adjacency constraints are defined by rows, columns, and local 3x3 sub-grids. Because this is a Constraint Satisfaction problem, standard Greedy coloring is not enough, hence why the implementation of a **Backtracking Algorithm**. It recursively assigns a color to the next unassigned vertex and validates it against all adjacent neighbors. If the program runs into a conflicting state, the algorithm backtracks by resetting the cell and trying the next available color option until a valid coloring for the entire graph is found.

### 2. Prerequisite to run the code, if any
- Python 3.x. 

### 3. Instructions to run the code
1. Move into the `W10` directory
2. Run `sudoku.py` by doing ```py sudoku.py```
3. When prompted, paste a valid 81-character Sudoku puzzle string(using 0 or . for empty cells) and press Enter.

### 4. Result of sample run

Sample 1 (Easy difficulty):
```text
Enter 81-character Sudoku string: 530070000600195000098000060800060003400803001700020006060000280000419005000080079

Solved Sudoku Board:
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
- - - + - - - + - - -
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
- - - + - - - + - - -
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

Sample 2 (Medium difficulty):
```text
Enter 81-character Sudoku string: 003020600900305001001806400008102900700000008006708200002609500800203009005010300

Solved Sudoku Board:
4 8 3 | 9 2 1 | 6 5 7
9 6 7 | 3 4 5 | 8 2 1
2 5 1 | 8 7 6 | 4 9 3
- - - + - - - + - - -
5 4 8 | 1 3 2 | 9 7 6
7 2 9 | 5 6 4 | 1 3 8
1 3 6 | 7 9 8 | 2 4 5
- - - + - - - + - - -
3 7 2 | 6 8 9 | 5 1 4
8 1 4 | 2 5 3 | 7 6 9
6 9 5 | 4 1 7 | 3 8 2
```

Sample 3 (Hard difficulty):
```text
Enter 81-character Sudoku string: 800000000003600000070902000050007000000045700000100030001000068008500010090000400

Solved Sudoku Board:
8 1 2 | 4 5 3 | 6 7 9
9 4 3 | 6 7 1 | 2 8 5
6 7 5 | 9 8 2 | 1 4 3
- - - + - - - + - - -
1 5 4 | 2 3 7 | 8 9 6
3 6 9 | 8 4 5 | 7 2 1
2 8 7 | 1 6 9 | 5 3 4
- - - + - - - + - - -
5 2 1 | 7 9 4 | 3 6 8
4 3 8 | 5 2 6 | 9 1 7
7 9 6 | 3 1 8 | 4 5 2
```

Sample 4 (Row Conflict):
```text
Enter 81-character Sudoku string: 530070005600195000098000060800060003400803001700020006060000280000419005000080079
No solution exists for this puzzle.
```
---

## AI Usage Disclosure

### AI Involved:
1. https://share.gemini.google/YaGgTx7MFLB7
2. https://share.gemini.google/NcVhcgxLTZ9n
