from io import BytesIO

from luabins import decode_luabins

from schemas.sav_14 import sav14_schema


class HadesSaveFile:
    def __init__(self, raw_bytes: bytes):
        self.parsed_schema = sav14_schema.parse(raw_bytes)

        self.lua_state = decode_luabins(
            BytesIO(bytes(self.parsed_schema.save_data.value.lua_state))
        )

    @classmethod
    def from_file(cls, path):
        with open(path, 'rb') as f:
            return HadesSaveFile(f.read())

    def to_file(self, path):
        sav14_schema.build_file(
            {'save_data': self.parsed_schema.save_data},
            filename=path,
        )
