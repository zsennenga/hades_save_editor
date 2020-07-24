from typing import List, Optional

from models.lua_state import LuaState
from models.raw_save_file import RawSaveFile


class HadesSaveFile:
    def __init__(
            self,
            version: int,
            timestamp: int,
            location: str,
            runs: int,
            active_meta_points: int,
            active_shrine_points: int,
            god_mode_enabled: bool,
            hell_mode_enabled: bool,
            lua_keys: List[str],
            current_map_name: str,
            start_next_map: str,
            lua_state: LuaState,
            raw_save_file: Optional[RawSaveFile] = None
    ):
        self.version = version
        self.timestamp = timestamp
        self.location = location
        self.runs = runs
        self.active_meta_points = active_meta_points
        self.active_shrine_points = active_shrine_points
        self.god_mode_enabled = god_mode_enabled
        self.hell_mode_enabled = hell_mode_enabled
        self.lua_keys = lua_keys
        self.current_map_name = current_map_name
        self.start_next_map = start_next_map
        self.lua_state = lua_state

        # Unusued, for debugging
        self.raw_save_file = raw_save_file

    @classmethod
    def from_file(cls, path):
        raw_save_file = RawSaveFile.from_file(path)
        lua_state = LuaState.from_bytes(
            version=raw_save_file.version,
            input_bytes=bytes(raw_save_file.lua_state_bytes)
        )

        # Unused, for debugging
        lua_state.raw_save_file = raw_save_file

        if raw_save_file.version < 16:
            return HadesSaveFile(
                version=raw_save_file.version,
                location=raw_save_file.save_data['location'],
                runs=raw_save_file.save_data['runs'],
                active_meta_points=raw_save_file.save_data['active_meta_points'],
                active_shrine_points=raw_save_file.save_data['active_shrine_points'],
                god_mode_enabled=raw_save_file.save_data['god_mode_enabled'],
                hell_mode_enabled=raw_save_file.save_data['hell_mode_enabled'],
                lua_keys=raw_save_file.save_data['lua_keys'],
                current_map_name=raw_save_file.save_data['current_map_name'],
                start_next_map=raw_save_file.save_data['start_next_map'],
                lua_state=lua_state,
                raw_save_file=raw_save_file
            )
        else:
            return HadesSaveFile(
                version=raw_save_file.version,
                timestamp=raw_save_file.save_data['timestamp'],
                location=raw_save_file.save_data['location'],
                runs=raw_save_file.save_data['runs'],
                active_meta_points=raw_save_file.save_data['active_meta_points'],
                active_shrine_points=raw_save_file.save_data['active_shrine_points'],
                god_mode_enabled=raw_save_file.save_data['god_mode_enabled'],
                hell_mode_enabled=raw_save_file.save_data['hell_mode_enabled'],
                lua_keys=raw_save_file.save_data['lua_keys'],
                current_map_name=raw_save_file.save_data['current_map_name'],
                start_next_map=raw_save_file.save_data['start_next_map'],
                lua_state=lua_state,
                raw_save_file=raw_save_file
            )

    def to_file(self, path):
        if self.version < 16:
            RawSaveFile(
                version=self.version,
                save_data={
                    'version': self.version,
                    'location': self.location,
                    'runs': self.runs,
                    'active_meta_points': self.active_meta_points,
                    'active_shrine_points': self.active_shrine_points,
                    'god_mode_enabled': self.god_mode_enabled,
                    'hell_mode_enabled': self.hell_mode_enabled,
                    'lua_keys': self.lua_keys,
                    'current_map_name': self.current_map_name,
                    'start_next_map': self.start_next_map,
                    'lua_state': self.lua_state.to_bytes(),
                }
            ).to_file(path)
        elif self.version == 16:
            RawSaveFile(
                version=16,
                save_data={
                    'version': self.version,
                    'timestamp': self.timestamp,
                    'location': self.location,
                    'runs': self.runs,
                    'active_meta_points': self.active_meta_points,
                    'active_shrine_points': self.active_shrine_points,
                    'god_mode_enabled': self.god_mode_enabled,
                    'hell_mode_enabled': self.hell_mode_enabled,
                    'lua_keys': self.lua_keys,
                    'current_map_name': self.current_map_name,
                    'start_next_map': self.start_next_map,
                    'lua_state': self.lua_state.to_bytes(),
                }
            ).to_file(path)
        else:
            raise Exception(f"Unsupported version {self.version}")
