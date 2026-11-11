NAME: warehouse_5v_10p
COMMENT: Warehouse TSP instance with realistic structure
COMMENT: Grid dimensions: X=[0, 50], Y=[0, 50]
COMMENT: 5 vertical aisles at x = 10, 20, ..., 50
COMMENT: 2 horizontal aisles at y=0 (bottom) and y=50 (top)
COMMENT: 10 products randomly distributed among aisles
COMMENT: Product distribution per aisle:
COMMENT:   Aisle 1 (x=10): 2 products
COMMENT:   Aisle 2 (x=20): 1 products
COMMENT:   Aisle 3 (x=30): 2 products
COMMENT:   Aisle 4 (x=40): 2 products
COMMENT:   Aisle 5 (x=50): 3 products
COMMENT: Depot at origin (city 0, coordinates 0,0)
COMMENT: Distance: shortest path through warehouse (via bottom or top aisle)
TYPE: TSP
DIMENSION: 11
EDGE_WEIGHT_TYPE: EXPLICIT
EDGE_WEIGHT_FORMAT: FULL_MATRIX

NODE_COORD_SECTION
1 0 0
2 10 44
3 50 11
4 30 48
5 10 2
6 40 48
7 20 8
8 50 44
9 40 48
10 30 45
11 50 6

EDGE_WEIGHT_SECTION
0 54 61 78 12 88 28 94 88 75 56 
54 0 85 28 42 38 58 52 38 31 90 
61 85 0 61 53 51 49 33 51 64 5 
78 28 61 0 70 14 54 28 14 3 66 
12 42 53 70 0 80 20 86 80 67 48 
88 38 51 14 80 0 64 18 0 17 56 
28 58 49 54 20 64 0 78 64 57 44 
94 52 33 28 86 18 78 0 18 31 38 
88 38 51 14 80 0 64 18 0 17 56 
75 31 64 3 67 17 57 31 17 0 69 
56 90 5 66 48 56 44 38 56 69 0 
EOF
