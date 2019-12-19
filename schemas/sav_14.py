import zlib

from construct import *

from constant import FILE_SIGNATURE

sav14_schema = Struct(
    "signature" / Const(FILE_SIGNATURE),
    "checksum_offset" / Tell,
    "checksum" / Padding(4),
    "save_data_offset" / Tell,
    "save_data" / RawCopy(
        Padded(
            3145728 - this.save_data_offset,
            Struct(
                "version" / Int32ul,
                "location" / PascalString(Int32ul, "utf8"),
                "runs" / Int32ul,
                "active_meta_points" / Int32ul,
                "active_shrine_points" / Int32ul,
                "easy_mode" / Byte,
                "hard_mode" / Byte,
                "keys" / PrefixedArray(
                    Int32ul,
                    PascalString(Int32ul, "utf8")
                ),
                "current_map_name" / PascalString(Int32ul, "utf8"),
                "start_next_map" / PascalString(Int32ul, "utf8"),
                "lua_state" / PrefixedArray(Int32ul, Byte)
            )
        )
    ),
    "checksum" / Pointer(
        this.checksum_offset,
        Checksum(
            Int32ul,
            lambda data: zlib.adler32(data, 1),
            this.save_data.data
        )
    )

)
