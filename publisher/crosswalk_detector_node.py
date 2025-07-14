import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

class CrosswalkDetectorNode(Node):
    def __init__(self):
        super().__init__('crosswalk_detector_node')

        self.subscriber = self.create_subscription(
            Bool,
            '/camera/trigger_crosswalk',
            self.trigger_callback,
            10,
        )

        # Publisher used to command the vehicle to stop when a crosswalk is
        # detected.
        self.stop_publisher = self.create_publisher(
            Bool,
            '/crosswalk/stop_signal',
            10
        )

        # Publisher that notifies the motor controller to start moving again
        # once the stop period has elapsed.
        self.start_publisher = self.create_publisher(
            Bool,
            '/motor_controller/start_signal',
            10,
        )
        self.timer_running = False
        self.stop_timer = None
        self.get_logger().info("CrosswalkDetectorNode is ready.")

    def trigger_callback(self, msg):
        if msg.data and not self.timer_running:
            self.get_logger().info('Trigger received: stopping vehicle for 5 seconds.')
            self.publish_stop_signal(True)
            self.timer_running = True
            self.stop_timer = self.create_timer(5.0, self.end_stop_signal)

    def publish_stop_signal(self, state: bool):
        msg = Bool()
        msg.data = state
        self.stop_publisher.publish(msg)

    def end_stop_signal(self):
        self.publish_stop_signal(False)
        # Stop the timer so it does not repeatedly fire.
        if self.stop_timer is not None:
            self.stop_timer.cancel()
            self.stop_timer = None
        # Notify the motor controller that it can resume movement.
        start_msg = Bool()
        start_msg.data = True
        self.start_publisher.publish(start_msg)
        self.get_logger().info('Stop complete: resuming movement.')
        self.timer_running = False

def main(args=None):
    rclpy.init(args=args)
    node = CrosswalkDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
