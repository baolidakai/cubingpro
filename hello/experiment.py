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

"""
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
