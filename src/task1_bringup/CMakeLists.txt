cmake_minimum_required(VERSION 3.8)
project(task1_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/odom_tf.py
  scripts/health_check.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
