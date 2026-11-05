#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class OpenLoopDemo(Node):
    def __init__(self):
        super().__init__("open_loop_demo")
        self.speed = self.declare_parameter("linear_speed", 0.18).value
        self.turn = self.declare_parameter("angular_speed", 0.8).value
        self.straight_time = self.declare_parameter("straight_seconds", 1.2).value
        self.turn_time = self.declare_parameter("turn_seconds", 1.8).value
        self.phase = -1
        self.last_phase = -1
        self.phase_start = None
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(0.1, self.update)

    def update(self):
        if self.phase_start is None:
            self.phase_start = self.get_clock().now()
        elapsed = (self.get_clock().now() - self.phase_start).nanoseconds / 1e9
        phases = (
            ("前进", self.straight_time, self.speed, 0.0),
            ("停止", 0.5, 0.0, 0.0),
            ("原地左转", self.turn_time, 0.0, self.turn),
            ("停止", 0.5, 0.0, 0.0),
            ("再次前进", self.straight_time, self.speed, 0.0),
            ("完成", 1e9, 0.0, 0.0),
        )
        if self.phase < 0:
            self.phase = 0
        elif elapsed > phases[self.phase][1]:
            self.phase = min(self.phase + 1, len(phases) - 1)
            self.phase_start = self.get_clock().now()
            elapsed = 0.0
        name, _, linear, angular = phases[self.phase]
        if self.phase < 4 and self.phase != self.last_phase:
            self.get_logger().info(f"开环阶段：{name}")
            self.last_phase = self.phase
        message = Twist()
        message.linear.x = float(linear)
        message.angular.z = float(angular)
        self.publisher.publish(message)


def main():
    rclpy.init()
    node = OpenLoopDemo()
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
