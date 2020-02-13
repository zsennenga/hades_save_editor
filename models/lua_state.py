import copy
from io import BytesIO
from typing import Dict, Any, List

from luabins import decode_luabins, encode_luabins


class _LuaStateProperty:
    def __init__(self, key: str):
        self.key = key

    def __get__(self, obj: 'LuaState', objtype):
        return obj._get_nested_key(self.key)

    def __set__(self, obj: 'LuaState', value: Any):
        return obj._set_nested_key(self.key, value)


class LuaState:
    def __init__(
            self,
            raw_lua_state: List[Dict[Any, Any]]
    ):
        self._active_state: Dict[Any, Any] = raw_lua_state[0]

        # For debugging purposes only
        self._raw_save_file = None
        self._raw_lua_state_dicts = raw_lua_state

    @classmethod
    def from_bytes(cls, input_bytes: bytes) -> 'LuaState':
        return LuaState.from_dict(
            decode_luabins(BytesIO(input_bytes))
        )

    @classmethod
    def from_dict(cls, input_dicts: List[Dict[Any, Any]]) -> 'LuaState':
        return LuaState(
            input_dicts
        )

    darkness = _LuaStateProperty("GameState.Resources.MetaPoints")
    gems = _LuaStateProperty("GameState.Resources.Gems")
    diamonds = _LuaStateProperty("GameState.Resources.SuperGems")
    nectar = _LuaStateProperty("GameState.Resources.GiftPoints")
    ambrosia = _LuaStateProperty("GameState.Resources.SuperGiftPoints")
    chthonic_key = _LuaStateProperty("GameState.Resources.LockKeys")
    titan_blood = _LuaStateProperty("GameState.Resources.SuperLockKeys")

    def _parse_nested_path_reference(
            self,
            path: str
    ) -> (Dict[Any, Any], str):
        (path_components, key) = self._split_path_into_key_and_components(path)
        state = self._active_state

        for component in path_components:
            if component not in state:
                raise Exception(
                    f"Trying to get key {key} from lua GameState, but failed at {component} as it does not exist"
                )
            state = state.get(component)

        return state, key

    def _split_path_into_key_and_components(self, path: str):
        components = path.split(".")
        path_components = components[:-1]
        key = components[-1]

        return path_components, key

    def _get_nested_key(self, path: str) -> Any:
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
        if (len(reference) == 0):
            return None
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
        return encode_luabins(self.to_dicts())

    def to_dicts(self) -> List[Dict[Any, Any]]:
        return [
            copy.deepcopy(self._active_state)
        ]
