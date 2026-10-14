import os
import pathlib
import shutil
import subprocess
import sys

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


@pytest.mark.parametrize("value", [[1, 2], {"a": 1}, None])
def test_make_csl_data_literal_unsupported(value):
    with pytest.raises(ValueError):
        make_csl_data_literal({"a:u32": value})


def test_make_csl_source_embeds_literal():
    assert "const _data = .{ .a = @as(u32, 1) };" in make_csl_source(
        {"a:u32": 1},
    )


CSLC = os.environ.get("CSLC", "cslc")


@pytest.mark.skipif(
    shutil.which(CSLC) is None and not os.path.exists(CSLC),
    reason="cslc >= 2.10 not available",
)
def test_compile_with_cslc(tmp_path):
    here = pathlib.Path(__file__).parent / "compile_csl"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "compconf",
            "--compconf-cslc",
            CSLC,
            "--compconf-dump",
            str(tmp_path / "compconf.json"),
            "--compconf-jq",
            '. += {"present:u32": 7}',
            str(here / "layout.csl"),
            "--fabric-dims=1,1",
            "--fabric-offsets=0,0",
            "-o",
            str(tmp_path / "out"),
        ],
        check=True,
    )
