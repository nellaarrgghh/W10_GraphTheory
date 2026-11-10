# Week 10: Matching and Coloring

Informatics ITS Graph Theory class Group 6

| Name | NRP |
| --- | --- |
| Naila Sa'ada Cahyani | 5025251258 |
| Lina Fatima Azzahra Badr | 5025251168 |

---

## A. Hungarian Algorithm (Kuhn-Munkres) for the Transportation Problem

### 1. Short explanation about algorithm
The **Hungarian Algorithm (Kuhn-Munkres Algorithm)** finds a minimum-cost perfect matching in a weighted bipartite graph. It solves both one-to-one assignment problems (such as moving bulldozers to construction sites in the Week 11 lecture slides) and general multi-unit transportation problems:

- Unbalanced supply and demand totals are equalized first by inserting a zero-cost dummy source or dummy destination with capacity $|\sum s_i - \sum d_j|$.
- A transportation problem with integer supplies $s_1, \dots, s_m$ and demands $d_1, \dots, d_n$ reduces to an $N \times N$ bipartite assignment matrix ($N = \max(\sum s_i, \sum d_j)$) by splitting each source $i$ into $s_i$ unit vertices and each destination $j$ into $d_j$ unit vertices.
- The algorithm subtracts the minimum entry of each row from its row, then subtracts the minimum entry of each column from its column, creating zero-cost edges without changing the optimal assignment.
- Using maximum bipartite matching on the zero entries and Konig's theorem, the solver finds the minimum number of horizontal and vertical lines needed to cover all zeros.
- While fewer than $N$ lines cover all zeros, the smallest uncovered value is subtracted from every uncovered entry and added to every doubly covered entry. Once $N$ lines are required, a full zero-cost matching exists and is aggregated back into source-to-destination shipment quantities.

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
# Bulldozer assignment problem from the lecture slides (with step-by-step matrices)
python3 main.py samples/bulldozer.txt --steps

# Balanced multi-unit transportation problem
python3 main.py samples/balanced_transport.txt

# Unbalanced transportation problems (surplus supply or unfulfilled demand)
python3 main.py samples/unbalanced_supply.txt
python3 main.py samples/unbalanced_demand.txt
```

#### Run interactively:
```sh
python3 main.py
```
Follow the prompts to enter the dimensions, choose unit assignment (`1`) or custom supplies and demands (`2`), and enter each row of the cost matrix:
```text
Enter a transportation or assignment problem.
Press Ctrl+C to cancel.
Sources and destinations (m n): 2 2
Unit assignment (1) or custom supplies/demands (2)? [1/2]: 2
Supplies (2 positive integers): 3 2
Demands (2 positive integers): 2 2
Cost row 1/2 (2 non-negative integers): 10 20
Cost row 2/2 (2 non-negative integers): 15 12
```

### 4. Result of sample run

#### Sample 1: Bulldozer to Construction Sites (`samples/bulldozer.txt`)
```text
$ python3 main.py samples/bulldozer.txt --steps
Input: bulldozer.txt
Sources: 4 (supplies: 1 1 1 1)
Destinations: 4 (demands: 1 1 1 1)
Status: Balanced (total supply equals total demand)
Expanded Matching Size: 4 x 4

Hungarian Algorithm Steps:
[1] Row reduction:
      15     0     0     5 
       0    50    20    30 
      35     5     0    15 
       0    65    50    70 
[2] Column reduction:
      15     0     0     0 
       0    50    20    25 
      35     5     0    10 
       0    65    50    65 
[3] Zero cover (3/4 lines):
  -   15|    0     0     0 
       0|   50    20    25 
  -   35|    5     0    10 
       0|   65    50    65 
[4] Zero cover (3/4 lines):
  -   35|    0     0|    0 
       0|   30     0|    5 
      55|    5     0|   10 
       0|   45    30|   45 
[5] Zero cover (4/4 lines):
  -   40     0     5     0 
  -    0    25     0     0 
  -   55     0     0     5 
  -    0    40    30    40 

Optimal Shipments:
  Source 1 -> Destination 4: cost 80
  Source 2 -> Destination 3: cost 55
  Source 3 -> Destination 2: cost 95
  Source 4 -> Destination 1: cost 45
Minimum Total Cost: 275
```

#### Sample 2: Balanced Multi-Unit Transportation (`samples/balanced_transport.txt`)
```text
$ python3 main.py samples/balanced_transport.txt
Input: balanced_transport.txt
Sources: 3 (supplies: 2 3 2)
Destinations: 3 (demands: 3 2 2)
Status: Balanced (total supply equals total demand)
Expanded Matching Size: 7 x 7

Optimal Shipments:
  Source 1 -> Destination 3: 2 unit(s) x 10 = 20
  Source 2 -> Destination 1: 3 unit(s) x 9 = 27
  Source 3 -> Destination 2: 2 unit(s) x 9 = 18
Minimum Total Cost: 65
```

#### Sample 3: Unbalanced Supply (`samples/unbalanced_supply.txt`)
```text
$ python3 main.py samples/unbalanced_supply.txt
Input: unbalanced_supply.txt
Sources: 2 (supplies: 3 2)
Destinations: 2 (demands: 2 2)
Status: Unbalanced: added dummy destination with demand 1
Expanded Matching Size: 5 x 5

Optimal Shipments:
  Source 1 -> Destination 1: 2 unit(s) x 10 = 20
  Source 1 -> Dummy Destination: 1 surplus unit(s) (cost 0)
  Source 2 -> Destination 2: 2 unit(s) x 12 = 24
Minimum Total Cost: 44
```

#### Sample 4: Unbalanced Demand (`samples/unbalanced_demand.txt`)
```text
$ python3 main.py samples/unbalanced_demand.txt
Input: unbalanced_demand.txt
Sources: 2 (supplies: 2 1)
Destinations: 2 (demands: 2 2)
Status: Unbalanced: added dummy source with supply 1
Expanded Matching Size: 4 x 4

Optimal Shipments:
  Source 1 -> Destination 2: 2 unit(s) x 8 = 16
  Source 2 -> Destination 1: 1 unit(s) x 9 = 9
  Dummy Source -> Destination 1: 1 unfulfilled unit(s) (cost 0)
Minimum Total Cost: 25
```

#### Summary of Sample Results:
| Input File | Sources ($m$) | Destinations ($n$) | Expanded Size ($N \times N$) | Minimum Total Cost |
| :--- | :---: | :---: | :---: | :---: |
| `samples/bulldozer.txt` | 4 | 4 | $4 \times 4$ | **275** |
| `samples/balanced_transport.txt` | 3 | 3 | $7 \times 7$ | **65** |
| `samples/unbalanced_supply.txt` | 2 | 2 | $5 \times 5$ | **44** |
| `samples/unbalanced_demand.txt` | 2 | 2 | $4 \times 4$ | **25** |

---

## B. [Algorithm Name]

### 1. Short explanation about algorithm

### 2. Prerequisite to run the code, if any

### 3. Instructions to run the code

### 4. Result of sample run


---

## AI Usage Disclosure

### AI Involved:
1. [Insert AI share link here]

