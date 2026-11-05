#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class ReactiveAvoidance(Node):
    def __init__(self):
        super().__init__("reactive_avoidance")
        self.stop_distance = self.declare_parameter("stop_distance", 0.48).value
        self.speed = self.declare_parameter("forward_speed", 0.16).value
        self.turn_speed = self.declare_parameter("turn_speed", 0.65).value
        self.front, self.left, self.right = None, None, None
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Float32MultiArray, "/lidar_sectors", self.on_sectors, 10)
        self.create_timer(0.1, self.update)

    def on_sectors(self, msg):
        if len(msg.data) >= 3:
            self.front, self.left, self.right = msg.data[:3]

    def update(self):
        message = Twist()
        if self.front is not None:
            if self.front < self.stop_distance:
                message.angular.z = self.turn_speed if self.left >= self.right else -self.turn_speed
            else:
                message.linear.x = self.speed
        self.publisher.publish(message)


def main():
    rclpy.init()
    node = ReactiveAvoidance()
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
