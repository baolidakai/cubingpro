# Brute force search for short skewb algorithms to solve intermediate cases.
def get_skewb_color_from_alg(alg):
    moves = alg.strip().split()
    moves = moves[::-1]

    def convert(move):
        if move == "H":
            return "S"
        elif move == "S":
            return "H"
        elif move == "y2":
            return "y2"
        elif move == "y'":
            return "y"
        elif move == "y":
            return "y'"
        elif move == "x":
            return "x'"
        elif move == "x'":
            return "x"
        elif move == "x2":
            return "x2"
        elif move == "z":
            return "z'"
        elif move == "z'":  
            return "z"
        elif move == "z2":
            return "z2"
        else:
            return move

    converted = [convert(m) for m in moves]
    curr = ["y"] * 5 + ["r"] * 5 + ["g"] * 5 + ["o"] * 5 + ["b"] * 5 + ["w"] * 5
    move_dict = {
        "H": [
            [0, 21, 5],
            [1, 16, 20],
            [2, 15, 11],
            [3, 10, 6],
            [4, 14],
            [9, 19],
        ],
        "S": [
            [0, 5, 21],
            [1, 20, 16],
            [2, 11, 15],
            [3, 6, 10],
            [4, 14],
            [9, 19],
        ],
        "y": [
            [0, 1, 2, 3],
            [5, 20, 15, 10],
            [6, 21, 16, 11],
            [7, 22, 17, 12],
            [8, 23, 18, 13],
            [9, 24, 19, 14],
        ],
        "y'": [
            [0, 3, 2, 1],
            [5, 10, 15, 20],
            [6, 11, 16, 21],
            [7, 12, 17, 22],
            [8, 13, 18, 23],
            [9, 14, 19, 24],
        ],
        "y2": [
            [0, 2], [1, 3],
            [5, 15], [20, 10],
            [6, 16], [21, 11],
            [7, 17], [22, 12],
            [8, 18], [23, 13],
            [9, 19], [24, 14],
        ],
        "x": [
            [0, 22, 25, 10],
            [1, 23, 26, 11],
            [2, 20, 27, 12],
            [3, 21, 28, 13],
            [4, 24, 29, 14],
            [5, 8, 7, 6],
            [15, 16, 17, 18],
        ],
        "x'": [
            [0, 10, 25, 22],
            [1, 11, 26, 23],
            [2, 12, 27, 20],
            [3, 13, 28, 21],
            [4, 14, 29, 24],
            [5, 6, 7, 8],
            [15, 18, 17, 16],
        ],
        "x2": [
            [0, 25], [10, 22],
            [1, 26], [11, 23],
            [2, 27], [12, 20],
            [3, 28], [13, 21],
            [4, 29], [14, 24],
            [5, 7], [6, 8],
            [15, 17], [16, 18],
        ],
        "z": [
            [0, 16, 27, 8],
            [1, 17, 28, 5],
            [2, 18, 25, 6],
            [3, 15, 26, 7],
            [4, 19, 29, 9],
            [10, 11, 12, 13],
            [20, 23, 22, 21],
        ],
        "z'": [
            [0, 8, 27, 16],
            [1, 5, 28, 17],
            [2, 6, 25, 18],
            [3, 7, 26, 15],
            [4, 9, 29, 19],
            [10, 13, 12, 11],
            [20, 21, 22, 23],
        ],
        "z2": [
            [0, 27], [16, 8],
            [1, 28], [17, 5],
            [2, 25], [18, 6],
            [3, 26], [15, 7],
            [4, 29], [19, 9],
            [10, 12], [11, 13],
            [20, 22], [21, 23],
        ],
    }
    for m in converted:
        nxt = curr[:]
        for cyc in move_dict.get(m, []):
            for i in range(len(cyc)):
                src = cyc[i]
                dst = cyc[(i + 1) % len(cyc)]
                nxt[dst] = curr[src]
        curr = nxt[:]
    return "".join(curr)

from itertools import product
from collections import defaultdict

mapping = defaultdict(list)
def translate(color):
    return ''.join(['y' if c == 'y' else ' ' for c in color])
for move_count in range(1, 4):
    moves = ['S', 'H']
    y_mods = ['', 'y', "y'", 'y2']

    # Generate all sequences of length move_count
    for seq in product(moves, repeat=move_count):
        for mods in product(y_mods, repeat=move_count):
            alg = ' '.join(f"{mod} {m}".strip() for m, mod in zip(seq, mods))
            color = get_skewb_color_from_alg(alg)
            if all([color[i] == 'y' for i in [5, 10, 11, 16]]) or all([color[i] == 'y' for i in [0, 2, 10, 16]]):
                mapping[translate(color)].append(alg)
for key in mapping:
    min_count = min(alg.count('S') + alg.count('H') for alg in mapping[key])
    shortest = [alg for alg in mapping[key] if alg.count('S') + alg.count('H') == min_count]
    print(f"{key}: {shortest}")

"""
# Computes the probability of having a 6 mover 3e for fewest moves
from collections import defaultdict, deque


R = {"RU": "RB", "RB": "RD", "RD": "RF", "RF": "RU"}
L = {"LU": "LF", "LF": "LD", "LD": "LB", "LB": "LU"}
U = {"UF": "UL", "UL": "UB", "UB": "UR", "UR": "UF"}
D = {"DF": "DR", "DR": "DB", "DB": "DL", "DL": "DF"}
F = {'FR': 'FD', 'FD': 'FL', 'FL': 'FU', 'FU': 'FR'}
B = {'BR': 'BU', 'BU': 'BL', 'BL': 'BD', 'BD': 'BR'}
def augment(move_dict):
    # Augment the move dictionary with reversed keys and values
    augmented = move_dict.copy()
    for k, v in move_dict.items():
        # Add the reversed mapping
        augmented[k[1] + k[0]] = v[1] + v[0]
    return augmented
moves = list(map(augment, [R, L, U, D, F, B]))
def get_inv(move_dict):
    return {v: k for k, v in move_dict.items()}
inv_moves = list(map(get_inv, moves))
def get_double(move_dict):
    return {k: move_dict[move_dict[k]] for k in move_dict}
double_moves = list(map(get_double, moves))
moves = moves + inv_moves + double_moves
edges = sorted({key for move in moves for key in move.keys()})
# Group edges according to whether they can be achievable in double moves only.
# Build adjacency list where each edge is connected to its double move
adj = defaultdict(list)
for move in double_moves:
    for k, v in move.items():
        adj[k].append(v)
        adj[v].append(k)
# Find groups using BFS
visited = set()
groups = []
for edge in edges:
    if edge not in visited:
        group = []
        queue = deque([edge])
        while queue:
            curr = queue.popleft()
            if curr not in visited:
                visited.add(curr)
                group.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        groups.append(sorted(group))
# Now run the simulation, for each simulation, generate three edges randomly, then make N random moves
# and see if they show up in the same group.
import random
random.seed(42)  # For reproducibility
def simulate_once(num_moves = 20, allow_setup = False):
    # Randomly select three edges
    selected_edges = random.sample(edges, 3)
    while any(sorted(selected_edges[i]) == sorted(selected_edges[j]) for i in range(3) for j in range(i + 1, 3)):
        selected_edges = random.sample(edges, 3)
    # Perform random moves
    for _ in range(num_moves):
        move = random.choice(moves)
        selected_edges = [move.get(edge, edge) for edge in selected_edges]
        # Check if all selected edges are still in the same group
        new_group_set = set()
        for edge in selected_edges:
            for i, group in enumerate(groups):
                if edge in group:
                    new_group_set.add(i)
                    break
        if len(new_group_set) == 1:
            return True
        if allow_setup:
            for setup in moves:
                new_selected_edges = [setup.get(edge, edge) for edge in selected_edges]
                new_group_set = set()
                for edge in new_selected_edges:
                    for i, group in enumerate(groups):
                        if edge in group:
                            new_group_set.add(i)
                            break
                if len(new_group_set) == 1:
                    return True
    return False

for num_moves in range(1, 30):
    tot = 10000
    cnt = 0
    for _ in range(tot):
        if simulate_once(num_moves, allow_setup=False):
            cnt += 1
    print(f"Probability of having a 6 mover 3e for {num_moves} moves: {cnt / tot:.4f}")
    
for num_moves in range(1, 30):
    tot = 10000
    cnt = 0
    for _ in range(tot):
        if simulate_once(num_moves, allow_setup=True):
            cnt += 1
    print(f"Probability of having a 8 mover 3e with setup for {num_moves} moves: {cnt / tot:.4f}")

from itertools import product
from collections import deque, defaultdict

# Define the range of values for X1, X2, X3, X4, X5
values = range(12)

# Initialize a counter for valid combinations
valid_combinations = 0

# Total number of combinations
total_combinations = 12 ** 5

# Iterate through all possible combinations of X1, X2, X3, X4, X5
for combination in product(values, repeat=5):
    X1, X2, X3, X4, X5 = combination
    # Check if at least one condition is satisfied
    if (X1 == X2 or X1 == X3 or X1 == X4 or X1 == X5 or
        X2 == X3 or X3 == X4 or X4 == X5 or X5 == X2):
        valid_combinations += 1

# Calculate the ratio
ratio = valid_combinations / total_combinations

# Print the results
print(f"Number of valid combinations: {valid_combinations}")
print(f"Total number of combinations: {total_combinations}")
print(f"Ratio: {ratio}")
"""
