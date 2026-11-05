cmake_minimum_required(VERSION 3.8)
project(task4_maze_control)

find_package(ament_cmake REQUIRED)
install(PROGRAMS
  scripts/left_wall_follower.py
  scripts/build_left_wall_route.py
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
ament_package()
