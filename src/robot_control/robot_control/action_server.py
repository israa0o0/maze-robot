import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from robot_movement.action import Movement

class MovementXActionServer(Node):
    def __init__(self):
        super().__init__('movement_x_action_server')
        self._action_server = ActionServer(
            self,
            Movement,
            'movement_x',
            self.execute_callback)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)
        self.current_x = 0.0
        self.current_y = 0.0
        self.odom_received = False

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.odom_received = True

    def execute_callback(self, goal_handle):
        while not self.odom_received:
            rclpy.spin_once(self, timeout_sec=0.1)

        start_x = self.current_x
        start_y = self.current_y
        target_distance = goal_handle.request.forward_distance

        twist_msg = Twist()
        twist_msg.linear.x = 0.2

        feedback_msg = Movement.Feedback()
        distance_traveled = 0.0

        while distance_traveled < target_distance:
            self.publisher_.publish(twist_msg)
            rclpy.spin_once(self, timeout_sec=0.1)
            
            distance_traveled = math.sqrt(
                (self.current_x - start_x)**2 + (self.current_y - start_y)**2
            )
            
            feedback_msg.current_action = "Moving forward"
            feedback_msg.progress = distance_traveled
            goal_handle.publish_feedback(feedback_msg)

        twist_msg.linear.x = 0.0
        self.publisher_.publish(twist_msg)

        goal_handle.succeed()
        result = Movement.Result()
        result.success = True
        result.message = "Reached target distance"
        return result

def main(args=None):
    rclpy.init(args=args)
    action_server = MovementXActionServer()
    rclpy.spin(action_server)
    action_server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()