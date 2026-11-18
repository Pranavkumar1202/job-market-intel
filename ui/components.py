"""Small HTML helpers for the dashboard. No Streamlit import, so they are easy to test."""
from html import escape


def chips_html(names, kind="ok", empty="none"):
    """Coloured pills for a list of skill names. kind: ok, miss or skill."""
    if not names:
        return f'<span class="chip chip-none">{escape(empty)}</span>'
    return "".join(
        f'<span class="chip chip-{kind}">{escape(str(name))}</span>' for name in names
    )


def bar_row_html(label, value, max_value):
    """One horizontal bar: label, filled track, number."""
    width = 0 if max_value <= 0 else round(100 * value / max_value)
    width = max(0, min(100, width))
    return (
        '<div class="bar-row">'
        f'<div class="bar-label">{escape(str(label))}</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div>'
        f'<div class="bar-value">{int(value)}</div>'
        "</div>"
    )


def score_label(score):
    """0.703 -> '70' (a score out of 100)."""
    return str(round(max(0.0, min(1.0, score)) * 100))
