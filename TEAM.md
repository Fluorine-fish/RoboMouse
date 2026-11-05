# 两人协作预设

## 组员A：模型与场景

负责：

- `task1_robot_description/urdf/robot.urdf.xacro`
- `task1_robot_description/urdf/parts/`
- `task1_robot_description/world/maze.sdf`
- `task1_robot_description/world/maze_layout.txt`
- `task1_robot_description/scripts/generate_maze_world.py`
- `task2_motion_control/`：开环直线/转向、里程计 P 控制与航点序列
- 机器人尺寸、惯性参数、LiDAR 安装和迷宫墙体碰撞检查

验收时应能说明 `link/joint/visual/collision/inertial`、轮距、轮半径、墙体位姿、
差速运动学、P 控制公式及航点切换逻辑。

## 组员B：启动与数据链路

负责：

- `task1_bringup/launch/simulation.launch.py`
- `task1_bringup/config/bridge.yaml`
- `task1_bringup/config/task1.rviz`
- `task1_bringup/scripts/odom_tf.py`
- `task1_bringup/scripts/health_check.py`
- `task3_lidar_perception/`：雷达分区、反应式避障
- `task4_maze_control/`：左墙跟随状态机

验收时应能说明 launch 节点关系、ROS-Gazebo 话题映射、`/odom` 与 `/scan`
的数据来源、雷达扇区算法和左手法则路线。

## 接口约定

组员A保证机器人模型名固定为 `task1_robot`，并发布 Gazebo 话题
`/model/task1_robot/cmd_vel`、`/wheel_odom`、`/odom` 和 `/scan`。
组员B负责桥接 `/cmd_vel`、`/odom`、`/scan`，并发布 `odom -> base_footprint`
变换和雷达分区话题。
