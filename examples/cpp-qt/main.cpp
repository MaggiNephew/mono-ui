// mono-ui Qt demo in C++.
//   ./mono_qt_demo            round
//   ./mono_qt_demo square     square
//   ./mono_qt_demo round --shot out.png
#include "mono_qt.hpp"

#include <QCheckBox>
#include <QComboBox>
#include <QFrame>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QSlider>
#include <QSpinBox>
#include <QStatusBar>
#include <QTableWidget>
#include <QTabWidget>
#include <QTimer>
#include <QVBoxLayout>

using monoui::setKind;
using monoui::setRole;

static QLabel* label(const QString& text, const char* role) {
    auto* l = new QLabel(text);
    setRole(l, role);
    return l;
}

static QPushButton* button(const QString& text, const char* kind = nullptr) {
    auto* b = new QPushButton(text);
    if (kind) setKind(b, kind);
    return b;
}

static QFrame* stats(const QList<QPair<QString, QString>>& items) {
    auto* box = new QFrame;
    setRole(box, "stats");
    auto* lay = new QHBoxLayout(box);
    lay->setContentsMargins(0, 0, 0, 0);
    lay->setSpacing(0);
    for (int i = 0; i < items.size(); ++i) {
        auto* cell = new QFrame;
        if (i < items.size() - 1) setRole(cell, "cell");
        auto* v = new QVBoxLayout(cell);
        v->setContentsMargins(14, 12, 14, 10);
        v->setSpacing(2);
        v->addWidget(label(items[i].first, "stat"));
        v->addWidget(label(items[i].second, "label"));
        lay->addWidget(cell);
    }
    return box;
}

int main(int argc, char** argv) {
    QApplication app(argc, argv);
    const QStringList args = app.arguments();
    QString name = "round";
    auto variant = monoui::Variant::Round;
    if (args.contains("square")) { name = "square"; variant = monoui::Variant::Square; }
    if (args.contains("blend")) { name = "blend"; variant = monoui::Variant::Blend; }
    if (args.contains("paper")) { name = "paper"; variant = monoui::Variant::Paper; }
    const QString fonts = qEnvironmentVariable("MONO_UI_FONTS", QString(MONO_UI_FONTS_DIR));
    monoui::apply(app, variant, fonts);

    QMainWindow win;
    win.setWindowTitle(QString("mono-ui · Qt C++ · ") + name);
    auto* root = new QWidget;
    win.setCentralWidget(root);
    auto* outer = new QHBoxLayout(root);
    outer->setContentsMargins(0, 0, 0, 0);
    outer->setSpacing(0);

    auto* side = new QWidget;
    side->setFixedWidth(200);
    auto* sv = new QVBoxLayout(side);
    sv->setContentsMargins(16, 18, 12, 16);
    sv->addWidget(label("Machines", "label"));
    auto* list = new QListWidget;
    list->addItems({"Black Hole", "Event Horizon", "Predator", "Pi"});
    list->setCurrentRow(1);
    sv->addWidget(list, 1);
    sv->addWidget(label("C++17 · Qt 6", "mono"));
    outer->addWidget(side);
    auto* rule = new QFrame;
    setRole(rule, "rule");
    rule->setFixedWidth(1);
    rule->setMaximumHeight(QWIDGETSIZE_MAX);
    outer->addWidget(rule);

    auto* main = new QWidget;
    auto* mv = new QVBoxLayout(main);
    mv->setContentsMargins(28, 22, 28, 22);
    mv->setSpacing(14);
    mv->addWidget(label("02 · Backups", "label"));
    mv->addWidget(label("Event Horizon", "h1"));
    mv->addWidget(label("Raspberry Pi 5 · apt-cacher-ng · 1 TB", "muted"));
    mv->addWidget(stats({{"7", "Daily"}, {"4", "Weekly"}, {"3", "Monthly"}, {"02:30", "Next run"}}));

    auto* row = new QHBoxLayout;
    row->setSpacing(8);
    row->addWidget(button("Back up now", "fill"));
    row->addWidget(button("Restore", "line"));
    row->addWidget(button("Outline"));
    row->addWidget(button("Ghost", "ghost"));
    auto* off = button("Disabled");
    off->setEnabled(false);
    row->addWidget(off);
    row->addStretch(1);
    mv->addLayout(row);

    auto* tabs = new QTabWidget;
    auto* table = new QTableWidget(5, 3);
    table->setHorizontalHeaderLabels({"Snapshot", "Size", "When"});
    const char* rows[5][3] = {{"daily-04", "18.2 GB", "today 02:30"}, {"daily-03", "18.1 GB", "yesterday"},
                              {"weekly-44", "17.9 GB", "Sun"}, {"weekly-43", "17.4 GB", "last Sun"},
                              {"monthly-10", "16.8 GB", "Oct 1"}};
    for (int r = 0; r < 5; ++r)
        for (int c = 0; c < 3; ++c) table->setItem(r, c, new QTableWidgetItem(rows[r][c]));
    table->verticalHeader()->setVisible(false);
    table->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    table->setSelectionBehavior(QAbstractItemView::SelectRows);
    table->selectRow(0);
    tabs->addTab(table, "Snapshots");

    auto* form = new QWidget;
    auto* g = new QGridLayout(form);
    g->setContentsMargins(16, 16, 16, 16);
    g->setHorizontalSpacing(18);
    g->addWidget(label("Target", "label"), 0, 0);
    g->addWidget(new QLineEdit("/mnt/event-horizon"), 1, 0);
    g->addWidget(label("Schedule", "label"), 0, 1);
    auto* combo = new QComboBox;
    combo->addItems({"Nightly", "Hourly", "Manual"});
    g->addWidget(combo, 1, 1);
    g->addWidget(label("Keep", "label"), 0, 2);
    auto* spin = new QSpinBox;
    spin->setValue(14);
    g->addWidget(spin, 1, 2);
    auto* checks = new QHBoxLayout;
    checks->setSpacing(22);
    auto* c1 = new QCheckBox("Compress");
    c1->setChecked(true);
    checks->addWidget(c1);
    checks->addWidget(new QCheckBox("Encrypt"));
    auto* r1 = new QRadioButton("Btrfs send");
    r1->setChecked(true);
    checks->addWidget(r1);
    checks->addWidget(new QRadioButton("rsync"));
    checks->addStretch(1);
    g->addLayout(checks, 2, 0, 1, 3);
    auto* slider = new QSlider(Qt::Horizontal);
    slider->setValue(40);
    g->addWidget(slider, 3, 0, 1, 2);
    auto* bar = new QProgressBar;
    bar->setValue(82);
    g->addWidget(bar, 3, 2);
    g->setRowStretch(4, 1);
    tabs->addTab(form, "Settings");
    mv->addWidget(tabs, 1);

    outer->addWidget(main, 1);
    win.statusBar()->showMessage("last backup 02:30 · 18.2 GB · ok");
    win.resize(980, 640);
    win.show();

    const int shot = args.indexOf("--shot");
    if (shot > 0 && shot + 1 < args.size()) {
        const QString path = args[shot + 1];
        QTimer::singleShot(300, [&win, &app, path] { win.grab().save(path); app.quit(); });
    }
    return app.exec();
}
