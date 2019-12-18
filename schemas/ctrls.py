from construct import *

ctrls_schema = Struct(
    "signature" / Const(b"\x53\x47\x42\x31"),
    "body" / Padded(
        2048,
        Struct(
            "total_key_count" / Int32ul,
            "key_mappings" / Array(
                this.total_key_count,
                Struct(
                    "unknown_const1" / Int32ul,
                    "name" / PascalString(Int32ul, "utf8"),
                    "key_count" / Int32ul,
                    "keyboard_keys" / Array(
                        this.key_count,
                        Int32ul
                    ),
                    "gamepad_keys" / Int32ul,
                    "mouse_keys" / Int32ul,
                    "unknown_flag" / Byte,
                    "use_shift" / Byte

                )
            )
        )
    )
)
