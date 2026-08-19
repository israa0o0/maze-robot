import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from robot_movement.action import Movement


class MazeSolver (Node):
    def __init__(self):
        super().__init__("maze_solver")

        self.move_x_client = ActionClient(
            self,
            Movement,
            'movement_x'
        )

    def move_x(self, distance):
        self.get_logger().info(f'sending x goal: {distance}')
        self.move_x_client.wait_for_server()
        goal = Movement.Goal()
        goal.forward_distance = distance
        self.get_logger().info('sending goal...')
        send_goal_future = self.move_x_client.send_goal_async(
            goal,
            feedback_callback = self.feedback_callback
        )
        send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def feedback_callback(self, feedback):
        fdb_msg = feedback.feedback
        self.get_logger().info(f"feedback: {fdb_msg}")

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return

        self.get_logger().info('Goal accepted!')

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.result_callback
        )

    def result_callback (self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info(
                f'Success: {result.message}'
            )
        else:
            self.get_logger().error(
                f'Failed: {result.message}'
            )


def main(args=None):
    rclpy.init(args=args)

    node = MazeSolver()

    # Test: move forward 1 meter
    node.move_x(1.0)

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()