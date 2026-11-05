#!/usr/bin/env python3
import argparse
from pathlib import Path


CELL = 0.6
DIRS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows = [list(row) for row in args.layout.read_text(encoding="utf-8").splitlines()]
    for col in range(4, 7):
        rows[0][col] = " "
    for col in range(9, 12):
        rows[-1][col] = " "

    row, col, heading = 1, 5, 2
    cells = [(row, col)]
    seen = set()
    for _ in range(1000):
        if row == len(rows) - 1:
            cells.append((row + 1, col))
            break
        state = (row, col, heading)
        if state in seen:
            raise RuntimeError("left-wall route entered a loop")
        seen.add(state)
        for new_heading in ((heading - 1) % 4, heading, (heading + 1) % 4,
                            (heading + 2) % 4):
            dr, dc = DIRS[new_heading]
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(rows) and 0 <= nc < len(rows[0]) and rows[nr][nc] == " ":
                row, col, heading = nr, nc, new_heading
                cells.append((row, col))
                break
        else:
            raise RuntimeError("left-wall route reached a dead end")
    else:
        raise RuntimeError("left-wall route did not exit")

    points = [
        ((r - 1) * CELL, (c - 5) * CELL)
        for r, c in cells
    ]
    compact = [points[0]]
    previous_direction = None
    for previous, point in zip(points, points[1:]):
        direction = (
            round(point[0] - previous[0], 3),
            round(point[1] - previous[1], 3),
        )
        if previous_direction is not None and direction != previous_direction:
            compact.append(previous)
        previous_direction = direction
    compact.append(points[-1])

    # 连续同向格点合并为折线端点。
    args.output.write_text(
        ";".join(f"{x:.3f},{y:.3f}" for x, y in compact) + "\n",
        encoding="utf-8",
    )
    print(f"route cells={len(points)}, waypoints={len(compact)}, output={args.output}")


if __name__ == "__main__":
    main()
