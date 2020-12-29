import copy
from io import BytesIO
from typing import Dict, Any, List
import json

from luabins import decode_luabins, encode_luabins
import lz4.block

from constant import SAV15_UNCOMPRESSED_SIZE, SAV16_UNCOMPRESSED_SIZE


class _LuaStateProperty:
    def __init__(self, key: str, default: Any):
        self.key = key

        self.default = default

    def __get__(self, obj: 'LuaState', objtype):
        return obj._get_nested_key(self.key, self.default)

    def __set__(self, obj: 'LuaState', value: Any):
        return obj._set_nested_key(self.key, value)


class LuaState:
    def __init__(
            self,
            version: int,
            raw_lua_state: List[Dict[Any, Any]]
    ):
        self.version = version

        self._active_state: Dict[Any, Any] = raw_lua_state[0]

        # For debugging purposes only
        self._raw_save_file = None
        self._raw_lua_state_dicts = raw_lua_state

        #with open("debug.txt", "w") as f:
#        #    f.write(json.dumps(raw_lua_state, indent=2))

    @classmethod
    def from_bytes(cls, version: int, input_bytes: bytes) -> 'LuaState':
        decompressed_bytes: bytes = input_bytes
        if version == 15:
            decompressed_bytes: bytes = lz4.block.decompress(input_bytes, uncompressed_size=SAV15_UNCOMPRESSED_SIZE)
        elif version == 16:
            decompressed_bytes: bytes = lz4.block.decompress(input_bytes, uncompressed_size=SAV16_UNCOMPRESSED_SIZE)

        return LuaState.from_dict(
            version,
            decode_luabins(BytesIO(decompressed_bytes))
        )

    @classmethod
    def from_dict(cls, version: int, input_dicts: List[Dict[Any, Any]]) -> 'LuaState':
        return LuaState(
            version,
            input_dicts
        )

    darkness = _LuaStateProperty("GameState.Resources.MetaPoints", 0.0)
    gems = _LuaStateProperty("GameState.Resources.Gems", 0.0)
    diamonds = _LuaStateProperty("GameState.Resources.SuperGems", 0.0)
    nectar = _LuaStateProperty("GameState.Resources.GiftPoints", 0.0)
    ambrosia = _LuaStateProperty("GameState.Resources.SuperGiftPoints", 0.0)
    chthonic_key = _LuaStateProperty("GameState.Resources.LockKeys", 0.0)
    titan_blood = _LuaStateProperty("GameState.Resources.SuperLockKeys", 0.0)
    hell_mode = _LuaStateProperty("GameState.Flags.HardMode", False)
    easy_mode_level = _LuaStateProperty("GameState.EasyModeLevel", 0.0)

    gift_record = _LuaStateProperty("CurrentRun.GiftRecord", {})
    npc_interactions = _LuaStateProperty("CurrentRun.NPCInteractions", {})
    trigger_record = _LuaStateProperty("CurrentRun.TriggerRecord", {})
    activation_record = _LuaStateProperty("CurrentRun.ActivationRecord", {})
    use_record = _LuaStateProperty("CurrentRun.UseRecord", {})
    text_lines = _LuaStateProperty("CurrentRun.TextLinesRecord", {})

    def _parse_nested_path_reference(
            self,
            path: str
    ) -> (Dict[Any, Any], str):
        (path_components, key) = self._split_path_into_key_and_components(path)
        state = self._active_state

        for component in path_components:
            if component not in state:
                return None, None
            state = state.get(component)

        return state, key

    def _split_path_into_key_and_components(self, path: str):
        components = path.split(".")
        path_components = components[:-1]
        key = components[-1]

        return path_components, key

    def _get_nested_key(self, path: str, default: Any) -> Any:
        """
        Sets a (potentially nested) key in a dict, such as the Game State.

        :param path: Target key. Nested keys can be denotated by "."
        For example, using the gamestate as our obj, "Resources.Gems" will map to gamestate['Resources']['Gems']
        The final key does not need to exist, but any intervening dicts must.
        In our example, 'Gems' may not exist, but 'Resources' must.
        :param default: Default value if it isn't found
        :return: None
        """
        (reference, key) = self._parse_nested_path_reference(path)

        if reference is None or key not in reference:
            return default

        return reference[key]

    def _set_nested_key(self, path: str, value: Any) -> None:
        """
        Sets a (potentially nested) key in a dict, such as the Game State.

        :param path: Target key. Nested keys can be denotated by "."
        For example, using the gamestate as our obj, "Resources.Gems" will map to gamestate['Resources']['Gems']
        The final key does not need to exist, but any intervening dicts must.
        In our example, 'Gems' may not exist, but 'Resources' must.
        :param value: value to set
        :return: None
        """
        (reference, key) = self._parse_nested_path_reference(path)
        reference[key] = value

    def to_bytes(self) -> bytes:
        if self.version <= 14:
            return encode_luabins(self.to_dicts())
        else:
            return lz4.block.compress(encode_luabins(self.to_dicts()), store_size=False)


    def to_dicts(self) -> List[Dict[Any, Any]]:
        return [
            copy.deepcopy(self._active_state)
        ]

    def dump_to_file(self, path: str):
        with open(path, 'w') as f:
            f.write(json.dumps(self._active_state, indent=2))
