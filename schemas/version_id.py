from construct import *

from constant import FILE_SIGNATURE

version_identifier_schema = Struct(
    "signature" / Const(FILE_SIGNATURE),
    "checksum" / Padding(4),
    "version" / Int32ul,
    GreedyBytes,
)
