// Swing demo. From the repo root:
//   javac -d build dist/apps/swing/monoui/MonoUI.java examples/swing/Demo.java
//   java -cp build Demo round        (or square, blend, paper)
import java.awt.*;
import java.nio.file.Path;
import javax.swing.*;
import monoui.MonoUI;

public class Demo {
    public static void main(String[] args) {
        MonoUI.Variant v = args.length > 0 ? MonoUI.Variant.valueOf(args[0].toUpperCase()) : MonoUI.Variant.ROUND;
        MonoUI.apply(v, Path.of("fonts/ttf"));
        SwingUtilities.invokeLater(() -> {
            JFrame f = new JFrame("mono-ui · swing · " + v.name().toLowerCase());
            JPanel p = new JPanel();
            p.setLayout(new BoxLayout(p, BoxLayout.Y_AXIS));
            p.setBorder(BorderFactory.createEmptyBorder(24, 24, 24, 24));
            p.add(left(MonoUI.label("01 · Settings", MonoUI.Role.LABEL)));
            p.add(left(MonoUI.label("Display", MonoUI.Role.H1)));
            p.add(left(MonoUI.label("Changes apply after a restart.", MonoUI.Role.MUTED)));
            p.add(Box.createVerticalStrut(16));

            JPanel row = new JPanel(new GridLayout(2, 2, 12, 4));
            row.add(MonoUI.label("Name", MonoUI.Role.LABEL));
            row.add(MonoUI.label("Theme", MonoUI.Role.LABEL));
            row.add(new JTextField("mono"));
            JComboBox<String> combo = new JComboBox<>(new String[]{"square", "round", "blend", "paper"});
            combo.setSelectedItem(v.name().toLowerCase());
            row.add(combo);
            row.setMaximumSize(new Dimension(520, 64));
            p.add(left(row));
            p.add(Box.createVerticalStrut(14));
            JCheckBox cb = new JCheckBox("Show hidden files", true);
            p.add(left(cb));
            JPanel radios = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 4));
            ButtonGroup g = new ButtonGroup();
            JRadioButton a = new JRadioButton("Compact", true), b = new JRadioButton("Comfortable");
            g.add(a); g.add(b); radios.add(a); radios.add(Box.createHorizontalStrut(24)); radios.add(b);
            radios.setMaximumSize(new Dimension(520, 30));
            p.add(left(radios));
            JProgressBar pb = new JProgressBar(0, 100); pb.setValue(62);
            pb.setPreferredSize(new Dimension(520, 4)); pb.setMaximumSize(new Dimension(520, 4));
            p.add(Box.createVerticalStrut(12)); p.add(left(pb)); p.add(Box.createVerticalStrut(20));

            JPanel btns = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
            btns.add(MonoUI.button("Save", MonoUI.Kind.FILL)); btns.add(Box.createHorizontalStrut(8));
            btns.add(MonoUI.button("Preview", MonoUI.Kind.OUTLINE)); btns.add(Box.createHorizontalStrut(8));
            btns.add(MonoUI.button("Reset", MonoUI.Kind.LINE)); btns.add(Box.createHorizontalStrut(8));
            btns.add(MonoUI.button("Cancel", MonoUI.Kind.GHOST));
            btns.setMaximumSize(new Dimension(720, 44));
            p.add(left(btns));
            p.add(Box.createVerticalStrut(20));

            JPanel card = MonoUI.card();
            card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
            card.add(MonoUI.label("Last sync", MonoUI.Role.LABEL));
            card.add(MonoUI.label("12 files", MonoUI.Role.STAT));
            card.add(MonoUI.label("2026-11-04 14:02 · ~/Projects", MonoUI.Role.MONO));
            card.setMaximumSize(new Dimension(320, 120));
            p.add(left(card));

            f.setContentPane(p);
            f.setSize(720, 560);
            f.setLocation(0, 0);
            f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            f.setVisible(true);
        });
    }

    static JComponent left(JComponent c) { c.setAlignmentX(Component.LEFT_ALIGNMENT); return c; }
}
