// cargo run -- round   (or square, blend, paper), from examples/iced
#[path = "../../../dist/apps/iced/mono_iced.rs"]
mod mono_iced;

use iced::widget::{button, checkbox, column, container, progress_bar, radio, row, text, text_input};
use iced::{Element, Length, Theme};
use mono_iced::Variant;

#[derive(Debug, Clone)]
enum Msg { Name(String), Hidden(bool), Density(u8), Noop }

struct Demo { v: Variant, name: String, hidden: bool, density: Option<u8> }

impl Demo {
    fn update(&mut self, m: Msg) {
        match m {
            Msg::Name(s) => self.name = s,
            Msg::Hidden(b) => self.hidden = b,
            Msg::Density(d) => self.density = Some(d),
            Msg::Noop => {}
        }
    }

    fn view(&self) -> Element<'_, Msg> {
        let c = mono_iced::palette(self.v);
        let up = |s: &str| if mono_iced::uppercase(self.v) { s.to_uppercase() } else { s.to_owned() };
        let content = column![
            text(up("01 · Settings")).size(11).color(c.fg_muted),
            text("Display").size(44).color(c.fg).font(mono_iced::display_font(self.v)),
            text("Changes apply after a restart.").color(c.fg_muted),
            text(up("Name")).size(11).color(c.fg_muted),
            text_input("name", &self.name).on_input(Msg::Name).width(280),
            checkbox(self.hidden).label("Show hidden files").on_toggle(Msg::Hidden),
            row![
                radio("Compact", 0u8, self.density, Msg::Density),
                radio("Comfortable", 1u8, self.density, Msg::Density),
            ].spacing(20),
            progress_bar(0.0..=1.0, 0.62).length(420).girth(4),
            row![
                button(text(up("Save"))).style(mono_iced::button_fill).on_press(Msg::Noop),
                button(text(up("Preview"))).style(mono_iced::button_outline).on_press(Msg::Noop),
                button(text(up("Reset"))).style(mono_iced::button_line).on_press(Msg::Noop),
                button(text(up("Cancel"))).style(mono_iced::button_ghost).on_press(Msg::Noop),
            ].spacing(8),
            container(column![
                text(up("Last sync")).size(11).color(c.fg_muted),
                text("12 files").size(30).font(mono_iced::display_font(self.v)),
                text("2026-11-04 14:02 · ~/Projects").size(12).color(c.fg_dim),
            ].spacing(4)).style(mono_iced::card).padding(16).width(320),
        ].spacing(12).padding(24);
        container(content).width(Length::Fill).height(Length::Fill).into()
    }

    fn theme(&self) -> Theme { mono_iced::theme(self.v) }
}

fn main() -> iced::Result {
    let v = match std::env::args().nth(1).as_deref() {
        Some("square") => Variant::Square,
        Some("blend") => Variant::Blend,
        Some("paper") => Variant::Paper,
        _ => Variant::Round,
    };
    iced::application(move || Demo { v, name: "mono".into(), hidden: true, density: Some(0) }, Demo::update, Demo::view)
        .theme(Demo::theme)
        .font(include_bytes!("../../../fonts/ttf/SpaceGrotesk-Regular.ttf").as_slice())
        .font(include_bytes!("../../../fonts/ttf/Fraunces-Light.ttf").as_slice())
        .font(include_bytes!("../../../fonts/ttf/3270NerdFont-Regular.ttf").as_slice())
        .default_font(mono_iced::font(v))
        .window(iced::window::Settings { size: iced::Size::new(720.0, 560.0), position: iced::window::Position::Specific(iced::Point::ORIGIN), ..Default::default() })
        .run()
}
