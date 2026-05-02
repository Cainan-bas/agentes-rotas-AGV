from .constants import AGV_CAPACITY, DOCKS, PACKAGES


def manhattan(position_a, position_b):
    row_a, col_a = position_a
    row_b, col_b = position_b
    return abs(row_a - row_b) + abs(col_a - col_b)


def package_dock_position(package_id):
    dock_id = PACKAGES[package_id]["dock"]
    return DOCKS[dock_id]


def choose_next_package(position, delivered):
    pending = [package_id for package_id in PACKAGES if package_id not in delivered]

    if not pending:
        return None

    return min(
        pending,
        key=lambda package_id: (
            -PACKAGES[package_id]["priority"],
            manhattan(position, package_dock_position(package_id)),
            package_id,
        ),
    )


def current_load(delivered):
    return sum(
        package_data["weight"]
        for package_id, package_data in PACKAGES.items()
        if package_id not in delivered
    )


def pending_priority(delivered):
    return sum(
        package_data["priority"]
        for package_id, package_data in PACKAGES.items()
        if package_id not in delivered
    )


def load_label(delivered):
    return f"{current_load(delivered):>2}/{AGV_CAPACITY}"
