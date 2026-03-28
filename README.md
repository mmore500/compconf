# compconf

[![CI](https://github.com/mmore500/compconf/actions/workflows/ci.yaml/badge.svg)](https://github.com/mmore500/compconf/actions/workflows/python-ci.yaml?query=branch:python)
[![GitHub stars](https://img.shields.io/github/stars/mmore500/compconf.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/mmore500/compconf)
[
![PyPi](https://img.shields.io/pypi/v/compconf.svg)
](https://pypi.python.org/pypi/compconf)
[![DOI](https://zenodo.org/badge/905963048.svg)](https://doi.org/10.5281/zenodo.19288520)

compconf enables flexible, type-rich comptime configuration of Cerebras Software Language (CSL) projects

-   Free software: MIT license

<!---
-   Documentation: <https://compconf.readthedocs.io>.
-->

## Usage

compconf wraps the `cslc` compiler, forwarding all non-compconf flags.

```bash
python3 -m compconf --compconf-jq '. += {"baz:f32": 42.0}'
```

Access configuration values in csl code using the `compconf` module.
```zig
const compconf = @import("compconf.zig");

fn main() void {
    @comptime_print(compconf.get_value("baz", f32));
    @comptime_print(compconf.get_value_or("bar", @as(f16, 24.0)));
}
```

The `compconf` module provides the following functions:
```zig
fn get_value(comptime field_name: comptime_string, comptime T: type) T

fn get_value_or(
    comptime field_name: comptime_string, comptime default_value: anytype
) @type_of(default_value)
```

Available options:
```
usage: __main__.py [-h] [--compconf-cslc COMPCONF_CSLC] [--compconf-data COMPCONF_DATA] [--compconf-jq COMPCONF_JQ] [--compconf-verbose]

compconf enables flexible, type-rich comptime configuration of csl projects.

options:
  -h, --help            show this help message and exit
  --compconf-cslc COMPCONF_CSLC
                        compiler command to run
  --compconf-data COMPCONF_DATA
                        json data file to read, if any
  --compconf-jq COMPCONF_JQ
                        jq command to add/modify data (e.g., '. += {"foo:u32": 42}')
  --compconf-verbose    enable verbose logging

JSON data must be formatted according to `@import_comptime_value` conventions. See <https://sdk.cerebras.net/csl/language/builtins#import-comptime-value> DISCLAIMER: Cerebras Software
Language is the intellectual property of Cerebras Systems, Inc. This project is not an official Cerebras project and is not affiliated with or endorsed by Cerebras Systems, Inc. in any
way. All trademarks, logos, and intellectual property associated with Cerebras Systems remain the exclusive property of Cerebras Systems, Inc.
```

## Installation

To install from PyPi with pip, run

```python3
python3 -m pip install compconf
```

## Citing

If compconf contributes to a scholarly work, please cite it as

> Matthew Andres Moreno. (2026). mmore500/compconf. Zenodo. https://doi.org/10.5281/zenodo.19288520

```bibtex
@software{moreno2026compconf,
  author = {Matthew Andres Moreno},
  title = {mmore500/compconf},
  month = mar,
  year = 2026,
  publisher = {Zenodo},
  doi = {10.5281/zenodo.19288520},
  url = {https://doi.org/10.5281/zenodo.19288520}
}
```

And don't forget to leave a [star on GitHub](https://github.com/mmore500/compconf/stargazers)!

## Disclaimer

Cerebras Software Language is the intellectual property of Cerebras Systems, Inc.
This project is not an official Cerebras project and is not affiliated with or endorsed by Cerebras Systems, Inc. in any way.
All trademarks, logos, and intellectual property associated with Cerebras Systems remain the exclusive property of Cerebras Systems, Inc.
