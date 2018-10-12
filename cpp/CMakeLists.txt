cmake_minimum_required(VERSION 3.9)

project(wsSimpleClient)

# for json support
# see https://github.com/nlohmann/json
find_package(nlohmann_json REQUIRED)

# we also use beast which is part of boost
set(Boost_USE_STATIC_LIBS        ON)
find_package(Boost 1.69 REQUIRED COMPONENTS date_time)
include_directories(${Boost_INCLUDE_DIRS})

# Request C++11 standard, using new CMake variables.
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS False)

add_library(wsSimpleClient wsSimpleClient.cxx)
target_link_libraries(wsSimpleClient PRIVATE nlohmann_json::nlohmann_json)
add_executable(wstest wstest.cxx)
target_link_libraries(wstest PRIVATE nlohmann_json::nlohmann_json)
