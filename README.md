# 机器人感知与控制综合实践：80 分必做部分

本工作区覆盖任务书中的全部基础必做项：

1. 环境与模型搭建
2. 差速运动控制
3. 激光雷达分区与反应式避障
4. 迷宫左墙跟随

## 环境

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic

任务书原文为 ROS 2 Humble + Gazebo Classic；本机实际环境为 Jazzy + Gazebo Harmonic。

## 编译与启动

```bash
cd ~/maze_task1_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
ros2 launch task1_bringup simulation.launch.py
```

默认 `mode:=wall_follow`，启动后机器人会自动从入口内侧走迷宫并从底部出口驶出。

无界面运行：

```bash
ros2 launch task1_bringup simulation.launch.py gz_gui:=false rviz:=false
```

## 功能模块

| 功能包 | 内容 |
| --- | --- |
| `task1_robot_description` | 分文件 URDF/Xacro、惯性、LiDAR、二维迷宫 world |
| `task2_motion_control` | 开环直行/原地转向、里程计 P 控制、航点序列 |
| `task3_lidar_perception` | `/scan` 前/左/右/后分区、反应式避障 |
| `task4_maze_control` | 左手法则路线生成及里程计航点执行 |
| `task1_bringup` | Gazebo、RViz2、桥接、TF 和总启动文件 |

## 模式切换

```bash
# 开环直行、停止、原地左转
ros2 launch task1_bringup simulation.launch.py mode:=open_loop

# 单点 P 控制
ros2 launch task1_bringup simulation.launch.py \
  mode:=point waypoints:="0.4,0.0"

# 多点航点序列
ros2 launch task1_bringup simulation.launch.py \
  mode:=waypoints waypoints:="0.4,0.0;0.8,0.0;1.0,0.2"

# 反应式避障
ros2 launch task1_bringup simulation.launch.py mode:=avoid

# 只启动仿真，不运行控制节点
ros2 launch task1_bringup simulation.launch.py mode:=idle
```

## 接口

- `/cmd_vel`：`geometry_msgs/msg/Twist`，从 ROS 2 发往 Gazebo。
- `/odom`：`nav_msgs/msg/Odometry`，由 Gazebo `OdometryPublisher` 发布的实时位姿里程计。
- `/wheel_odom`：Gazebo 内部轮式里程计话题，保留用于调试比较。
- `/scan`：`sensor_msgs/msg/LaserScan`，360 点、约 10 Hz。
- `/lidar_sectors`：`std_msgs/msg/Float32MultiArray`，依次为前、左、右、后距离。
- `/maze_status`：`std_msgs/msg/String`，左墙跟随状态。

## 迷宫与左墙跟随

迷宫来自现成二维生成器，原始布局为 13×9 格：

- 源文件：`task1_robot_description/world/maze_layout.txt`
- 来源及固定版本：`task1_robot_description/world/SOURCE.md`
- Gazebo 转换：`task1_robot_description/scripts/generate_maze_world.py`
- 左手法则路线：`task4_maze_control/scripts/build_left_wall_route.py`
- 运行路线：`task4_maze_control/config/maze_route.csv`

候选布局按“入口内侧朝南、左侧优先”策略筛选；选中的布局从入口到出口约需
29 个格步，比原布局更短，且以左转和直行为主。

每格边长为 0.6 m，内部通道净宽 0.6 m，入口和出口各宽 1.8 m。外墙除入口和
出口外均封闭。左手法则优先选择左侧通道，否则直行、右转或掉头；运行节点以
0.35 m/s 巡航，利用里程计逐段行驶，并使用雷达前方距离做急停保护。

## 已验证项目

- `colcon build`：5 个功能包全部构建成功。
- `check_urdf`：模型解析成功，根连杆为 `base_footprint`。
- `/scan`：360 点，约 10 Hz。
- `/odom`：约 20 Hz，包含 `odom -> base_footprint` 变换。
- 开环模式：完成直行和原地左转。
- P 控制/航点模式：依次到达全部输入航点并停车。
- 反应式避障：前方障碍进入阈值后转向绕开。
- 左墙模式：从入口内侧自动到达出口，最终 `/cmd_vel` 为零。

详细实测记录见 [VERIFICATION.md](VERIFICATION.md)。
