import random


# Each roll generates this many random numbers.
NUMBERS_PER_ROLL = 3


def simulate_round(
    rng,
    minimum,
    maximum,
    target_to_index,
    target_count,
    rolls_per_round,
):
    """
    rolls_per_round > 0:
        Run exactly that many rolls.

    rolls_per_round == 0:
        Continue until every target has at least one valid hit.
    """

    # first_hits[index] contains the earliest valid roll for that target.
    first_hits = [None] * target_count

    targets_remaining = target_count
    roll_number = 0

    while (
        roll_number < rolls_per_round
        if rolls_per_round > 0
        else targets_remaining > 0
    ):
        roll_number += 1

        first_target_index = -1
        multiple_different_targets = False

        # Generate the three numbers for this roll.
        for _ in range(NUMBERS_PER_ROLL):
            value = rng.randint(minimum, maximum)
            target_index = target_to_index.get(value)

            # The generated number was not one of the targets.
            if target_index is None:
                continue

            # This is the first target found during this roll.
            if first_target_index == -1:
                first_target_index = target_index

            # A different target also appeared during the same roll.
            elif target_index != first_target_index:
                multiple_different_targets = True

        # Accept only rolls containing exactly one distinct target.
        #
        # Examples:
        # [target1, target1, 7] -> accepted
        # [target1, target2, 7] -> discarded
        if first_target_index != -1 and not multiple_different_targets:
            if first_hits[first_target_index] is None:
                first_hits[first_target_index] = roll_number
                targets_remaining -= 1

    return first_hits, roll_number


def hungarian(cost):
    """
    Finds the minimum-cost one-to-one assignment.

    Rows represent target numbers.
    Columns represent rounds.

    Returns:
        assignment[target_index] = round_index

    There must be at least as many rounds as target numbers.
    """

    row_count = len(cost)
    column_count = len(cost[0])

    if row_count > column_count:
        raise ValueError(
            "There must be at least as many rounds as target numbers."
        )

    row_potential = [0] * (row_count + 1)
    column_potential = [0] * (column_count + 1)

    matched_row = [0] * (column_count + 1)
    previous_column = [0] * (column_count + 1)

    for row_to_add in range(1, row_count + 1):
        matched_row[0] = row_to_add

        minimum_reduced_cost = [float("inf")] * (column_count + 1)
        used_column = [False] * (column_count + 1)

        column = 0

        while True:
            used_column[column] = True
            current_row = matched_row[column]

            delta = float("inf")
            next_column = 0

            for candidate_column in range(1, column_count + 1):
                if used_column[candidate_column]:
                    continue

                reduced_cost = (
                    cost[current_row - 1][candidate_column - 1]
                    - row_potential[current_row]
                    - column_potential[candidate_column]
                )

                if reduced_cost < minimum_reduced_cost[candidate_column]:
                    minimum_reduced_cost[candidate_column] = reduced_cost
                    previous_column[candidate_column] = column

                if minimum_reduced_cost[candidate_column] < delta:
                    delta = minimum_reduced_cost[candidate_column]
                    next_column = candidate_column

            for candidate_column in range(column_count + 1):
                if used_column[candidate_column]:
                    row_potential[matched_row[candidate_column]] += delta
                    column_potential[candidate_column] -= delta
                else:
                    minimum_reduced_cost[candidate_column] -= delta

            column = next_column

            if matched_row[column] == 0:
                break

        while True:
            old_column = previous_column[column]
            matched_row[column] = matched_row[old_column]
            column = old_column

            if column == 0:
                break

    assignment = [-1] * row_count

    for column in range(1, column_count + 1):
        if matched_row[column] != 0:
            target_index = matched_row[column] - 1
            round_index = column - 1
            assignment[target_index] = round_index

    return assignment


def main():
    minimum = int(input("Minimum value: "))
    maximum = int(input("Maximum value: "))

    if minimum > maximum:
        raise ValueError("Minimum cannot be greater than maximum.")

    target_count_text = input(
        "Number of target numbers [4]: "
    ).strip()

    target_count = int(target_count_text or 4)

    if target_count < 1:
        raise ValueError("There must be at least one target number.")

    targets = []

    for index in range(target_count):
        target = int(input(f"Target number {index + 1}: "))

        if not minimum <= target <= maximum:
            raise ValueError(
                f"Target {target} is outside the range "
                f"{minimum} to {maximum}."
            )

        if target in targets:
            raise ValueError("Target numbers must be different.")

        targets.append(target)

    round_count_text = input(
        f"Number of rounds [{target_count}]: "
    ).strip()

    round_count = int(round_count_text or target_count)

    if round_count < target_count:
        raise ValueError(
            "You need at least as many rounds as target numbers."
        )

    rolls_text = input(
        "Rolls per round [1000], "
        "or 0 to continue until every target is hit: "
    ).strip()

    rolls_per_round = int(rolls_text or 1000)

    if rolls_per_round < 0:
        raise ValueError("Rolls per round cannot be negative.")

    # Allows target lookup in approximately constant time.
    target_to_index = {
        target: index
        for index, target in enumerate(targets)
    }

    rng = random.Random()

    # round_results[round_index][target_index]
    round_results = []

    print("\nRunning simulation...\n")

    for round_index in range(round_count):
        first_hits, rolls_run = simulate_round(
            rng=rng,
            minimum=minimum,
            maximum=maximum,
            target_to_index=target_to_index,
            target_count=target_count,
            rolls_per_round=rolls_per_round,
        )

        round_results.append(first_hits)

        print(f"Round {round_index + 1} ({rolls_run} rolls):")

        for target, hit_roll in zip(targets, first_hits):
            if hit_roll is None:
                print(f"  Target {target}: not hit")
            else:
                print(
                    f"  Target {target}: "
                    f"first hit at roll {hit_roll}"
                )

        print()

    # Find the largest real roll number that was recorded.
    real_hits = [
        hit_roll
        for round_hits in round_results
        for hit_roll in round_hits
        if hit_roll is not None
    ]

    largest_real_cost = max(real_hits, default=0)

    # Missing hits must be represented by a finite cost for the
    # Hungarian algorithm. This value is guaranteed to be larger
    # than any valid complete result.
    impossible_cost = (
        largest_real_cost + 1
    ) * (target_count + 1)

    # Convert round-based results into:
    # cost_matrix[target][round]
    cost_matrix = [
        [
            (
                round_results[round_index][target_index]
                if round_results[round_index][target_index] is not None
                else impossible_cost
            )
            for round_index in range(round_count)
        ]
        for target_index in range(target_count)
    ]

    assignment = hungarian(cost_matrix)

    # Check whether the algorithm was forced to select a missing hit.
    impossible_assignment = any(
        round_results[round_index][target_index] is None
        for target_index, round_index in enumerate(assignment)
    )

    if impossible_assignment:
        print(
            "No complete assignment exists with the recorded hits.\n"
            "Increase the rolls per round, or enter 0 to continue "
            "until every target is hit."
        )
        return

    chosen_results = []

    for target_index, round_index in enumerate(assignment):
        chosen_results.append(
            (
                round_index,
                targets[target_index],
                round_results[round_index][target_index],
            )
        )

    # Display results in round order.
    chosen_results.sort()

    total_rolls = sum(
        hit_roll
        for _, _, hit_roll in chosen_results
    )

    print("Best combination:")

    for round_index, target, hit_roll in chosen_results:
        print(
            f"  Round {round_index + 1}: "
            f"target {target} at roll {hit_roll}"
        )

    print(f"\nLowest total: {total_rolls} rolls")


if __name__ == "__main__":
    main()