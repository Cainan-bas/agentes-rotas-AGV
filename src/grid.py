from .constants import DOCKS, GRID_SIZE, START, TERRAIN_COSTS


def build_grid():
    grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    for col in range(2, 66):
        grid[2][col] = "F"

    for row in range(2, 69):
        grid[row][65] = "F"

    for col in range(4, 62):
        grid[35][col] = "F"

    for row in range(10, 66):
        grid[row][4] = "F"

    for col in range(4, 66):
        grid[60][col] = "F"

    for row in range(8, 20):
        for col in range(42, 50):
            grid[row][col] = "~"

    for row in range(42, 53):
        for col in range(14, 23):
            grid[row][col] = "~"

    for row in range(24, 34):
        for col in range(54, 61):
            grid[row][col] = "L"

    for row in range(50, 62):
        for col in range(43, 51):
            grid[row][col] = "L"

    shelf_gaps = {
        10: {2, 12, 24, 35, 50, 60, 65},
        18: {2, 10, 28, 35, 48, 60, 65},
        28: {2, 16, 30, 35, 52, 60, 65},
        38: {2, 14, 26, 35, 46, 60, 65},
        48: {2, 12, 24, 35, 54, 60, 65},
        58: {2, 18, 32, 35, 50, 60, 65},
    }

    for col, gaps in shelf_gaps.items():
        for row in range(5, 66):
            if row not in gaps:
                grid[row][col] = "X"

    for row in (15, 30, 45, 58):
        for col in range(5, 66):
            if col not in {4, 12, 22, 35, 46, 60, 65}:
                grid[row][col] = "X"

    for row, col in [
        (6, 6),
        (6, 7),
        (22, 22),
        (22, 23),
        (36, 50),
        (51, 8),
        (61, 31),
        (63, 32),
    ]:
        grid[row][col] = "B"

    for row, col in [START, *DOCKS.values()]:
        grid[row][col] = "."

    return grid


GRID = build_grid()


def is_valid_position(position):
    row, col = position

    if row < 0 or row >= len(GRID):
        return False

    if col < 0 or col >= len(GRID[0]):
        return False

    return GRID[row][col] in TERRAIN_COSTS
