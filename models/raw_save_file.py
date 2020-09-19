from typing import Dict, Any

from bin_utils import rpad_bytes
from constant import SAVE_DATA_V14_LENGTH, SAVE_DATA_V15_LENGTH
from schemas.sav_14 import sav14_schema, sav14_save_data_schema
from schemas.sav_15 import sav15_schema, sav15_save_data_schema
from schemas.sav_16 import sav16_schema, sav16_save_data_schema
from schemas.version_id import version_identifier_schema


class RawSaveFile:
    def __init__(
            self,
            version: int,
            save_data: Dict[Any, Any],
    ):
        self.version = version
        self.save_data = save_data
        self.lua_state_bytes = save_data['lua_state']

    @classmethod
    def from_file(cls, path: str) -> 'RawSaveFile':
        with open(path, 'rb') as f:
            input_bytes = f.read()
            version = version_identifier_schema.parse(input_bytes).version

            if version == 14:
                parsed_schema = sav14_schema.parse(input_bytes)
            elif version == 15:
                parsed_schema = sav15_schema.parse(input_bytes)
            elif version == 16:
                parsed_schema = sav16_schema.parse(input_bytes)
            else:
                raise Exception(f"Unsupported version {version}")

            return RawSaveFile(
                version,
                dict(parsed_schema.save_data.value)
            )

    def to_file(self, path: str) -> None:
        if self.version == 14:
            sav14_schema.build_file(
                {
                    'save_data': {
                        'data': rpad_bytes(
                            sav14_save_data_schema.build(
                                self.save_data
                            ),
                            SAVE_DATA_V14_LENGTH
                        )
                    }
                },
                filename=path,
            )
        elif self.version == 15:
            sav15_schema.build_file(
                {
                    'save_data': {
                        'data': rpad_bytes(
                            sav15_save_data_schema.build(
                                self.save_data
                            ),
                            SAVE_DATA_V15_LENGTH
                        )
                    }
                },
                filename=path,
            )
        elif self.version == 16:
            sav15_schema.build_file(
                {
                    'save_data': {
                        'data': sav16_save_data_schema.build(
                            self.save_data
                        )
                    }
                },
                filename=path,
            )
        else:
            raise Exception(f"Unsupported version {self.version}")
