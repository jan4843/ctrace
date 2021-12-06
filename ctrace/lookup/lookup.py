from .lookup_dict import LookupDict


class Lookup:
    ids: LookupDict[int, str]
    names: LookupDict[str, int]

    def __init__(self):
        self.ids = LookupDict(self._normalize_name, self._normalize_id)
        self.names = LookupDict(self._normalize_id, self._normalize_name)

    def _normalize_id(self, id_: int):
        return int(id_)

    def _normalize_name(self, name: str):
        return str(name)

    def _add(self, id_: int, name: str):
        self.ids[name] = id_
        self.names[id_] = name
