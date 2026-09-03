# Code for finding perks in noita wand seed. Specific perks. Can pick 4 perks for starters. The program will reroll the first 3 perk options until one of the 4 is hit
# Once a perk is hit, it will drop down to the next 4 perks and roll until the second perk is hit. 
# Challenge: Mathetmatically speaking how do we determine the lowest amount of rolls? If a perk is hit after 50 rolls on the first round
# and that same perk appears on the 2nd roll on the second round, should we then ignore the 50th roll of the first round and keep rolling
# until we hit the second perk, on the first round? Should we decide to go back in previous attempts after all rolls are done, or do we go back
# each time we hit a better roll? There is math behind this, but also computing logic.

import random

minimum = int(input("Min value: "))
maximum = int(input("Max value: "))
target = int(input("Target number: "))

if minimum > maximum: 
    raise ValueError("Min is higher than max")
if not minimum <= target <= maximum: 
    raise ValueError("Target not within range")

target_rolls = []

for roll in range(1,101):
    numbers = [random.randint(minimum, maximum) for _ in range(3)]

    if target in numbers:
        target_rolls.append(roll)

if target_rolls:
    rolls_text = ", ".join(map(str, target_rolls))
    print(f"Target found at roll {rolls_text}")
else:
    print("Target was not found in 100 rolls.") # testing addition