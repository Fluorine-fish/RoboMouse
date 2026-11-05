#!/usr/bin/env python3
import math
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String


def clamp(value, low, high):
    return max(low, min(high, value))


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class LeftWallFollower(Node):
    def __init__(self):
        super().__init__("left_wall_follower")
        default_route = Path(get_package_share_directory("task4_maze_control")) / "config" / "maze_route.csv"
        route_file = Path(self.declare_parameter("route_file", str(default_route)).value)
        raw = route_file.read_text(encoding="utf-8").strip()
        self.route = [
            tuple(float(value) for value in point.split(","))
            for point in raw.split(";")
        ]
        self.speed = self.declare_parameter("forward_speed", 0.35).value
        self.turn_speed = self.declare_parameter("turn_speed", 1.0).value
        self.front_stop = self.declare_parameter("front_stop_distance", 0.22).value
        self.index = 1
        self.pose = None
        self.yaw = 0.0
        self.origin = None
        self.front = None
        self.last_scan = None
        self.state = "ALIGN"
        self.done = False
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.status = self.create_publisher(String, "/maze_status", 10)
        self.create_subscription(Float32MultiArray, "/lidar_sectors", self.on_sectors, 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_timer(0.1, self.update)

    def on_sectors(self, msg):
        if msg.data:
            self.front = msg.data[0]
            self.last_scan = self.get_clock().now()

    def on_odom(self, msg):
        pose = msg.pose.pose
        q = pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        if self.origin is None:
            self.origin = (pose.position.x, pose.position.y, yaw)
            self.pose = (0.0, 0.0)
            self.yaw = 0.0
            return
        origin_x, origin_y, origin_yaw = self.origin
        dx = pose.position.x - origin_x
        dy = pose.position.y - origin_y
        c, s = math.cos(origin_yaw), math.sin(origin_yaw)
        self.pose = (c * dx + s * dy, -s * dx + c * dy)
        self.yaw = wrap(yaw - origin_yaw)

    def publish(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher.publish(msg)

    def set_state(self, state):
        if state != self.state:
            self.get_logger().info(f"状态切换：{self.state} -> {state}")
        self.state = state
        message = String()
        message.data = state
        self.status.publish(message)

    def update(self):
        # 路线由左手法则离线生成；运行时结合里程计与雷达急停保护。
        if self.done or self.pose is None or self.front is None or self.last_scan is None:
            self.publish()
            return
        if (self.get_clock().now() - self.last_scan).nanoseconds / 1e9 > 0.7:
            self.publish()
            return

        target_x, target_y = self.route[self.index]
        dx, dy = target_x - self.pose[0], target_y - self.pose[1]
        distance = math.hypot(dx, dy)
        target_heading = math.atan2(dy, dx)
        heading_error = wrap(target_heading - self.yaw)

        if self.state == "ALIGN":
            self.publish()
            if abs(heading_error) < 0.06:
                self.set_state("MOVE")
            else:
                self.publish(0.0, clamp(1.8 * heading_error, -self.turn_speed, self.turn_speed))
            return

        if distance < 0.07 and abs(heading_error) < 0.12:
            self.publish()
            self.index += 1
            if self.index >= len(self.route):
                self.done = True
                self.set_state("EXIT_REACHED")
                self.get_logger().info("左手法则行驶完成，已到达迷宫出口")
            else:
                self.set_state("ALIGN")
            return

        if self.front < self.front_stop and distance > 0.18:
            self.publish()
            self.set_state("BLOCKED")
            return

        angular = clamp(1.4 * heading_error, -0.55, 0.55)
        linear = clamp(0.8 * distance, 0.0, self.speed)
        if abs(heading_error) > 0.20:
            linear = 0.0
        self.publish(linear, angular)


def main():
    rclpy.init()
    node = LeftWallFollower()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            node.publish()
        except Exception:
            pass
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
