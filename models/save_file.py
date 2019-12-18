from io import BytesIO

from luabins import decode_luabins

from schemas.sav_14 import sav14_schema


class HadesSaveFile:
    def __init__(self, raw_bytes: bytes):
        self.parsed_schema = sav14_schema.parse(raw_bytes)

        self.lua_state = decode_luabins(BytesIO(bytes(self.parsed_schema.lua_state)))
