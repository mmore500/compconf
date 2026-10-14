import argparse

from cerebras.sdk.runtime.sdkruntimepybind import (
    MemcpyDataType,
    MemcpyOrder,
    SdkRuntime,
)
from cerebras.sdk.sdk_utils import memcpy_view
import more_itertools as mit
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="the test compile output dir")
parser.add_argument("--cmaddr", help="IP:port for CS system")
args = parser.parse_args()

nRow, nCol = 1, 1  # number of rows, columns, and genome words

runner = SdkRuntime("out", cmaddr=args.cmaddr, suppress_simfab_trace=True)
runner.load()
runner.run()

x = np.zeros(1, dtype=np.uint32)
runner.memcpy_d2h(
    x,
    runner.get_id("x"),
    0,  # x0
    0,  # y0
    nCol,  # width
    nRow,  # height
    1,  # num wavelets
    streaming=False,
    data_type=MemcpyDataType.MEMCPY_32BIT,
    order=MemcpyOrder.ROW_MAJOR,
    nonblock=False,
)
assert mit.one(memcpy_view(x, np.dtype(np.uint32))) == 42
print("compconf.get_value ok")

y = np.zeros(1, dtype=np.float32)
runner.memcpy_d2h(
    y,
    runner.get_id("y"),
    0,  # x0
    0,  # y0
    nCol,  # width
    nRow,  # height
    1,  # num wavelets
    streaming=False,
    data_type=MemcpyDataType.MEMCPY_32BIT,
    order=MemcpyOrder.ROW_MAJOR,
    nonblock=False,
)
assert mit.one(memcpy_view(y, np.dtype(np.float32))) == 10.0
print("compconf.get_value_or ok")

z = np.zeros(1, dtype=np.uint32)
runner.memcpy_d2h(
    z,
    runner.get_id("z"),
    0,  # x0
    0,  # y0
    nCol,  # width
    nRow,  # height
    1,  # num wavelets
    streaming=False,
    data_type=MemcpyDataType.MEMCPY_32BIT,
    order=MemcpyOrder.ROW_MAJOR,
    nonblock=False,
)
assert mit.one(memcpy_view(z, np.dtype(np.uint32))) == 99
print("COMPCONFENV_ integration ok")

arr = np.zeros(3, dtype=np.uint32)
runner.memcpy_d2h(
    arr,
    runner.get_id("arr"),
    0,  # x0
    0,  # y0
    nCol,  # width
    nRow,  # height
    3,  # num wavelets
    streaming=False,
    data_type=MemcpyDataType.MEMCPY_32BIT,
    order=MemcpyOrder.ROW_MAJOR,
    nonblock=False,
)
assert list(memcpy_view(arr, np.dtype(np.uint32))) == [1, 2, 3]
print("compconf array ok")

nested_a = np.zeros(1, dtype=np.uint32)
runner.memcpy_d2h(
    nested_a,
    runner.get_id("nested_a"),
    0,  # x0
    0,  # y0
    nCol,  # width
    nRow,  # height
    1,  # num wavelets
    streaming=False,
    data_type=MemcpyDataType.MEMCPY_32BIT,
    order=MemcpyOrder.ROW_MAJOR,
    nonblock=False,
)
assert mit.one(memcpy_view(nested_a, np.dtype(np.uint32))) == 7
print("compconf nested struct ok")

runner.stop()

print("test/client.py complete")
