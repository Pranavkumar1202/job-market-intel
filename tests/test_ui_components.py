from ui.components import bar_row_html, chips_html, score_label


def test_chips_escape_html():
    out = chips_html(["<script>alert(1)</script>"], "ok")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_chips_empty_list_shows_none():
    assert "none" in chips_html([], "miss")


def test_bar_width_is_proportional_and_safe():
    assert "width:50%" in bar_row_html("Python", 5, 10)
    assert "width:0%" in bar_row_html("Python", 5, 0)
    assert "width:100%" in bar_row_html("Python", 50, 10)


def test_score_label_rounds_and_clamps():
    assert score_label(0.703) == "70"
    assert score_label(1.7) == "100"
    assert score_label(-0.2) == "0"


def test_chips_custom_empty_text():
    assert "nothing missing" in chips_html([], "miss", empty="nothing missing")
