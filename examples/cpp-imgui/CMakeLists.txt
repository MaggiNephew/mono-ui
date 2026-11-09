cmake_minimum_required(VERSION 3.16)
project(mono_imgui_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Point IMGUI_DIR at a Dear ImGui checkout:  cmake -B build -DIMGUI_DIR=~/src/imgui
set(IMGUI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/imgui" CACHE PATH "Dear ImGui source directory")
if(NOT EXISTS "${IMGUI_DIR}/imgui.h")
  message(FATAL_ERROR "Dear ImGui not found at ${IMGUI_DIR}. git clone https://github.com/ocornut/imgui and pass -DIMGUI_DIR=...")
endif()

get_filename_component(MONO_UI_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

find_package(OpenGL REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLFW REQUIRED IMPORTED_TARGET glfw3)

add_executable(mono_imgui_demo
  main.cpp
  ${IMGUI_DIR}/imgui.cpp ${IMGUI_DIR}/imgui_draw.cpp ${IMGUI_DIR}/imgui_tables.cpp ${IMGUI_DIR}/imgui_widgets.cpp
  ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp)
target_include_directories(mono_imgui_demo PRIVATE ${IMGUI_DIR} ${IMGUI_DIR}/backends "${MONO_UI_ROOT}/dist/imgui")
target_compile_definitions(mono_imgui_demo PRIVATE MONO_UI_FONTS_DIR="${MONO_UI_ROOT}/fonts/ttf")
target_link_libraries(mono_imgui_demo PRIVATE PkgConfig::GLFW OpenGL::GL)
