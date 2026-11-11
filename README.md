# TSP bounds solver

Upper and lower bounds for the Travelling Salesman Problem (symmetric and asymmetric), written in Python with NumPy and SciPy.

The Travelling Salesman Problem is NP-hard, so large instances cannot be solved exactly in reasonable time. This project brackets the optimal tour length instead: heuristics give a tour (an upper bound), relaxations give a lower bound, and the gap between the two says how good the tour is without knowing the optimum.

Team project for the Operations Research course at Grenoble INP – Génie Industriel (February–March 2026).

## Methods

| Side | Method | Function in `main.py` | Works on |
| --- | --- | --- | --- |
| Upper bound | Nearest neighbour | `solve_nearest_neighbor` | STSP, ATSP |
| Upper bound | Nearest insertion | `solve_nearest_insertion` | STSP, ATSP |
| Upper bound | Spanning-tree heuristic (2-approximation under the triangle inequality) | `solve_spanning_tree_heuristic` | STSP, ATSP |
| Upper bound | 2-opt local search | `apply_2opt` | STSP |
| Upper bound | Tabu search on 2-opt moves (memory of 10 moves, 50 iterations) | `apply_tabu_search` | STSP |
| Lower bound | Assignment problem relaxation | `compute_assignment_lb` | STSP, ATSP |
| Lower bound | 1-tree | `compute_1tree_lb` | STSP |
| Lower bound | Fractional 2-matching (LP), not part of the benchmark tables | `compute_fractional_2matching_lb` | STSP |
| Lower bound | Dantzig LP with subtour-elimination cutting planes (separation by max-flow) | `compute_dantzig_cutting_planes_stsp` / `_atsp` | STSP, ATSP |
| Lower bound | Lagrangian relaxation of the 1-tree with subgradient updates (300 iterations) | `compute_lagrangian_lb_stsp` | STSP |

## Results

Costs produced by `python main.py` (full output in [`results/benchmark_output.txt`](results/benchmark_output.txt)). The CPLEX column is the team's run of an exact model with a 2-minute limit.

| Instance | Type | Nodes | Best upper bound | Best lower bound | Gap (UB−LB)/LB | CPLEX, 2-minute limit |
| --- | --- | --- | --- | --- | --- | --- |
| instance_8nodes | STSP | 8 | 13 (insertion) | 13 (Lagrangian) | 0% | 13 |
| warehouse_5v_10p | STSP | – | 230 (insertion) | 230 (Lagrangian, Dantzig) | 0% | 230 |
| warehouse_10v_30p | STSP | – | 558 (NN + tabu) | 533.2 (Lagrangian) | 4.7% | 540 |
| warehouse_10v_50p | STSP | – | 548 (2-opt, tabu) | 540.3 (Lagrangian) | 1.4% | not proven: 548 / 534.2 |
| bays29 | STSP | 29 | 2110 (insertion + 2-opt) | 2013.5 (Lagrangian, Dantzig) | 4.8% | 2020 |
| dantzig42 | STSP | 42 | 734 (insertion + 2-opt) | 697 (Lagrangian, Dantzig) | 5.3% | not proven: 699 / 675.9 |
| pr76 | STSP | 76 | 114,262.9 (NN + tabu) | 105,120.3 (Lagrangian, Dantzig) | 8.7% | not proven: 108,137 / 107,235.9 |
| ftv33 | ATSP | 34 | 1504 (insertion) | 1219.5 (Dantzig) | 23.3% | 1286 |
| ftv70 | ATSP | 71 | 2294 (insertion) | 1777 (Dantzig) | 29.1% | 1950 |
| p43 | ATSP | 43 | 5655 (insertion) | 216 (Dantzig) | very large | not proven: 5626 / 5572.8 |

What the numbers show:

- On symmetric instances the bracket is within 9%, and no method takes more than a few seconds.
- The Lagrangian bound matches the cutting-plane LP bound on the TSPLIB instances and beats it on the two larger warehouse instances.
- On asymmetric instances the gap is wide. 2-opt and tabu are not applied (reversing a segment changes its cost), and the lower bounds are weak, especially on p43.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

The script runs every method on the ten instances in `instances/` and prints four tables (costs and run times for upper and lower bounds). It takes a few seconds.

`convert.py` writes each instance as an OPL `.dat` distance matrix for CPLEX (output already in `cplex_dat/`).

## Repository layout

```
main.py              all heuristics, relaxations and the benchmark tables
tsp_instance.py      TSPLIB / ATSP parser (provided by the course staff)
tsp_solution.py      solution container (provided by the course staff)
convert.py           TSPLIB -> CPLEX .dat converter
instances/           10 benchmark instances
cplex_dat/           the same instances as OPL data files
results/             output of the benchmark run
```

## Credits and honesty notes

- **Team:** built by a team of four students; Ahmed Rashed is the member publishing this repository.
- **Course-provided code:** `tsp_instance.py` and `tsp_solution.py` were supplied by the course staff and are not covered by the licence of this repository.
- **AI-assisted parts:** the table-printing block in `main()` and `convert.py` were generated with an AI assistant, as their comments state. The algorithms were written by the team.
- **Instances:** `bays29`, `dantzig42`, `pr76`, `ftv33`, `ftv70` and `p43` come from [TSPLIB](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/). `instance_8nodes` and the `warehouse_*` instances were supplied with the course.
- **Change made for this repo:** two lines were added so the scripts read from `instances/` whatever the working directory. Nothing else was modified.

## Licence

MIT for the team's code (see `LICENSE`).
