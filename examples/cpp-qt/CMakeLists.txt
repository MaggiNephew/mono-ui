cmake_minimum_required(VERSION 3.16)
project(mono_qt_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets)

# mono-ui root (this file lives in mono-ui/examples/cpp-qt)
get_filename_component(MONO_UI_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

add_executable(mono_qt_demo main.cpp)
target_include_directories(mono_qt_demo PRIVATE "${MONO_UI_ROOT}/dist/qt/cpp")
target_compile_definitions(mono_qt_demo PRIVATE MONO_UI_FONTS_DIR="${MONO_UI_ROOT}/fonts/ttf")
target_link_libraries(mono_qt_demo PRIVATE Qt6::Widgets)
