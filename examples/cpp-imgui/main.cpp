// mono-ui Dear ImGui demo (GLFW + OpenGL 3).
//   ./mono_imgui_demo            round
//   ./mono_imgui_demo square
//   ./mono_imgui_demo round --shot out.ppm     render a few frames, save, exit
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "mono_imgui.h"

#include <GLFW/glfw3.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#ifndef MONO_UI_FONTS_DIR
#define MONO_UI_FONTS_DIR "../../fonts/ttf"
#endif

static void savePPM(const char* path, int w, int h) {
    std::vector<unsigned char> px((size_t)w * h * 3);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, px.data());
    FILE* f = std::fopen(path, "wb");
    if (!f) return;
    std::fprintf(f, "P6\n%d %d\n255\n", w, h);
    for (int y = h - 1; y >= 0; --y) std::fwrite(&px[(size_t)y * w * 3], 1, (size_t)w * 3, f);
    std::fclose(f);
}

int main(int argc, char** argv) {
    MonoUI::Variant variant = MonoUI::Round;
    const char* shot = nullptr;
    for (int i = 1; i < argc; ++i) {
        if (!std::strcmp(argv[i], "square")) variant = MonoUI::Square;
        if (!std::strcmp(argv[i], "blend")) variant = MonoUI::Blend;
        if (!std::strcmp(argv[i], "paper")) variant = MonoUI::Paper;
        if (!std::strcmp(argv[i], "--shot") && i + 1 < argc) shot = argv[++i];
    }
    if (!glfwInit()) return 1;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    GLFWwindow* window = glfwCreateWindow(980, 640, "mono-ui · Dear ImGui", nullptr, nullptr);
    if (!window) return 1;
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui::GetIO().IniFilename = nullptr;
    MonoUI::ApplyStyle(variant);
    const char* fonts = std::getenv("MONO_UI_FONTS") ? std::getenv("MONO_UI_FONTS") : MONO_UI_FONTS_DIR;
    MonoUI::LoadFonts(fonts);
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    bool nightly = true, offline = false;
    int mode = 0;
    float volume = 0.62f;
    char host[64] = "black-hole";
    int frame = 0;
    const MonoUI::Palette& p = MonoUI::Colors();

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        const ImGuiViewport* vp = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(vp->WorkPos);
        ImGui::SetNextWindowSize(vp->WorkSize);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(28, 22));
        ImGui::Begin("main", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoSavedSettings);
        ImGui::PopStyleVar(3);

        ImGui::BeginChild("side", ImVec2(190, 0), ImGuiChildFlags_Borders);
        MonoUI::Label("Workspaces");
        static int sel = 0;
        const char* items[] = {"Black Hole", "Event Horizon", "Predator", "Stream kit", "Soundboard"};
        for (int i = 0; i < 5; ++i)
            if (ImGui::Selectable(items[i], sel == i)) sel = i;
        ImGui::SetCursorPosY(ImGui::GetWindowHeight() - ImGui::GetFrameHeightWithSpacing() - 6);
        MonoUI::Mono("Dear ImGui " IMGUI_VERSION);
        ImGui::EndChild();
        ImGui::SameLine(0, 24);

        ImGui::BeginGroup();
        MonoUI::Label("03 · Monitor");
        MonoUI::Heading(items[sel]);
        MonoUI::Muted("Proxmox VE 9.2 · Ryzen 9 7900X · RTX 3060");
        ImGui::Spacing();
        const char* nums[] = {"24", "64", "41%", "02:30"};
        const char* labs[] = {"Threads", "GB memory", "CPU", "Next backup"};
        MonoUI::Stats(nums, labs, 4);
        ImGui::Spacing();

        MonoUI::ButtonFill("Open console");
        ImGui::SameLine();
        MonoUI::ButtonLine("Mirror report");
        ImGui::SameLine();
        ImGui::Button("Outline");
        ImGui::SameLine();
        MonoUI::ButtonGhost("Ghost");
        ImGui::Spacing();

        if (ImGui::BeginTabBar("tabs")) {
            if (ImGui::BeginTabItem("Settings")) {
                ImGui::Spacing();
                ImGui::SetNextItemWidth(260);
                ImGui::InputText("Hostname", host, sizeof host);
                ImGui::SetNextItemWidth(260);
                const char* modes[] = {"Apt mirror", "Direct", "Offline"};
                ImGui::Combo("Updates", &mode, modes, 3);
                ImGui::SetNextItemWidth(260);
                ImGui::SliderFloat("Volume", &volume, 0, 1, "%.2f");
                MonoUI::Checkbox("Nightly backup", &nightly);
                ImGui::SameLine(0, 24);
                MonoUI::Checkbox("Offline", &offline);
                ImGui::SameLine(0, 24);
                ImGui::RadioButton("Btrfs", &mode, 0);
                ImGui::SameLine();
                ImGui::RadioButton("rsync", &mode, 1);
                ImGui::ProgressBar(0.64f, ImVec2(260, 4), "");
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Machines")) {
                if (ImGui::BeginTable("m", 3, ImGuiTableFlags_RowBg | ImGuiTableFlags_BordersInnerH | ImGuiTableFlags_BordersOuter)) {
                    ImGui::TableSetupColumn("Machine");
                    ImGui::TableSetupColumn("Address");
                    ImGui::TableSetupColumn("Role");
                    ImGui::TableHeadersRow();
                    const char* rows[3][3] = {{"Black Hole", "10.10.10.10", "Proxmox"}, {"Event Horizon", "10.10.10.11", "Backups"},
                                              {"Predator", "10.10.10.20", "Laptop"}};
                    for (auto& r : rows) {
                        ImGui::TableNextRow();
                        for (int c = 0; c < 3; ++c) { ImGui::TableSetColumnIndex(c); ImGui::TextUnformatted(r[c]); }
                    }
                    ImGui::EndTable();
                }
                ImGui::EndTabItem();
            }
            ImGui::EndTabBar();
        }
        ImGui::Spacing();
        ImGui::SeparatorText("Log");
        MonoUI::Mono("02:30:00  snapshot daily-04 created  18.2 GB");
        MonoUI::Mono("02:31:12  sent to event-horizon      ok");
        ImGui::EndGroup();
        ImGui::End();

        ImGui::Render();
        int w, h;
        glfwGetFramebufferSize(window, &w, &h);
        glViewport(0, 0, w, h);
        glClearColor(p.bg.x, p.bg.y, p.bg.z, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        if (shot && ++frame == 4) { savePPM(shot, w, h); break; }
        glfwSwapBuffers(window);
    }
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
