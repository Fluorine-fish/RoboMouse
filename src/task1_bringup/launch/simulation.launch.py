from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    EqualsSubstitution,
    FindExecutable,
    LaunchConfiguration,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    desc_dir = get_package_share_directory("task1_robot_description")
    bringup_dir = get_package_share_directory("task1_bringup")
    gz_dir = get_package_share_directory("ros_gz_sim")
    xacro_file = os.path.join(desc_dir, "urdf", "robot.urdf.xacro")
    world_file = os.path.join(desc_dir, "world", "maze.sdf")

    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", xacro_file]), value_type=str
    )
    rviz = LaunchConfiguration("rviz")
    gz_gui = LaunchConfiguration("gz_gui")
    mode = LaunchConfiguration("mode")

    gz_launch = PythonLaunchDescriptionSource(
        os.path.join(gz_dir, "launch", "gz_sim.launch.py")
    )
    gz_gui_node = IncludeLaunchDescription(
        gz_launch,
        launch_arguments={"gz_args": f"-r {world_file}"}.items(),
        condition=IfCondition(gz_gui),
    )
    gz_headless_node = IncludeLaunchDescription(
        gz_launch,
        launch_arguments={"gz_args": f"-r -s {world_file}"}.items(),
        condition=UnlessCondition(gz_gui),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("rviz", default_value="true"),
            DeclareLaunchArgument("gz_gui", default_value="true"),
            DeclareLaunchArgument("mode", default_value="wall_follow"),
            DeclareLaunchArgument("waypoints", default_value="0.35,0.0"),
            gz_gui_node,
            gz_headless_node,
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description, "use_sim_time": True}],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                parameters=[
                    {
                        "config_file": os.path.join(bringup_dir, "config", "bridge.yaml"),
                        "use_sim_time": True,
                    }
                ],
                output="screen",
            ),
            Node(
                package="task1_bringup",
                executable="odom_tf.py",
                parameters=[{"use_sim_time": True}],
                output="screen",
            ),
            TimerAction(
                period=2.0,
                actions=[
                    Node(
                        package="ros_gz_sim",
                        executable="create",
                        arguments=[
                            "-world", "maze_world",
                            "-name", "task1_robot",
                            "-topic", "robot_description",
                            "-x", "-0.6",
                            "-y", "1.8",
                            "-z", "0.01",
                            "-Y", "-1.5708",
                        ],
                        output="screen",
                    )
                ],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", os.path.join(bringup_dir, "config", "task1.rviz")],
                parameters=[{"use_sim_time": True}],
                condition=IfCondition(rviz),
                output="screen",
            ),
            TimerAction(
                period=5.0,
                actions=[
                    Node(
                        package="task3_lidar_perception",
                        executable="sector_scan.py",
                        parameters=[{"use_sim_time": True}],
                        output="screen",
                    ),
                    Node(
                        package="task1_bringup",
                        executable="health_check.py",
                        parameters=[{"use_sim_time": True}],
                        output="screen",
                    )
                ],
            ),
            TimerAction(
                period=5.5,
                actions=[
                    Node(
                        package="task2_motion_control",
                        executable="open_loop_demo.py",
                        parameters=[{"use_sim_time": True}],
                        condition=IfCondition(EqualsSubstitution(mode, "open_loop")),
                        output="screen",
                    ),
                    Node(
                        package="task2_motion_control",
                        executable="waypoint_controller.py",
                        parameters=[
                            {
                                "use_sim_time": True,
                                "waypoints": LaunchConfiguration("waypoints"),
                            }
                        ],
                        condition=IfCondition(
                            PythonExpression(
                                ["'", mode, "' in ['point', 'waypoints']"]
                            )
                        ),
                        output="screen",
                    ),
                    Node(
                        package="task3_lidar_perception",
                        executable="reactive_avoidance.py",
                        parameters=[{"use_sim_time": True}],
                        condition=IfCondition(EqualsSubstitution(mode, "avoid")),
                        output="screen",
                    ),
                    Node(
                        package="task4_maze_control",
                        executable="left_wall_follower.py",
                        parameters=[{"use_sim_time": True}],
                        condition=IfCondition(EqualsSubstitution(mode, "wall_follow")),
                        output="screen",
                    ),
                ],
            ),
        ]
    )
