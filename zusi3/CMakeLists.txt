cmake_minimum_required (VERSION 2.6)

project (deadlock_check)

set (CMAKE_CXX_STANDARD 17)
set (CMAKE_CXX_STANDARD_REQUIRED ON)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -Werror")

add_executable(deadlock_check_test test.cpp)
