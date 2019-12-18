import zlib
from io import BytesIO

from luabins import decode_luabins

from constant import FILE_SIGNATURE
from schemas.sav_14 import sav14_schema


class HadesSaveFile:
    def __init__(self, raw_bytes: bytes):
        self.parsed_schema = sav14_schema.parse(raw_bytes)

        self.lua_state = decode_luabins(BytesIO(bytes(self.parsed_schema.lua_state)))

    @classmethod
    def from_file(cls, path):
        with open(path, 'rb') as f:
            return HadesSaveFile(f.read())

    def to_file(self, path):
        save_data = sav14_schema.save_data.build(self.parsed_schema.save_data)
        with open(path, 'wb') as f:
            f.write(FILE_SIGNATURE)
            f.write(zlib.adler32(save_data).to_bytes(4, "little"))
            f.write(save_data)
