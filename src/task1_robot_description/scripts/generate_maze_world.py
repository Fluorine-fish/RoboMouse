#!/usr/bin/env python3
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "world" / "maze_layout.txt"
OUTPUT = ROOT / "world" / "maze.sdf"
CELL = 0.6
WALL_HEIGHT = 0.24


def runs(row):
    start = None
    for col, char in enumerate(row + " "):
        if char == "█" and start is None:
            start = col
        elif char != "█" and start is not None:
            yield start, col - 1
            start = None


def main():
    rows = SOURCE.read_text(encoding="utf-8").splitlines()
    height, width = len(rows), len(rows[0])
    assert all(len(row) == width for row in rows)
    assert [i for i, ch in enumerate(rows[0]) if ch != "█"] == [5]
    assert [i for i, ch in enumerate(rows[-1]) if ch != "█"] == [11]
    rows[0] = "".join(" " if 4 <= i <= 6 else ch for i, ch in enumerate(rows[0]))
    rows[-1] = "".join(" " if 9 <= i <= 11 else ch for i, ch in enumerate(rows[-1]))
    assert [i for i, ch in enumerate(rows[0]) if ch != "█"] == [4, 5, 6]
    assert [i for i, ch in enumerate(rows[-1]) if ch != "█"] == [9, 10, 11]
    assert rows[0][0] == rows[0][-1] == "█"
    assert rows[0][-1] == "█"
    assert rows[-1][0] == rows[-1][-1] == "█"
    assert all(row[0] == row[-1] == "█" for row in rows[1:-1])
    queue, seen = deque([(5, 0)]), {(5, 0)}
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (col + dc, row + dr)
            if (0 <= nxt[0] < width and 0 <= nxt[1] < height
                    and rows[nxt[1]][nxt[0]] != "█" and nxt not in seen):
                seen.add(nxt)
                queue.append(nxt)
    assert (11, height - 1) in seen

    walls = []
    for row_idx, row in enumerate(rows):
        y = ((height - 1) / 2 - row_idx) * CELL
        for run_idx, (first, last) in enumerate(runs(row)):
            center_col = (first + last) / 2
            x = (center_col - (width - 1) / 2) * CELL
            size_x = (last - first + 1) * CELL
            name = f"wall_{row_idx:02d}_{run_idx:02d}"
            walls.append(
                f"""        <visual name="{name}_v">
          <pose>{x:.3f} {y:.3f} 0 0 0 0</pose>
          <geometry><box><size>{size_x:.3f} {CELL:.3f} {WALL_HEIGHT}</size></box></geometry>
          <material><ambient>0.08 0.12 0.18 1</ambient><diffuse>0.08 0.12 0.18 1</diffuse></material>
        </visual>
        <collision name="{name}_c">
          <pose>{x:.3f} {y:.3f} 0 0 0 0</pose>
          <geometry><box><size>{size_x:.3f} {CELL:.3f} {WALL_HEIGHT}</size></box></geometry>
        </collision>"""
            )

    entry_x = (5 - (width - 1) / 2) * CELL
    exit_x = (10 - (width - 1) / 2) * CELL
    top_y, bottom_y = height / 2 * CELL, -height / 2 * CELL
    sdf = f"""<?xml version="1.0"?>
<sdf version="1.9">
  <world name="maze_world">
    <gravity>0 0 -9.8</gravity>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 8 0 0 0</pose>
      <diffuse>0.9 0.9 0.9 1</diffuse>
      <direction>-0.4 0.2 -0.9</direction>
    </light>

    <model name="ground">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>32 20</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>32 20</size></plane></geometry>
          <material><ambient>0.86 0.87 0.89 1</ambient><diffuse>0.86 0.87 0.89 1</diffuse></material>
        </visual>
      </link>
    </model>

    <!-- 由 maze_layout.txt 生成的 2D 迷宫。 -->
    <model name="maze_walls">
      <static>true</static>
      <pose>0 0 {WALL_HEIGHT / 2} 0 0 0</pose>
      <link name="walls">
{chr(10).join(walls)}
      </link>
    </model>

    <model name="entrance_marker">
      <static>true</static>
      <pose>{entry_x:.3f} {top_y:.3f} 0.003 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>{CELL * 0.8:.3f} {CELL * 0.8:.3f} 0.004</size></box></geometry>
          <material><ambient>0.1 0.75 0.2 1</ambient><diffuse>0.1 0.75 0.2 1</diffuse></material>
        </visual>
      </link>
    </model>
    <model name="exit_marker">
      <static>true</static>
      <pose>{exit_x:.3f} {bottom_y:.3f} 0.003 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>{CELL * 0.8:.3f} {CELL * 0.8:.3f} 0.004</size></box></geometry>
          <material><ambient>0.85 0.1 0.1 1</ambient><diffuse>0.85 0.1 0.1 1</diffuse></material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
"""
    OUTPUT.write_text(sdf, encoding="utf-8")
    print(f"{OUTPUT}: {width}x{height}, cell={CELL}, walls={len(walls)}")
    print(f"entry=({entry_x:.3f}, {top_y:.3f}), exit=({exit_x:.3f}, {bottom_y:.3f})")
    print(f"opening width={3 * CELL:.1f} m")


if __name__ == "__main__":
    main()
