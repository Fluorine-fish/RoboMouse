#!/usr/bin/env python3
import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray


class SectorScan(Node):
    def __init__(self):
        super().__init__("sector_scan")
        self.front_half = math.radians(
            self.declare_parameter("front_half_angle_deg", 20.0).value
        )
        self.side_inner = math.radians(
            self.declare_parameter("side_inner_angle_deg", 65.0).value
        )
        self.side_outer = math.radians(
            self.declare_parameter("side_outer_angle_deg", 115.0).value
        )
        self.publisher = self.create_publisher(Float32MultiArray, "/lidar_sectors", 10)
        self.create_subscription(LaserScan, "/scan", self.on_scan, 10)

    @staticmethod
    def distance(msg, low, high):
        distances = []
        for index, distance in enumerate(msg.ranges):
            angle = msg.angle_min + index * msg.angle_increment
            if low <= angle <= high and math.isfinite(distance) and distance >= msg.range_min:
                distances.append(distance)
        if not distances:
            return msg.range_max
        distances.sort()
        return distances[len(distances) // 2]

    def on_scan(self, msg):
        # 输出顺序：前、左、右、后。
        front = self.distance(msg, -self.front_half, self.front_half)
        left = self.distance(msg, self.side_inner, self.side_outer)
        right = self.distance(msg, -self.side_outer, -self.side_inner)
        rear = self.distance(msg, math.radians(160), math.pi)
        rear = min(rear, self.distance(msg, -math.pi, math.radians(-160)))
        output = Float32MultiArray()
        output.data = [front, left, right, rear]
        self.publisher.publish(output)


def main():
    rclpy.init()
    node = SectorScan()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
