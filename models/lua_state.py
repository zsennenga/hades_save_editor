import copy
from io import BytesIO
from typing import Dict, Any, List

from luabins import decode_luabins, encode_luabins


class _LuaStateProperty:
    def __init__(self, obj_name, key):
        self.obj_name = obj_name
        self.key = key

    def __get__(self, obj, objtype):
        return obj._get_nested_key(obj.__dict__[self.obj_name], self.key)

    def __set__(self, obj, value):
        return obj._set_nested_key(obj.__dict__[self.obj_name], self.key, value)


class _GameStateProperty(_LuaStateProperty):
    def __init__(self, key):
        super(_GameStateProperty, self).__init__(
            obj_name="game_state",
            key=key
        )


class LuaState:
    def __init__(
            self,
            raw_lua_state: List[Dict[Any, Any]] = None
    ):
        self.active_state: Dict[Any, Any] = raw_lua_state[0]

        self.game_state: Dict[Any, Any] = self.active_state['GameState']

        # For debugging purposes only
        self.raw_save_file = None
        self.raw_lua_state_dicts = raw_lua_state

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

    gems = _GameStateProperty("Resources.Gems")
    diamonds = _GameStateProperty("Resources.SuperGems")
    nectar = _GameStateProperty("Resources.GiftPoints")
    ambrosia = _GameStateProperty("Resources.SuperGiftPoints")
    chthonic_key = _GameStateProperty("Resources.LockKeys")
    titan_blood = _GameStateProperty("Resources.SuperLockKeys")
    darkness = _GameStateProperty("Resources.MetaPoints")

    def _get_nested_path_reference(
            self,
            obj: Dict[Any, Any],
            path_components: List[str]
    ) -> Dict[Any, Any]:
        state = obj

        for component in path_components:
            if component not in state:
                raise Exception(
                    f"Failed to traverse via {path_components}"
                )
            state = state.get(component)

        return state

    def _split_path_into_key_and_components(self, path: str):
        components = path.split(".")
        path_components = components[:-1]
        key = components[-1]

        return path_components, key

    def _get_nested_key(self, obj: Dict[Any, Any], path: str) -> Any:
        """
        Sets a (potentially nested) key in a dict, such as the Game State.

        :param path: Target key. Nested keys can be denotated by "."
        For example, using the gamestate as our obj, "Resources.Gems" will map to gamestate['Resources']['Gems']
        The final key does not need to exist, but any intervening dicts must.
        In our example, 'Gems' may not exist, but 'Resources' must.
        :param value: value to set
        :return: None
        """
        (path_components, key) = self._split_path_into_key_and_components(path)

        try:
            reference = self._get_nested_path_reference(obj, path_components)
            return reference[key]
        except Exception as e:
            raise Exception(
                f"Trying to get key {key} from lua GameState, but failed at {component} as it does not exist"
            )

    def _set_nested_key(self, obj: Dict[Any, Any], path: str, value: Any) -> None:
        """
        Sets a (potentially nested) key in a dict, such as the Game State.

        :param path: Target key. Nested keys can be denotated by "."
        For example, using the gamestate as our obj, "Resources.Gems" will map to gamestate['Resources']['Gems']
        The final key does not need to exist, but any intervening dicts must.
        In our example, 'Gems' may not exist, but 'Resources' must.
        :param value: value to set
        :return: None
        """
        (path_components, key) = self._split_path_into_key_and_components(path)

        try:
            reference = self._get_nested_path_reference(obj, path_components)
            reference[key] = value
        except Exception as e:
            raise Exception(
                f"Trying to get key {key} from lua GameState, but failed at {component} as it does not exist"
            )

    def to_bytes(self) -> bytes:
        return encode_luabins(self.to_dicts())

    def to_dicts(self) -> List[Dict[Any, Any]]:
        active_state = copy.deepcopy(self.active_state)

        game_state = copy.deepcopy(self.game_state)

        active_state['GameState'] = game_state

        return [
            active_state
        ]
