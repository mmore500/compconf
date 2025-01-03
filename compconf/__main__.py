#!/usr/bin/env python3

import argparse
import itertools as it
import json
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile

import jq


# polyfill adapted from https://stackoverflow.com/a/16891418/17332200
def _removeprefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def make_parser():
    parser = argparse.ArgumentParser(
        description="compconf enables flexible, type-rich comptime configuration of csl projects.",
        epilog="""JSON data must be formatted according to `@import_comptime_value` conventions. See <https://sdk.cerebras.net/csl/language/builtins#import-comptime-value>

        DISCLAIMER: Cerebras Software Language is the intellectual property of Cerebras Systems, Inc. This project is not an official Cerebras project and is not affiliated with or endorsed by Cerebras Systems, Inc. in any way. All trademarks, logos, and intellectual property associated with Cerebras Systems remain the exclusive property of Cerebras Systems, Inc.""",
    )
    parser.add_argument(
        "--compconf-cslc",
        default="cslc",
        help="compiler command to run",
        type=str,
    )
    parser.add_argument(
        "--compconf-data",
        default="",
        help="json data file to read, if any",
        type=str,
    )
    parser.add_argument(
        "--compconf-dump",
        default="compconf.json",
        help="path to dump the final json data",
        type=str,
    )
    parser.add_argument(
        "--compconf-jq",
        action="append",
        default=[],
        help="""jq command to add/modify data (e.g., '. += {"foo:u32": 42}')""",
    )
    parser.add_argument(
        "--compconf-verbose",
        action="store_true",
        help="enable verbose logging",
    )
    parser.add_argument(
        "--import-path",
        action="append",
        default=[],
        help="additional import paths for cslc",
    )
    return parser


def make_csl_source(data_path: str) -> str:
    return f"""// autogenerated by compconf
const _data = @import_comptime_value(comptime_struct, "{data_path}");

fn has_value(comptime field_name: comptime_string) bool {{
    return @has_field(_data, field_name);
}}

fn get_value(comptime field_name: comptime_string, comptime T: type) T {{
    const field_value = @field(_data, field_name);
    const message = @strcat(
        "COMPCONF field `",
        field_name,
        "` configured with value ",
    );
    @comptime_print(message, field_value);
    return field_value;
}}

fn get_value_or(
    comptime field_name: comptime_string, comptime default_value: anytype
) @type_of(default_value) {{
    const has_value = has_value(field_name);
    if (has_value) {{
        return get_value(field_name, @type_of(default_value));
    }} else {{
        const message = @strcat(
            "COMPCONF missing field `",
            field_name,
            "`, falling back to default ",
        );
        @comptime_print(message, default_value);
        return default_value;
    }}
}}"""


def make_csl_raw(data: dict) -> str:
    res = """// autogenerated by compconf
    """
    for key, value in data.items():
        res += f"""const {key} = {repr(value).replace("'", '"')};\n"""

    return res


if __name__ == "__main__":
    args, unknown_args = make_parser().parse_known_args()
    if args.compconf_verbose:
        logging.basicConfig(level=logging.INFO, format="compconf %(message)s")

    logging.info(f"args={args} unknown_args={unknown_args}")

    data = (
        json.loads(pathlib.Path(args.compconf_data).read_text())
        if args.compconf_data
        else dict()
    )
    logging.info(f"initial data={data}")

    data["_compconf_dummy:u32"] = 42  # ensure csl interprets as struct
    logging.info(f"after dummy data={data}")

    for key, value in os.environ.items():
        prefix = "COMPCONFENV_"
        if key.startswith(prefix):
            logging.info(f"found env var key={key} value={value}")
            compconf_key = _removeprefix(key, prefix).replace("__", ":")
            try:
                data[compconf_key] = json.loads(value)
            except json.JSONDecodeError:
                logging.warning(
                    f"failed to parse value={value}, treating as string",
                )
                data[compconf_key] = value
    logging.info(f"after env data={data}")

    for jq_command in args.compconf_jq:
        logging.info(f"jq_command={jq_command}")
        jq_program = jq.compile(jq_command)
        data = jq_program.input(data).first()
        logging.info(f"after jq data={data}")

    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = f"{tmpdir}/data.json"
        source_path = f"{tmpdir}/compconf.csl"
        raw_path = f"{tmpdir}/compconf_raw.csl"
        logging.info(
            f"tmpdir={tmpdir} data_path={data_path} source_path={source_path}",
        )

        with open(data_path, "w") as data_file:
            json.dump(data, data_file)

        if args.compconf_dump:
            shutil.copy(data_path, args.compconf_dump)

        with open(source_path, "w") as source_file:
            csl_source_content = make_csl_source(data_path)
            logging.info(f"csl_source_content={csl_source_content}")
            source_file.write(csl_source_content)

        with open(raw_path, "w") as raw_file:
            csl_raw_content = make_csl_raw(data)
            logging.info(f"csl_raw_content={csl_raw_content}")
            raw_file.write(csl_raw_content)

        import_paths = args.import_path + [tmpdir]
        if "CSL_IMPORT_PATH" in os.environ:
            import_paths += os.environ["CSL_IMPORT_PATH"].split(":")

        import_paths = [*map(os.path.abspath, import_paths)]
        logging.info(f"import_paths={import_paths}")

        import_path = ":".join(import_paths)
        logging.info(f"import_path={import_path}")

        os.environ["CSL_IMPORT_PATH"] = import_path
        subprocess.run(
            [
                args.compconf_cslc,
                *[
                    item
                    for pair in zip(it.repeat("--import-path"), import_paths)
                    for item in pair
                ],
                *unknown_args,
            ],
            check=True,
        )
