#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def clamp(value, low, high):
    return max(low, min(high, value))


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class WaypointController(Node):
    def __init__(self):
        super().__init__("waypoint_controller")
        raw = self.declare_parameter("waypoints", "0.35,0.0").value
        self.points = [
            tuple(float(v) for v in item.split(","))
            for item in raw.replace(";", " ").split()
        ]
        self.tolerance = self.declare_parameter("tolerance", 0.05).value
        self.kp_linear = self.declare_parameter("kp_linear", 0.8).value
        self.kp_angular = self.declare_parameter("kp_angular", 1.8).value
        self.max_linear = self.declare_parameter("max_linear", 0.24).value
        self.max_angular = self.declare_parameter("max_angular", 0.8).value
        self.pose = None
        self.yaw = 0.0
        self.origin = None
        self.index = 0
        self.done = False
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_timer(0.1, self.update)

    def on_odom(self, msg):
        pose = msg.pose.pose
        q = pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                         1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        if self.origin is None:
            self.origin = (pose.position.x, pose.position.y, yaw)
            self.pose = pose
            self.pose.position.x = 0.0
            self.pose.position.y = 0.0
            self.yaw = 0.0
            return
        origin_x, origin_y, origin_yaw = self.origin
        dx = pose.position.x - origin_x
        dy = pose.position.y - origin_y
        c, s = math.cos(origin_yaw), math.sin(origin_yaw)
        self.pose = pose
        self.pose.position.x = c * dx + s * dy
        self.pose.position.y = -s * dx + c * dy
        self.yaw = wrap(yaw - origin_yaw)

    def update(self):
        message = Twist()
        if self.pose is None or self.done:
            self.publisher.publish(message)
            return

        target_x, target_y = self.points[self.index]
        dx = target_x - self.pose.position.x
        dy = target_y - self.pose.position.y
        distance = math.hypot(dx, dy)
        if distance < self.tolerance:
            self.get_logger().info(f"到达航点 {self.index + 1}/{len(self.points)}")
            self.index += 1
            if self.index >= len(self.points):
                self.done = True
                self.get_logger().info("航点跟踪完成")
                self.publisher.publish(message)
                return
            target_x, target_y = self.points[self.index]
            dx, dy = target_x - self.pose.position.x, target_y - self.pose.position.y
            distance = math.hypot(dx, dy)

        error = wrap(math.atan2(dy, dx) - self.yaw)
        message.angular.z = clamp(self.kp_angular * error, -self.max_angular, self.max_angular)
        if abs(error) < 0.45:
            message.linear.x = clamp(self.kp_linear * distance, 0.0, self.max_linear)
        self.publisher.publish(message)


def main():
    rclpy.init()
    node = WaypointController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            node.publisher.publish(Twist())
        except Exception:
            pass
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
