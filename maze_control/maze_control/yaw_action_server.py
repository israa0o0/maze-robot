#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from maze_control.action import RotateRobotYaw


class YawActionServer(Node):

    def __init__(self):
        super().__init__('yaw_action_server')

        self.callback_group = ReentrantCallbackGroup()

        # Action Server
        self._action_server = ActionServer(
            self,
            RotateRobotYaw,
            'rotate_robot_yaw',
            self.execute_callback,
            callback_group=self.callback_group
        )
        # Publisher for robot velocity
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Subscriber for odometry
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10,
            callback_group=self.callback_group
        )

        # Current yaw angle
        self.current_yaw = 0.0

        self.get_logger().info('Yaw Action Server is ready!')

    def odom_callback(self, msg):
        
        #Read the robot orientation from /odom and convert quaternion to yaw angle.
        

        q = msg.pose.pose.orientation

        sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
        cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.current_yaw = math.atan2(sin_yaw, cos_yaw)

    def normalize_angle(self, angle):
        
        #Keep angle between -pi and pi.
        

        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle

    def execute_callback(self, goal_handle):
        
        #Execute the requested yaw rotation.
        

        target_angle = goal_handle.request.angle

        self.get_logger().info(
            f'Received yaw goal: {target_angle:.2f} rad'
        )

        # Starting yaw
        start_yaw = self.current_yaw

        # Target yaw
        target_yaw = self.normalize_angle(
            start_yaw + target_angle
        )

        feedback_msg = RotateRobotYaw.Feedback()

        twist = Twist()

        # Rotation speed
        angular_speed = 0.5

        # Tolerance
        tolerance = 0.03

        # Timer to allow odometry callbacks to update
        rate = self.create_rate(20)

        while rclpy.ok():

            # Calculate error
            error = self.normalize_angle(
                target_yaw - self.current_yaw
            )

            # Check if target reached
            if abs(error) < tolerance:
                break

            # Rotate in correct direction
            twist.linear.x = 0.0

            if error > 0:
                twist.angular.z = angular_speed
            else:
                twist.angular.z = -angular_speed

            self.cmd_vel_publisher.publish(twist)

            # Send feedback
            feedback_msg.current_angle = self.current_yaw
            goal_handle.publish_feedback(feedback_msg)

            # Small delay
            rate.sleep()

        # Stop robot
        twist.linear.x = 0.0
        twist.angular.z = 0.0

        self.cmd_vel_publisher.publish(twist)

        # Finish action
        goal_handle.succeed()

        result = RotateRobotYaw.Result()

        result.final_angle = self.current_yaw
        result.success = True

        self.get_logger().info(
            f'Rotation completed. Final yaw: '
            f'{self.current_yaw:.2f} rad'
        )

        return result


def main(args=None):

    rclpy.init(args=args)

    node = YawActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()