🤖 ROS2 Maze Navigation

A ROS2 project for controlling a TurtleBot3 to navigate a grid-based maze autonomously using Gazebo Sim.

🎯 Goal

The goal of this project is to make the robot:

- Move forward and backward.
- Rotate to different directions.
- Control the movable walls.
- Use "/odom" to track its movement.
- Navigate through the maze automatically.
- Reach the final goal.

🛠️ Technologies

- ROS2
- Gazebo Sim Harmonic
- TurtleBot3
- Python
- Git & GitHub

📂 Project Structure

maze_navigation/
├── action/
├── maze_navigation/
├── package.xml
├── setup.py
└── README.md

🚀 Getting Started

1. Create the workspace

mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

2. Clone the maze

git clone <maze-repository-url>

3. Build the workspace

cd ~/ros2_ws
colcon build
source install/setup.bash

4. Run Gazebo

ros2 launch maze_control maze_simulation_tb3.launch.py

🤖 Main Components

Movement X

"move_robot_x" is responsible for moving the robot forward or backward.

It uses:

- "/cmd_vel" → sends movement commands.
- "/odom" → gets the robot's position.

Movement Yaw

"move_robot_yaw" is responsible for rotating the robot.

It uses "/cmd_vel" and "/odom" to control and measure the rotation.

Wall Service

The maze contains movable red walls.

A ROS2 Service is used to control these walls.

To find the available services:

ros2 service list

Maze Solver

The main controller contains:

solve_maze()

It combines the movement Actions and wall Service to navigate the robot through the maze.

🔗 ROS2 Communication

             Maze Solver
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
   Move X      Move Yaw   Wall Service
        │         │
        └────┬────┘
             ↓
          /cmd_vel
             ↓
         TurtleBot3
             │
             ↓
           /odom
             │
             └──────→ Feedback

⚠️ Error Handling

The project should handle situations such as:

- Missing "/odom"
- Movement timeout
- Robot not responding

When an error occurs, the robot should stop safely.

👥 Team

This project is developed as a team using GitHub.

Each member works on their own branch and creates a Pull Request before merging their work into "main".

🏁 Final Result

The final system should allow the TurtleBot3 to navigate the maze autonomously and reach the goal using ROS2 Actions, Services, and Topics.
