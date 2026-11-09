// mono-ui React components. Thin wrappers over the classes in mono.css, so they render
// square or round depending on data-mono, and server-render fine (no effects, no state
// except where noted). Import mono.css once at your app root.
//
//   import { MonoRoot, Button, Card, Stats, Kv, Field, Input, Tabs } from "./MonoUI";
//   <MonoRoot variant="round"><Button kind="fill">Save</Button></MonoRoot>
import * as React from "react";

export type Variant = "square" | "round" | "blend" | "paper";
type Div = React.HTMLAttributes<HTMLDivElement>;

const cx = (...parts: Array<string | false | null | undefined>) => parts.filter(Boolean).join(" ");

/** Sets data-mono on a wrapper. Put it at the root, or around any subtree to switch just that part. */
export function MonoRoot({ variant = "square", className, ...rest }: Div & { variant?: Variant }) {
  return <div data-mono={variant} className={className} {...rest} />;
}

// ---------- type ----------

export function Heading({ level = 1, className, ...rest }: React.HTMLAttributes<HTMLHeadingElement> & { level?: 1 | 2 | 3 }) {
  const Tag = (`h${level}` as unknown) as "h1";
  return <Tag className={cx(`m-h${level}`, className)} {...rest} />;
}

export function Label({ className, as: Tag = "span", ...rest }: React.HTMLAttributes<HTMLElement> & { as?: "span" | "div" | "p" }) {
  return <Tag className={cx("m-label", className)} {...rest} />;
}

export function Mono({ className, ...rest }: React.HTMLAttributes<HTMLSpanElement>) {
  return <span className={cx("m-mono", className)} {...rest} />;
}

/** "01 · Label" over a big title, with an optional note on the right. */
export function SectionHeader({ number, label, title, note }: { number?: string; label: string; title: React.ReactNode; note?: React.ReactNode }) {
  return (
    <div className="m-sh">
      <div>
        <span className="m-n">{number ? `${number} · ` : ""}<span className="m-label">{label}</span></span>
        <h2 className="m-h2">{title}</h2>
      </div>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

// ---------- controls ----------

export type ButtonKind = "outline" | "fill" | "line" | "ghost";
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  kind?: ButtonKind;
  size?: "small" | "normal" | "big";
  arrow?: boolean;
  busy?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { kind = "outline", size = "normal", arrow, busy, className, type = "button", ...rest }, ref) {
  return (
    <button ref={ref} type={type} aria-busy={busy || undefined}
      className={cx("m-btn", kind !== "outline" && kind, size !== "normal" && size, arrow && "arrow", busy && "is-busy", className)}
      {...rest} />
  );
});

export function Chip({ on, className, ...rest }: React.HTMLAttributes<HTMLSpanElement> & { on?: boolean }) {
  return <span className={cx("m-chip", on && "is-on", className)} {...rest} />;
}

export function Field({ label, hint, children }: { label: React.ReactNode; hint?: React.ReactNode; children: React.ReactNode }) {
  return (
    <label className="m-field">
      <span className="m-label">{label}</span>
      {children}
      {hint ? <span className="m-hint">{hint}</span> : null}
    </label>
  );
}

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function Input({ className, ...rest }, ref) {
  return <input ref={ref} className={cx("m-input", className)} {...rest} />;
});

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(function Select({ className, ...rest }, ref) {
  return <select ref={ref} className={cx("m-select", className)} {...rest} />;
});

export const TextArea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(function TextArea({ className, ...rest }, ref) {
  return <textarea ref={ref} className={cx("m-textarea", className)} {...rest} />;
});

type Toggle = Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & { children?: React.ReactNode };
export function Checkbox({ children, ...rest }: Toggle) {
  return <label className="m-check"><input type="checkbox" {...rest} /> {children}</label>;
}
export function Radio({ children, ...rest }: Toggle) {
  return <label className="m-radio"><input type="radio" {...rest} /> {children}</label>;
}
export function Switch({ children, ...rest }: Toggle) {
  return <label className="m-switch"><input type="checkbox" role="switch" {...rest} /> {children}</label>;
}

export function Progress({ value, busy }: { value?: number; busy?: boolean }) {
  const pct = Math.max(0, Math.min(100, value ?? 0));
  return (
    <div className={cx("m-progress", busy && "is-busy")} role="progressbar" aria-valuenow={busy ? undefined : pct} aria-valuemin={0} aria-valuemax={100}>
      <span style={{ "--value": `${pct}%` } as React.CSSProperties} />
    </div>
  );
}

/** Pill tabs. Controlled: pass value and onChange. */
export function Tabs<T extends string>({ items, value, onChange }: { items: Array<{ value: T; label: React.ReactNode; count?: number }>; value: T; onChange: (v: T) => void }) {
  return (
    <div className="m-tabs" role="tablist">
      {items.map((it) => (
        <button key={it.value} type="button" role="tab" className="m-tab" aria-selected={it.value === value} onClick={() => onChange(it.value)}>
          {it.label}{it.count !== undefined ? <span className="m-count">{it.count}</span> : null}
        </button>
      ))}
    </div>
  );
}

// ---------- data ----------

export function Card({ kind, className, ...rest }: Div & { kind?: "flat" | "strong" | "dashed" }) {
  return <div className={cx("m-card", kind, className)} {...rest} />;
}

export function Stats({ items }: { items: Array<{ value: React.ReactNode; label: React.ReactNode }> }) {
  return (
    <div className="m-stats">
      {items.map((s, i) => <div key={i}><b>{s.value}</b><span>{s.label}</span></div>)}
    </div>
  );
}

/** Key/value list. note renders small under the value. */
export function Kv({ items, align = "right" }: { items: Array<{ k: React.ReactNode; v: React.ReactNode; note?: React.ReactNode }>; align?: "right" | "left" }) {
  return (
    <dl className={cx("m-kv", align === "left" && "left")}>
      {items.map((it, i) => <div key={i}><dt>{it.k}</dt><dd>{it.v}{it.note ? <small>{it.note}</small> : null}</dd></div>)}
    </dl>
  );
}

export function Readout({ items }: { items: Array<{ k: React.ReactNode; v: React.ReactNode; note?: React.ReactNode; hot?: boolean }> }) {
  return (
    <dl className="m-readout">
      {items.map((it, i) => <div key={i} className={it.hot ? "is-hot" : undefined}><dt>{it.k}</dt><dd>{it.v}{it.note ? <small>{it.note}</small> : null}</dd></div>)}
    </dl>
  );
}

export function Status({ state = "info", title, children }: { state?: "info" | "loading" | "success" | "error"; title: React.ReactNode; children?: React.ReactNode }) {
  return (
    <div className={cx("m-status", state !== "info" && `is-${state}`)} role="status">
      <div><p>{title}</p>{children ? <p>{children}</p> : null}</div>
    </div>
  );
}

/** Canvas drawn with mono.js's 8×8 Bayer dither. fn(x, y, w, h) returns 0..1. */
export function Dither({ fn, size = 300, caption }: { fn: (x: number, y: number, w: number, h: number) => number; size?: number; caption?: [React.ReactNode, React.ReactNode] }) {
  const ref = React.useRef<HTMLCanvasElement>(null);
  React.useEffect(() => {
    let cancelled = false;
    // @ts-ignore -- plain JS module shipped next to mono.css
    import("../web/mono.js").then((m: { dither: (c: HTMLCanvasElement, f: typeof fn) => void }) => {
      if (!cancelled && ref.current) m.dither(ref.current, fn);
    });
    return () => { cancelled = true; };
  }, [fn]);
  return (
    <figure className="m-figure">
      <canvas ref={ref} width={size} height={size} />
      {caption ? <figcaption><span>{caption[0]}</span><span>{caption[1]}</span></figcaption> : null}
    </figure>
  );
}
