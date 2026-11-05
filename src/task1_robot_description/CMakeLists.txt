cmake_minimum_required(VERSION 3.8)
project(task1_robot_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf world DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/generate_maze_world.py DESTINATION lib/${PROJECT_NAME})

ament_package()
