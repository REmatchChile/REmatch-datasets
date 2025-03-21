cmake_minimum_required(VERSION 3.16)
project(hello-rematch)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(REmatch REQUIRED)

set(CMAKE_CXX_FLAGS "-O3 -g0")

set(
    TESTS
    test-performance
    test-performance-stream
)

foreach(test ${TESTS})
    add_executable(${test} cpp/${test}.cpp)
    target_link_libraries(${test} REmatch::REmatch)
endforeach()
