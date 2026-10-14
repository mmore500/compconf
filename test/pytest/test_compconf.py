import pytest

from compconf.__main__ import make_csl_data_literal, make_csl_source


def test_make_csl_data_literal():
    data = {
        "A:u32": 1,
        "B:comptime_string": "x",
        "C:bool": True,
        "_compconf_dummy:u32": 42,
    }
    assert make_csl_data_literal(data) == (
        '.{ .A = @as(u32, 1), .B = "x", .C = true, '
        "._compconf_dummy = @as(u32, 42) }"
    )


def test_make_csl_data_literal_float_and_false():
    data = {"f:f32": 1.5, "b:bool": False}
    assert make_csl_data_literal(data) == (
        ".{ .f = @as(f32, 1.5), .b = false }"
    )


def test_make_csl_data_literal_array():
    assert make_csl_data_literal({"arr:[3]i16": [1, -2, 3]}) == (
        ".{ .arr = [3]i16 { 1, -2, 3 } }"
    )


def test_make_csl_data_literal_nested_and_color():
    data = {"s:comptime_struct": {"a:u8": 1, "c:color": 4}}
    assert make_csl_data_literal(data) == (
        ".{ .s = .{ .a = @as(u8, 1), .c = @get_color(4) } }"
    )


@pytest.mark.parametrize(
    "data",
    [
        {"a:u32": None},
        {"a:[2]u32": [1]},
        {"a": [1, 2]},
        {"a:[2]u32": [[1], [2]]},
        {"a": 1},
    ],
)
def test_make_csl_data_literal_invalid(data):
    with pytest.raises(ValueError):
        make_csl_data_literal(data)


def test_make_csl_source_embeds_literal():
    assert "const _data = .{ .a = @as(u32, 1) };" in make_csl_source(
        {"a:u32": 1},
    )
