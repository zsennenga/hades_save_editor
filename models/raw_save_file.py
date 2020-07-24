from typing import Dict, Any

from bin_utils import rpad_bytes
from constant import SAVE_DATA_V14_LENGTH, SAVE_DATA_V15_LENGTH, SAVE_DATA_V16_LENGTH
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
            parser_dict = {
                14: sav14_schema,
                15: sav15_schema,
                16: sav16_schema
            }

            input_bytes = f.read()
            version = version_identifier_schema.parse(input_bytes).version

            if version in parser_dict:
                parsed_schema = parser_dict[version].parse(input_bytes)
            else:
                raise Exception(f"Unsupported version {version}")

            return RawSaveFile(
                version,
                dict(parsed_schema.save_data.value)
            )

    def to_file(self, path: str) -> None:
        build_dictionary = {
            14: {
                'schema': sav14_schema,
                'save_data_schema': sav14_save_data_schema,
                'length': SAVE_DATA_V14_LENGTH
            },
            15: {
                'schema': sav15_schema,
                'save_data_schema': sav15_save_data_schema,
                'length': SAVE_DATA_V15_LENGTH
            },
            16: {
                'schema': sav16_schema,
                'save_data_schema': sav16_save_data_schema,
                'length': SAVE_DATA_V16_LENGTH
            }
        }

        if self.version in build_dictionary:
            build_dictionary[self.version]['schema'].build_file(
                {
                    'save_data': {
                        'data': rpad_bytes(
                            build_dictionary[self.version]['save_data_schema'].build(
                                self.save_data
                            ),
                            build_dictionary[self.version]['length']
                        )
                    }
                },
                filename=path,
            )
        else:
            raise Exception(f"Unsupported version {self.version}")
