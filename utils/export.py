"""Export generated sequences to TXT or CSV."""

import csv
from pathlib import Path
from typing import Sequence


def export_sequence(path: str | Path, generator: str, parameters: str,
                    values: Sequence[int], states: Sequence[int] | None = None,
                    modulus: int | None = None) -> None:
    destination = Path(path)
    suffix = destination.suffix.lower()
    if suffix == ".csv":
        with destination.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.writer(stream)
            if generator == "BBS":
                writer.writerow(["index", "bit", "state"])
                for index, (value, state) in enumerate(zip(values, states or ()), 1):
                    writer.writerow([index, value, state])
            elif modulus is not None:
                writer.writerow(["index", "state", "normalized"])
                for index, value in enumerate(values, 1):
                    writer.writerow([index, value, value / modulus])
            else:
                writer.writerow(["index", "state"])
                for index, value in enumerate(values, 1):
                    writer.writerow([index, value])
        return

    with destination.open("w", encoding="utf-8") as stream:
        stream.write("Random Number Generator Laboratory\n")
        stream.write(f"Generator: {generator}\nParameters: {parameters}\n\n")
        if generator == "BBS":
            stream.write("Index\tBit\tState\n")
            stream.writelines(f"{i}\t{value}\t{state}\n" for i, (value, state) in enumerate(zip(values, states or ()), 1))
        elif modulus is not None:
            stream.write("Index\tX_n\tNormalized\n")
            stream.writelines(f"{i}\t{value}\t{value / modulus:.12g}\n" for i, value in enumerate(values, 1))
        else:
            stream.write("Index\tX_n\n")
            stream.writelines(f"{i}\t{value}\n" for i, value in enumerate(values, 1))
