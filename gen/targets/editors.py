"""Editors: Neovim, VS Code, Helix, Zed. Every variant."""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, Tokens, write



def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "editors"
    files: list[Path] = []
    for v in t.variants:
        files.append(neovim(t, o, v))
        files.append(lualine(t, o, v))
        files.append(helix(t, o, v))
    files += vscode(t, o)
    files.append(zed(t, o))
    return files


# ---------------------------------------------------------------- Neovim

NVIM_SYNTAX = {
    # legacy groups
    "Comment": "comment", "Constant": "constant", "String": "string", "Character": "string", "Number": "number",
    "Boolean": "boolean", "Float": "number", "Identifier": "variable", "Function": "function", "Statement": "keyword",
    "Conditional": "control", "Repeat": "control", "Label": "keyword", "Operator": "operator", "Keyword": "keyword",
    "Exception": "control", "PreProc": "macro", "Include": "keyword", "Define": "macro", "Macro": "macro",
    "PreCondit": "macro", "Type": "type", "StorageClass": "keyword", "Structure": "type", "Typedef": "type",
    "Special": "escape", "SpecialChar": "escape", "Tag": "tag", "Delimiter": "punctuation",
    "SpecialComment": "comment", "Debug": "macro", "Underlined": "link", "Todo": "strong", "Title": "heading",
    "Directory": "strong",
    # treesitter
    "@comment": "comment", "@comment.documentation": "comment", "@keyword": "keyword", "@keyword.function": "keyword",
    "@keyword.return": "control", "@keyword.operator": "keyword", "@keyword.import": "keyword",
    "@keyword.conditional": "control", "@keyword.repeat": "control", "@keyword.exception": "control",
    "@operator": "operator", "@punctuation": "punctuation", "@punctuation.bracket": "punctuation",
    "@punctuation.delimiter": "punctuation", "@punctuation.special": "escape", "@string": "string",
    "@string.escape": "escape", "@string.regexp": "regexp", "@string.special": "escape", "@character": "string",
    "@number": "number", "@number.float": "number", "@boolean": "boolean", "@constant": "constant",
    "@constant.builtin": "constant", "@constant.macro": "macro", "@function": "function", "@function.call": "function",
    "@function.method": "method", "@function.method.call": "method", "@function.builtin": "builtin",
    "@function.macro": "macro", "@constructor": "type", "@type": "type", "@type.builtin": "builtin",
    "@type.definition": "type", "@module": "namespace", "@variable": "variable", "@variable.builtin": "builtin",
    "@variable.parameter": "parameter", "@variable.member": "property", "@property": "property",
    "@attribute": "attribute", "@label": "keyword", "@tag": "tag", "@tag.attribute": "attribute",
    "@tag.delimiter": "punctuation", "@markup.heading": "heading", "@markup.strong": "strong",
    "@markup.italic": "emphasis", "@markup.link": "link", "@markup.link.url": "link", "@markup.raw": "code",
    "@markup.list": "punctuation", "@markup.quote": "comment", "@diff.plus": "added", "@diff.minus": "removed",
    "@diff.delta": "changed",
    # LSP semantic tokens
    "@lsp.type.class": "type", "@lsp.type.enum": "type", "@lsp.type.interface": "type", "@lsp.type.struct": "type",
    "@lsp.type.type": "type", "@lsp.type.typeParameter": "type", "@lsp.type.namespace": "namespace",
    "@lsp.type.parameter": "parameter", "@lsp.type.property": "property", "@lsp.type.variable": "variable",
    "@lsp.type.function": "function", "@lsp.type.method": "method", "@lsp.type.macro": "macro",
    "@lsp.type.keyword": "keyword", "@lsp.type.comment": "comment", "@lsp.type.string": "string",
    "@lsp.type.number": "number", "@lsp.type.enumMember": "constant", "@lsp.mod.readonly": "constant",
}


def nvim_style(spec: dict, extra: dict | None = None) -> str:
    parts = [f'fg = "{spec["color"].hex}"']
    for f in ("bold", "italic", "underline", "strikethrough"):
        if spec.get(f):
            parts.append(f"{f} = true")
    for k, val in (extra or {}).items():
        parts.append(f"{k} = {val}")
    return "{ " + ", ".join(parts) + " }"


def neovim(t: Tokens, o: Path, v: str) -> Path:
    e, s, term = t.editor(v), t.syntax(v), t.term(v)
    h = lambda **kw: "{ " + ", ".join(f'{k} = "{x.hex}"' if hasattr(x, "hex") else f"{k} = {str(x).lower()}"
                                      for k, x in kw.items()) + " }"
    ui = {
        "Normal": h(fg=e["fg"], bg=e["bg"]), "NormalNC": h(fg=e["fg"], bg=e["bg"]), "NormalFloat": h(fg=e["fg"], bg=e["surface"]),
        "FloatBorder": h(fg=e["borderStrong"], bg=e["surface"]), "FloatTitle": h(fg=e["strong"], bg=e["surface"], bold=True),
        "ColorColumn": h(bg=e["cursorLine"]), "Conceal": h(fg=e["faint"]), "Cursor": h(fg=e["bg"], bg=e["cursor"]),
        "lCursor": h(fg=e["bg"], bg=e["cursor"]), "CursorIM": h(fg=e["bg"], bg=e["cursor"]),
        "CursorLine": h(bg=e["cursorLine"]), "CursorColumn": h(bg=e["cursorLine"]),
        "CursorLineNr": h(fg=e["lineNrActive"], bold=True), "LineNr": h(fg=e["lineNr"]),
        "SignColumn": h(bg=e["bg"]), "FoldColumn": h(fg=e["faint"], bg=e["bg"]), "Folded": h(fg=e["muted"], bg=e["surface"]),
        "VertSplit": h(fg=e["border"]), "WinSeparator": h(fg=e["border"]), "EndOfBuffer": h(fg=e["bg"]),
        "NonText": h(fg=e["indent"]), "Whitespace": h(fg=e["indent"]), "SpecialKey": h(fg=e["faint"]),
        "Visual": h(bg=e["selection"]), "VisualNOS": h(bg=e["selection"]),
        "Search": h(fg=e["strong"], bg=e["search"]), "IncSearch": h(fg=e["onAccent"], bg=e["accent"]),
        "CurSearch": h(fg=e["onAccent"], bg=e["accent"]), "Substitute": h(fg=e["onAccent"], bg=e["accent"]),
        "MatchParen": h(fg=e["strong"], bg=e["match"], bold=True),
        "Pmenu": h(fg=e["fg"], bg=e["surface"]), "PmenuSel": h(fg=e["selectionFg"], bg=e["selection"]),
        "PmenuSbar": h(bg=e["surface"]), "PmenuThumb": h(bg=e["borderStrong"]),
        "StatusLine": h(fg=e["fg"], bg=e["panel"]), "StatusLineNC": h(fg=e["faint"], bg=e["panel"]),
        "TabLine": h(fg=e["muted"], bg=e["panel"]), "TabLineFill": h(bg=e["panel"]), "TabLineSel": h(fg=e["strong"], bg=e["bg"], bold=True),
        "WinBar": h(fg=e["muted"], bg=e["bg"]), "WinBarNC": h(fg=e["faint"], bg=e["bg"]),
        "ModeMsg": h(fg=e["strong"], bold=True), "MoreMsg": h(fg=e["strong"]), "Question": h(fg=e["strong"]),
        "ErrorMsg": h(fg=e["strong"], bold=True), "WarningMsg": h(fg=e["fg"]), "MsgArea": h(fg=e["fg"]),
        "WildMenu": h(fg=e["selectionFg"], bg=e["selection"]), "QuickFixLine": h(bg=e["cursorLine"], bold=True),
        "SpellBad": h(sp=e["strong"], undercurl=True), "SpellCap": h(sp=e["muted"], undercurl=True),
        "SpellRare": h(sp=e["muted"], undercurl=True), "SpellLocal": h(sp=e["muted"], undercurl=True),
        "DiagnosticError": h(fg=e["strong"], bold=True), "DiagnosticWarn": h(fg=t.shade(v, "gray.800")),
        "DiagnosticInfo": h(fg=e["muted"]), "DiagnosticHint": h(fg=e["faint"]), "DiagnosticOk": h(fg=e["fg"]),
        "DiagnosticUnderlineError": h(sp=e["strong"], undercurl=True), "DiagnosticUnderlineWarn": h(sp=t.shade(v, "gray.800"), undercurl=True),
        "DiagnosticUnderlineInfo": h(sp=e["muted"], underdotted=True), "DiagnosticUnderlineHint": h(sp=e["faint"], underdotted=True),
        "DiagnosticVirtualTextError": h(fg=e["strong"], bg=e["cursorLine"]), "DiagnosticVirtualTextWarn": h(fg=t.shade(v, "gray.800"), bg=e["cursorLine"]),
        "DiagnosticVirtualTextInfo": h(fg=e["muted"], bg=e["cursorLine"]), "DiagnosticVirtualTextHint": h(fg=e["faint"], bg=e["cursorLine"]),
        "DiffAdd": h(bg=t.shade(v, "gray.200")), "DiffDelete": h(fg=e["faint"], bg=e["bg"]),
        "DiffChange": h(bg=e["cursorLine"]), "DiffText": h(bg=t.shade(v, "gray.300"), bold=True),
        "LspReferenceText": h(bg=e["match"]), "LspReferenceRead": h(bg=e["match"]), "LspReferenceWrite": h(bg=e["match"], underline=True),
        "LspInlayHint": h(fg=e["faint"], italic=True), "LspSignatureActiveParameter": h(fg=e["strong"], bold=True, underline=True),
        # common plugins
        "GitSignsAdd": h(fg=t.shade(v, "gray.850")), "GitSignsChange": h(fg=t.shade(v, "gray.650")), "GitSignsDelete": h(fg=t.shade(v, "gray.500")),
        "TelescopeBorder": h(fg=e["border"], bg=e["bg"]), "TelescopeSelection": h(fg=e["strong"], bg=e["selection"]),
        "TelescopeMatching": h(fg=e["strong"], bold=True), "TelescopePromptPrefix": h(fg=e["strong"]),
        "CmpItemAbbrMatch": h(fg=e["strong"], bold=True), "CmpItemAbbrMatchFuzzy": h(fg=e["strong"], bold=True),
        "CmpItemKind": h(fg=e["muted"]), "CmpItemMenu": h(fg=e["faint"]),
        "NvimTreeNormal": h(fg=e["fg"], bg=e["panel"]), "NvimTreeFolderName": h(fg=e["fg"]), "NvimTreeRootFolder": h(fg=e["strong"], bold=True),
        "NeoTreeNormal": h(fg=e["fg"], bg=e["panel"]), "NeoTreeNormalNC": h(fg=e["fg"], bg=e["panel"]),
        "WhichKey": h(fg=e["strong"]), "WhichKeyDesc": h(fg=e["fg"]), "WhichKeyGroup": h(fg=e["muted"]),
        "IblIndent": h(fg=e["indent"]), "IblScope": h(fg=e["indentActive"]),
        "MiniStatuslineModeNormal": h(fg=e["onAccent"], bg=e["accent"], bold=True),
    }
    lines = [f"-- {t.title(v)} for Neovim. {HEADER}",
             "vim.cmd(\"highlight clear\")",
             "if vim.fn.exists(\"syntax_on\") == 1 then vim.cmd(\"syntax reset\") end",
             f"vim.o.background = \"{t.mode(v)}\"",
             f"vim.g.colors_name = \"mono-{v}\"",
             "local hl = function(name, opts) vim.api.nvim_set_hl(0, name, opts) end", ""]
    for name, val in ui.items():
        lines.append(f'hl("{name}", {val})')
    lines.append("")
    for name, role in NVIM_SYNTAX.items():
        lines.append(f'hl("{name}", {nvim_style(s[role])})')
    lines.append("")
    lines.append("-- terminal")
    for i, c in enumerate(term["ansi"]):
        lines.append(f'vim.g.terminal_color_{i} = "{c.hex}"')
    p = o / "nvim" / "colors" / f"mono-{v}.lua"
    write(p, "\n".join(lines) + "\n")
    return p


def lualine(t: Tokens, o: Path, v: str) -> Path:
    e = t.editor(v)
    def mode(bg, fg):
        return (f'{{ a = {{ bg = "{bg.hex}", fg = "{fg.hex}", gui = "bold" }}, b = {{ bg = "{e["surface"].hex}", fg = "{e["fg"].hex}" }}, '
                f'c = {{ bg = "{e["panel"].hex}", fg = "{e["muted"].hex}" }} }}')
    text = f"""-- lualine theme. require("lualine").setup({{ options = {{ theme = "mono_{v}" }} }})  {HEADER}
return {{
  normal = {mode(e["accent"], e["onAccent"])},
  insert = {mode(e["fg"], e["bg"])},
  visual = {mode(e["borderStrong"], e["bg"])},
  replace = {mode(e["muted"], e["bg"])},
  command = {mode(e["strong"], e["bg"])},
  inactive = {mode(e["surface"], e["faint"])},
}}
"""
    p = o / "nvim" / "lua" / "lualine" / "themes" / f"mono_{v}.lua"
    write(p, text)
    return p


# ---------------------------------------------------------------- Helix

HELIX_SYNTAX = {
    "comment": "comment", "keyword": "keyword", "keyword.control": "control", "keyword.function": "keyword",
    "operator": "operator", "punctuation": "punctuation", "string": "string", "string.regexp": "regexp",
    "constant.character.escape": "escape", "constant.numeric": "number", "constant": "constant",
    "constant.builtin.boolean": "boolean", "function": "function", "function.method": "method",
    "function.builtin": "builtin", "function.macro": "macro", "type": "type", "type.builtin": "builtin",
    "constructor": "type", "namespace": "namespace", "variable": "variable", "variable.parameter": "parameter",
    "variable.builtin": "builtin", "variable.other.member": "property", "attribute": "attribute", "tag": "tag",
    "label": "keyword", "special": "escape", "markup.heading": "heading", "markup.bold": "strong",
    "markup.italic": "emphasis", "markup.strikethrough": "removed", "markup.link.url": "link",
    "markup.link.text": "strong", "markup.raw": "code", "markup.quote": "comment", "markup.list": "punctuation",
    "diff.plus": "added", "diff.minus": "removed", "diff.delta": "changed",
}


def helix_style(spec: dict) -> str:
    mods = [m for m in ("bold", "italic", "crossed_out") if spec.get("strikethrough" if m == "crossed_out" else m)]
    out = f'{{ fg = "{spec["color"].hex}"'
    if mods:
        out += ", modifiers = [" + ", ".join(f'"{m}"' for m in mods) + "]"
    if spec.get("underline"):
        out += ', underline = { style = "line" }'
    return out + " }"


def helix(t: Tokens, o: Path, v: str) -> Path:
    e, s = t.editor(v), t.syntax(v)
    L = [f"# {t.title(v)} for Helix. Copy to ~/.config/helix/themes/ and set theme = \"mono-{v}\". {HEADER}", ""]
    for scope, role in HELIX_SYNTAX.items():
        L.append(f'"{scope}" = {helix_style(s[role])}')
    ui = {
        "ui.background": f'{{ bg = "{e["bg"].hex}" }}', "ui.text": f'{{ fg = "{e["fg"].hex}" }}',
        "ui.text.focus": f'{{ fg = "{e["strong"].hex}", modifiers = ["bold"] }}', "ui.text.inactive": f'{{ fg = "{e["faint"].hex}" }}',
        "ui.cursor": f'{{ fg = "{e["bg"].hex}", bg = "{e["muted"].hex}" }}',
        "ui.cursor.primary": f'{{ fg = "{e["bg"].hex}", bg = "{e["cursor"].hex}" }}',
        "ui.cursor.match": f'{{ bg = "{e["match"].hex}", modifiers = ["bold"] }}',
        "ui.cursorline.primary": f'{{ bg = "{e["cursorLine"].hex}" }}',
        "ui.selection": f'{{ bg = "{e["selection"].hex}" }}', "ui.selection.primary": f'{{ bg = "{e["selection"].hex}" }}',
        "ui.linenr": f'{{ fg = "{e["lineNr"].hex}" }}', "ui.linenr.selected": f'{{ fg = "{e["lineNrActive"].hex}", modifiers = ["bold"] }}',
        "ui.statusline": f'{{ fg = "{e["fg"].hex}", bg = "{e["panel"].hex}" }}',
        "ui.statusline.inactive": f'{{ fg = "{e["faint"].hex}", bg = "{e["panel"].hex}" }}',
        "ui.statusline.normal": f'{{ fg = "{e["onAccent"].hex}", bg = "{e["accent"].hex}", modifiers = ["bold"] }}',
        "ui.statusline.insert": f'{{ fg = "{e["bg"].hex}", bg = "{e["fg"].hex}", modifiers = ["bold"] }}',
        "ui.statusline.select": f'{{ fg = "{e["bg"].hex}", bg = "{e["borderStrong"].hex}", modifiers = ["bold"] }}',
        "ui.popup": f'{{ fg = "{e["fg"].hex}", bg = "{e["surface"].hex}" }}', "ui.window": f'{{ fg = "{e["border"].hex}" }}',
        "ui.help": f'{{ fg = "{e["fg"].hex}", bg = "{e["surface"].hex}" }}',
        "ui.menu": f'{{ fg = "{e["fg"].hex}", bg = "{e["surface"].hex}" }}',
        "ui.menu.selected": f'{{ fg = "{e["selectionFg"].hex}", bg = "{e["selection"].hex}" }}',
        "ui.virtual.whitespace": f'{{ fg = "{e["indent"].hex}" }}', "ui.virtual.indent-guide": f'{{ fg = "{e["indent"].hex}" }}',
        "ui.virtual.ruler": f'{{ bg = "{e["cursorLine"].hex}" }}', "ui.virtual.inlay-hint": f'{{ fg = "{e["faint"].hex}" }}',
        "ui.bufferline": f'{{ fg = "{e["muted"].hex}", bg = "{e["panel"].hex}" }}',
        "ui.bufferline.active": f'{{ fg = "{e["strong"].hex}", bg = "{e["bg"].hex}" }}',
        "error": f'{{ fg = "{e["strong"].hex}", modifiers = ["bold"] }}', "warning": f'{{ fg = "{t.shade(v, "gray.800").hex}" }}',
        "info": f'{{ fg = "{e["muted"].hex}" }}', "hint": f'{{ fg = "{e["faint"].hex}" }}',
        "diagnostic.error": f'{{ underline = {{ color = "{e["strong"].hex}", style = "curl" }} }}',
        "diagnostic.warning": f'{{ underline = {{ color = "{t.shade(v, "gray.800").hex}", style = "curl" }} }}',
        "diagnostic.info": f'{{ underline = {{ color = "{e["muted"].hex}", style = "dotted" }} }}',
        "diagnostic.hint": f'{{ underline = {{ color = "{e["faint"].hex}", style = "dotted" }} }}',
    }
    L.append("")
    L += [f'"{k}" = {val}' for k, val in ui.items()]
    p = o / "helix" / "themes" / f"mono-{v}.toml"
    write(p, "\n".join(L) + "\n")
    return p


# ---------------------------------------------------------------- VS Code

VSC_SCOPES = {
    "comment": ["comment", "punctuation.definition.comment"],
    "keyword": ["keyword", "storage", "storage.type", "storage.modifier", "keyword.other"],
    "control": ["keyword.control"],
    "operator": ["keyword.operator", "punctuation.separator.key-value"],
    "punctuation": ["punctuation", "meta.brace", "meta.delimiter"],
    "string": ["string", "punctuation.definition.string"],
    "escape": ["constant.character.escape", "constant.other.placeholder"],
    "regexp": ["string.regexp"],
    "number": ["constant.numeric"],
    "constant": ["constant", "support.constant", "variable.other.constant", "variable.other.enummember"],
    "boolean": ["constant.language.boolean", "constant.language"],
    "function": ["entity.name.function", "support.function", "meta.function-call"],
    "type": ["entity.name.type", "entity.name.class", "support.type", "support.class", "entity.other.inherited-class"],
    "namespace": ["entity.name.namespace", "entity.name.module"],
    "variable": ["variable", "meta.definition.variable"],
    "parameter": ["variable.parameter"],
    "property": ["variable.other.property", "variable.other.object.property", "support.type.property-name", "meta.object-literal.key"],
    "builtin": ["support.function.builtin", "variable.language", "support.variable"],
    "macro": ["entity.name.function.preprocessor", "meta.preprocessor", "entity.name.function.macro"],
    "tag": ["entity.name.tag"],
    "attribute": ["entity.other.attribute-name"],
    "heading": ["markup.heading", "entity.name.section"],
    "strong": ["markup.bold"],
    "emphasis": ["markup.italic"],
    "link": ["markup.underline.link", "string.other.link"],
    "code": ["markup.inline.raw", "markup.fenced_code", "markup.raw"],
    "added": ["markup.inserted"],
    "removed": ["markup.deleted"],
    "changed": ["markup.changed"],
}
VSC_SEMANTIC = {"namespace": "namespace", "class": "type", "enum": "type", "interface": "type", "struct": "type",
                "typeParameter": "type", "type": "type", "parameter": "parameter", "variable": "variable",
                "property": "property", "enumMember": "constant", "function": "function", "method": "method",
                "macro": "macro", "keyword": "keyword", "comment": "comment", "string": "string", "number": "number",
                "regexp": "regexp", "operator": "operator", "variable.readonly": "constant",
                "variable.defaultLibrary": "builtin", "function.defaultLibrary": "builtin"}


def vsc_font(spec: dict) -> str:
    return " ".join(f for f in ("bold", "italic", "underline", "strikethrough") if spec.get(f))


def vscode_theme(t: Tokens, v: str) -> dict:
    e, s, term = t.editor(v), t.syntax(v), t.term(v)
    a = lambda c, alpha: c.hex + f"{round(alpha * 255):02x}"
    names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    colors = {
        "editor.background": e["bg"].hex, "editor.foreground": e["fg"].hex,
        "editorCursor.foreground": e["cursor"].hex, "editor.lineHighlightBackground": e["cursorLine"].hex,
        "editor.lineHighlightBorder": "#00000000", "editor.selectionBackground": e["selection"].hex,
        "editor.inactiveSelectionBackground": a(e["selection"], 0.6), "editor.selectionHighlightBackground": a(e["match"], 0.8),
        "editor.wordHighlightBackground": a(e["match"], 0.8), "editor.wordHighlightStrongBackground": e["match"].hex,
        "editor.findMatchBackground": e["accent"].hex, "editor.findMatchHighlightBackground": a(e["search"], 0.6),
        "editor.findMatchBorder": e["strong"].hex,
        "editorLineNumber.foreground": e["lineNr"].hex, "editorLineNumber.activeForeground": e["lineNrActive"].hex,
        "editorIndentGuide.background1": e["indent"].hex, "editorIndentGuide.activeBackground1": e["indentActive"].hex,
        "editorWhitespace.foreground": e["indent"].hex, "editorRuler.foreground": e["indent"].hex,
        "editorBracketMatch.background": e["match"].hex, "editorBracketMatch.border": e["borderStrong"].hex,
        "editorBracketHighlight.foreground1": e["fg"].hex, "editorBracketHighlight.foreground2": e["muted"].hex,
        "editorBracketHighlight.foreground3": e["faint"].hex,
        "editorError.foreground": e["strong"].hex, "editorWarning.foreground": t.shade(v, "gray.800").hex,
        "editorInfo.foreground": e["muted"].hex, "editorHint.foreground": e["faint"].hex,
        "editorGutter.background": e["bg"].hex, "editorGutter.addedBackground": t.shade(v, "gray.850").hex,
        "editorGutter.modifiedBackground": t.shade(v, "gray.650").hex, "editorGutter.deletedBackground": t.shade(v, "gray.500").hex,
        "editorWidget.background": e["surface"].hex, "editorWidget.border": e["borderStrong"].hex,
        "editorSuggestWidget.background": e["surface"].hex, "editorSuggestWidget.border": e["border"].hex,
        "editorSuggestWidget.selectedBackground": e["selection"].hex, "editorSuggestWidget.highlightForeground": e["strong"].hex,
        "editorHoverWidget.background": e["surface"].hex, "editorHoverWidget.border": e["borderStrong"].hex,
        "editorGroup.border": e["border"].hex, "editorGroupHeader.tabsBackground": e["panel"].hex,
        "editorInlayHint.foreground": e["faint"].hex, "editorInlayHint.background": "#00000000",
        "diffEditor.insertedTextBackground": a(t.shade(v, "gray.900"), 0.10), "diffEditor.removedTextBackground": a(t.shade(v, "gray.0"), 0.5),
        "focusBorder": e["borderStrong"].hex, "foreground": e["fg"].hex, "descriptionForeground": e["muted"].hex,
        "errorForeground": e["strong"].hex, "icon.foreground": e["muted"].hex, "widget.border": e["border"].hex,
        "selection.background": e["selection"].hex, "textLink.foreground": e["strong"].hex,
        "textLink.activeForeground": e["strong"].hex, "textPreformat.foreground": t.shade(v, "gray.800").hex,
        "activityBar.background": e["panel"].hex, "activityBar.foreground": e["fg"].hex,
        "activityBar.inactiveForeground": e["faint"].hex, "activityBar.border": e["border"].hex,
        "activityBar.activeBorder": e["strong"].hex, "activityBarBadge.background": e["accent"].hex,
        "activityBarBadge.foreground": e["onAccent"].hex,
        "sideBar.background": e["panel"].hex, "sideBar.foreground": e["fg"].hex, "sideBar.border": e["border"].hex,
        "sideBarTitle.foreground": e["muted"].hex, "sideBarSectionHeader.background": e["panel"].hex,
        "sideBarSectionHeader.foreground": e["muted"].hex, "sideBarSectionHeader.border": e["border"].hex,
        "list.activeSelectionBackground": e["selection"].hex, "list.activeSelectionForeground": e["selectionFg"].hex,
        "list.inactiveSelectionBackground": e["cursorLine"].hex, "list.hoverBackground": e["cursorLine"].hex,
        "list.highlightForeground": e["strong"].hex, "list.focusOutline": e["borderStrong"].hex,
        "tab.activeBackground": e["bg"].hex, "tab.activeForeground": e["strong"].hex,
        "tab.inactiveBackground": e["panel"].hex, "tab.inactiveForeground": e["faint"].hex,
        "tab.border": e["border"].hex, "tab.activeBorderTop": e["strong"].hex, "tab.hoverBackground": e["cursorLine"].hex,
        "titleBar.activeBackground": e["panel"].hex, "titleBar.activeForeground": e["fg"].hex,
        "titleBar.inactiveBackground": e["panel"].hex, "titleBar.inactiveForeground": e["faint"].hex,
        "titleBar.border": e["border"].hex,
        "statusBar.background": e["panel"].hex, "statusBar.foreground": e["muted"].hex, "statusBar.border": e["border"].hex,
        "statusBar.debuggingBackground": e["accent"].hex, "statusBar.debuggingForeground": e["onAccent"].hex,
        "statusBar.noFolderBackground": e["panel"].hex, "statusBarItem.remoteBackground": e["accent"].hex,
        "statusBarItem.remoteForeground": e["onAccent"].hex,
        "panel.background": e["panel"].hex, "panel.border": e["border"].hex,
        "panelTitle.activeForeground": e["strong"].hex, "panelTitle.activeBorder": e["strong"].hex,
        "panelTitle.inactiveForeground": e["faint"].hex,
        "input.background": e["panel"].hex, "input.foreground": e["fg"].hex, "input.border": e["border"].hex,
        "input.placeholderForeground": e["faint"].hex, "inputOption.activeBorder": e["strong"].hex,
        "dropdown.background": e["surface"].hex, "dropdown.border": e["border"].hex,
        "button.background": e["accent"].hex, "button.foreground": e["onAccent"].hex,
        "button.hoverBackground": t.shade(v, "gray.800").hex, "button.secondaryBackground": e["surface"].hex,
        "button.secondaryForeground": e["fg"].hex, "badge.background": e["raised"].hex, "badge.foreground": e["strong"].hex,
        "scrollbarSlider.background": a(e["borderStrong"], 0.35), "scrollbarSlider.hoverBackground": a(e["borderStrong"], 0.55),
        "scrollbarSlider.activeBackground": a(e["borderStrong"], 0.8),
        "progressBar.background": e["strong"].hex, "breadcrumb.foreground": e["faint"].hex,
        "breadcrumb.focusForeground": e["fg"].hex, "menu.background": e["surface"].hex, "menu.foreground": e["fg"].hex,
        "menu.selectionBackground": e["selection"].hex, "menu.border": e["borderStrong"].hex,
        "notifications.background": e["surface"].hex, "notifications.border": e["border"].hex,
        "peekView.border": e["borderStrong"].hex, "peekViewEditor.background": e["panel"].hex,
        "peekViewResult.background": e["surface"].hex, "peekViewTitle.background": e["surface"].hex,
        "gitDecoration.addedResourceForeground": t.shade(v, "gray.850").hex,
        "gitDecoration.modifiedResourceForeground": t.shade(v, "gray.700").hex,
        "gitDecoration.deletedResourceForeground": t.shade(v, "gray.500").hex,
        "gitDecoration.untrackedResourceForeground": t.shade(v, "gray.800").hex,
        "gitDecoration.ignoredResourceForeground": t.shade(v, "gray.400").hex,
        "terminal.background": term["background"].hex, "terminal.foreground": term["foreground"].hex,
        "terminalCursor.foreground": term["cursor"].hex, "terminal.selectionBackground": a(term["selectionBg"], 0.5),
    }
    for i, c in enumerate(term["ansi"]):
        colors[f"terminal.ansi{'Bright' if i >= 8 else ''}{names[i % 8]}"] = c.hex
    token_colors = []
    for role, scopes in VSC_SCOPES.items():
        spec = s[role]
        token_colors.append({"name": role, "scope": scopes,
                             "settings": {"foreground": spec["color"].hex, "fontStyle": vsc_font(spec)}})
    semantic = {}
    for sel, role in VSC_SEMANTIC.items():
        spec = s[role]
        semantic[sel] = {"foreground": spec["color"].hex, **{f: True for f in ("bold", "italic", "underline", "strikethrough") if spec.get(f)}}
    return {"$schema": "vscode://schemas/color-theme", "name": t.title(v), "type": t.mode(v), "semanticHighlighting": True,
            "colors": colors, "tokenColors": token_colors, "semanticTokenColors": semantic}


def vscode(t: Tokens, o: Path) -> list[Path]:
    base = o / "vscode"
    files = []
    themes = []
    for v in t.variants:
        p = base / "themes" / f"mono-{v}-color-theme.json"
        write(p, json.dumps(vscode_theme(t, v), indent=2) + "\n")
        files.append(p)
        themes.append({"label": t.title(v), "uiTheme": "vs" if t.light(v) else "vs-dark", "path": f"./themes/mono-{v}-color-theme.json"})
    pkg = {
        "name": "mono-ui-theme", "displayName": "Mono", "description": "Black and white: Square, Round, Blend and Paper.",
        "version": t.data["version"], "publisher": "MaggiNephew", "license": "MIT",
        "repository": {"type": "git", "url": "https://github.com/MaggiNephew/mono-ui"},
        "engines": {"vscode": "^1.80.0"}, "categories": ["Themes"], "keywords": ["monochrome", "black", "white", "grayscale"],
        "contributes": {"themes": themes},
    }
    p = base / "package.json"
    write(p, json.dumps(pkg, indent=2) + "\n")
    files.append(p)
    p = base / "README.md"
    write(p, "# Mono for VS Code\n\nGreyscale themes from "
             "[mono-ui](https://github.com/MaggiNephew/mono-ui): Mono Square, Round and Blend (dark) and Mono Paper (light).\n\nInstall from this folder: "
             "`npx @vscode/vsce package` then `code --install-extension mono-ui-theme-*.vsix`, "
             "or copy the folder into `~/.vscode/extensions/`.\n")
    files.append(p)
    return files


# ---------------------------------------------------------------- Zed

ZED_SYNTAX = {"comment": "comment", "comment.doc": "comment", "keyword": "keyword", "operator": "operator",
              "punctuation": "punctuation", "punctuation.bracket": "punctuation", "punctuation.delimiter": "punctuation",
              "punctuation.special": "escape", "string": "string", "string.escape": "escape", "string.regex": "regexp",
              "string.special": "escape", "number": "number", "boolean": "boolean", "constant": "constant",
              "function": "function", "function.method": "method", "function.builtin": "builtin", "type": "type",
              "type.builtin": "builtin", "constructor": "type", "namespace": "namespace", "variable": "variable",
              "variable.special": "builtin", "variable.parameter": "parameter", "property": "property",
              "attribute": "attribute", "tag": "tag", "label": "keyword", "title": "heading", "emphasis": "emphasis",
              "emphasis.strong": "strong", "link_text": "strong", "link_uri": "link", "text.literal": "code",
              "embedded": "text", "preproc": "macro", "enum": "type", "variant": "constant"}


def zed(t: Tokens, o: Path) -> Path:
    themes = []
    for v in t.variants:
        e, term, s = t.editor(v), t.term(v), t.syntax(v)
        names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        style = {
            "background": e["panel"].hex, "editor.background": e["bg"].hex, "editor.foreground": e["fg"].hex,
            "editor.gutter.background": e["bg"].hex, "editor.active_line.background": e["cursorLine"].hex,
            "editor.line_number": e["lineNr"].hex, "editor.active_line_number": e["lineNrActive"].hex,
            "editor.indent_guide": e["indent"].hex, "editor.indent_guide_active": e["indentActive"].hex,
            "editor.document_highlight.read_background": e["match"].hex,
            "editor.subheader.background": e["panel"].hex, "editor.wrap_guide": e["indent"].hex,
            "surface.background": e["surface"].hex, "elevated_surface.background": e["surface"].hex,
            "panel.background": e["panel"].hex, "border": e["border"].hex, "border.variant": e["indent"].hex,
            "border.focused": e["borderStrong"].hex, "border.selected": e["borderStrong"].hex,
            "text": e["fg"].hex, "text.muted": e["muted"].hex, "text.placeholder": e["faint"].hex,
            "text.disabled": t.shade(v, "gray.400").hex, "text.accent": e["strong"].hex, "icon": e["muted"].hex,
            "icon.muted": e["faint"].hex, "icon.accent": e["strong"].hex,
            "element.background": e["surface"].hex, "element.hover": e["cursorLine"].hex,
            "element.active": e["selection"].hex, "element.selected": e["selection"].hex,
            "ghost_element.hover": e["cursorLine"].hex, "ghost_element.selected": e["selection"].hex,
            "tab_bar.background": e["panel"].hex, "tab.active_background": e["bg"].hex,
            "tab.inactive_background": e["panel"].hex, "toolbar.background": e["bg"].hex,
            "title_bar.background": e["panel"].hex, "status_bar.background": e["panel"].hex,
            "scrollbar.thumb.background": e["borderStrong"].hex + "55", "scrollbar.track.background": "#00000000",
            "search.match_background": e["search"].hex,
            "error": e["strong"].hex, "warning": t.shade(v, "gray.800").hex, "info": e["muted"].hex, "hint": e["faint"].hex,
            "success": e["fg"].hex, "created": t.shade(v, "gray.850").hex, "modified": t.shade(v, "gray.650").hex,
            "deleted": t.shade(v, "gray.500").hex, "conflict": e["strong"].hex, "ignored": t.shade(v, "gray.400").hex,
            "terminal.background": term["background"].hex, "terminal.foreground": term["foreground"].hex,
            "terminal.bright_foreground": t.shade(v, "gray.1000").hex, "terminal.dim_foreground": t.shade(v, "gray.650").hex,
            "players": [{"cursor": e["cursor"].hex, "background": e["cursor"].hex, "selection": e["selection"].hex}],
            "syntax": {k: {"color": s[r]["color"].hex,
                           "font_style": "italic" if s[r].get("italic") else None,
                           "font_weight": 700 if s[r].get("bold") else None} for k, r in ZED_SYNTAX.items()},
        }
        for i, c in enumerate(term["ansi"]):
            style[f"terminal.ansi.{'bright_' if i >= 8 else ''}{names[i % 8]}"] = c.hex
        themes.append({"name": t.title(v), "appearance": t.mode(v), "style": style})
    doc = {"$schema": "https://zed.dev/schema/themes/v0.2.0.json", "name": "Mono", "author": "MaggiNephew", "themes": themes}
    p = o / "zed" / "themes" / "mono.json"
    write(p, json.dumps(doc, indent=2) + "\n")
    return p
