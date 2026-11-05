#!/usr/bin/env python3
import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class HealthCheck(Node):
    def __init__(self):
        super().__init__("task1_health_check")
        self.odom_ok = False
        self.scan_ok = False
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_subscription(LaserScan, "/scan", self.on_scan, qos_profile_sensor_data)

    def on_odom(self, msg):
        if not self.odom_ok:
            self.get_logger().info(f"/odom 已就绪，frame={msg.header.frame_id}")
            self.odom_ok = True
            self.report()

    def on_scan(self, msg):
        if not self.scan_ok:
            self.get_logger().info(f"/scan 已就绪，点数={len(msg.ranges)}")
            self.scan_ok = True
            self.report()

    def report(self):
        if self.odom_ok and self.scan_ok:
            self.get_logger().info("任务1传感器接口检查通过")


def main():
    rclpy.init()
    node = HealthCheck()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException, RuntimeError):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
