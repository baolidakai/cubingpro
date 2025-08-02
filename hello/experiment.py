from itertools import product

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