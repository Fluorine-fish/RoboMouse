cmake_minimum_required(VERSION 3.8)
project(task3_lidar_perception)

find_package(ament_cmake REQUIRED)
install(PROGRAMS
  scripts/sector_scan.py
  scripts/reactive_avoidance.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
