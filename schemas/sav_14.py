from construct import *

from constant import FILE_SIGNATURE

sav14_schema = Padded(
    3145728,
    Struct(
        "signature" / Const(FILE_SIGNATURE),
        "checksum" / Int32ul,
        "save_data" / Struct(
            "version" / Int32ul,
            "location" / PascalString(Int32ul, "utf8"),
            "runs" / Int32ul,
            "active_meta_points" / Int32ul,
            "active_shrine_points" / Int32ul,
            "easy_mode" / Byte,
            "hard_mode" / Byte,
            "key_count" / Int32ul,
            "keys" / Array(
                this.key_count,
                PascalString(Int32ul, "utf8")
            ),
            "current_map_name" / PascalString(Int32ul, "utf8"),
            "start_next_map" / PascalString(Int32ul, "utf8"),
            "lua_state_length" / Int32ul,
            "lua_state" / Array(this.lua_state_length, Byte)
        )
    )
)
