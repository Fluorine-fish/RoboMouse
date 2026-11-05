cmake_minimum_required(VERSION 3.8)
project(task2_motion_control)

find_package(ament_cmake REQUIRED)
install(PROGRAMS
  scripts/open_loop_demo.py
  scripts/waypoint_controller.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
