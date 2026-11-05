#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class OdomTf(Node):
    def __init__(self):
        super().__init__("odom_tf")
        self.tf = TransformBroadcaster(self)
        self.create_subscription(Odometry, "/odom", self.publish_tf, 10)

    def publish_tf(self, msg):
        # 将 Gazebo 里程计位姿转换为 ROS 2 TF。
        out = TransformStamped()
        out.header.stamp = msg.header.stamp
        out.header.frame_id = "odom"
        out.child_frame_id = "base_footprint"
        out.transform.translation.x = msg.pose.pose.position.x
        out.transform.translation.y = msg.pose.pose.position.y
        out.transform.translation.z = msg.pose.pose.position.z
        out.transform.rotation = msg.pose.pose.orientation
        self.tf.sendTransform(out)


def main():
    rclpy.init()
    node = OdomTf()
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
