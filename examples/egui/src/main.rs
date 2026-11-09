// cargo run -- round   (or square, blend, paper), from examples/egui
#[path = "../../../dist/apps/egui/mono_egui.rs"]
mod mono_egui;

use eframe::egui;
use mono_egui::Variant;

struct Demo { name: String, hidden: bool, density: u8, scale: f32 }

impl eframe::App for Demo {
    fn ui(&mut self, ui: &mut egui::Ui, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ui, |ui| {
            mono_egui::label(ui, "01 · Settings");
            mono_egui::heading(ui, "Display");
            mono_egui::muted(ui, "Changes apply after a restart.");
            ui.add_space(12.0);
            mono_egui::label(ui, "Name");
            ui.add(egui::TextEdit::singleline(&mut self.name).desired_width(280.0));
            ui.add_space(6.0);
            ui.checkbox(&mut self.hidden, "Show hidden files");
            ui.horizontal(|ui| {
                ui.radio_value(&mut self.density, 0, "Compact");
                ui.radio_value(&mut self.density, 1, "Comfortable");
            });
            ui.add(egui::Slider::new(&mut self.scale, 0.0..=100.0).text("scale"));
            mono_egui::progress(ui, 0.62, 420.0);
            ui.add_space(10.0);
            ui.horizontal(|ui| {
                mono_egui::button_fill(ui, "Save");
                let _ = ui.button("Preview");
                mono_egui::button_line(ui, "Reset");
                mono_egui::button_ghost(ui, "Cancel");
            });
            ui.add_space(12.0);
            mono_egui::card(ui).show(ui, |ui| {
                mono_egui::label(ui, "Last sync");
                ui.label(egui::RichText::new("12 files").size(30.0));
                ui.monospace("2026-11-04 14:02 · ~/Projects");
            });
        });
    }
}

fn main() -> eframe::Result {
    let v = match std::env::args().nth(1).as_deref() {
        Some("square") => Variant::Square,
        Some("blend") => Variant::Blend,
        Some("paper") => Variant::Paper,
        _ => Variant::Round,
    };
    let opts = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([720.0, 520.0]).with_position([0.0, 0.0]),
        ..Default::default()
    };
    eframe::run_native("mono-ui · egui", opts, Box::new(move |cc| {
        mono_egui::apply(&cc.egui_ctx, v);
        mono_egui::load_fonts(&cc.egui_ctx, v, concat!(env!("CARGO_MANIFEST_DIR"), "/../../fonts/ttf"));
        Ok(Box::new(Demo { name: "mono".into(), hidden: true, density: 0, scale: 62.0 }))
    }))
}
