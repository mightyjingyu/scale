import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import time

class CrosswalkDetectorNode(Node):
    def __init__(self):
        super().__init__('crosswalk_detector_node')

        self.subscriber = self.create_subscription(
            Bool,
            '/camera/trigger_crosswalk',
            self.trigger_callback,
            10
        )

        self.publisher = self.create_publisher(Bool, '/crosswalk/stop_signal', 10)
        self.timer_running = False
        self.get_logger().info("CrosswalkDetectorNode is ready.")

    def trigger_callback(self, msg):
        if msg.data and not self.timer_running:
            self.get_logger().info('Trigger received: stopping vehicle for 5 seconds.')
            self.publish_stop_signal(True)
            self.timer_running = True
            self.create_timer(5.0, self.end_stop_signal)

    def publish_stop_signal(self, state: bool):
        msg = Bool()
        msg.data = state
        self.publisher.publish(msg)

    def end_stop_signal(self):
        self.publish_stop_signal(False)
        self.get_logger().info('Stop complete: resuming movement.')
        self.timer_running = False

def main(args=None):
    rclpy.init(args=args)
    node = CrosswalkDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
