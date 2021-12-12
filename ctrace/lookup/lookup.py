class LookupDict(dict):
    def __init__(self, normalize_key_fn, normalize_val_fn):
        self.normalize_key_fn = normalize_key_fn
        self.normalize_val_fn = normalize_val_fn
        dict.__init__(self)

    def __getitem__(self, key):
        key = self.normalize_key_fn(key)
        return dict.__getitem__(self, key)

    def __setitem__(self, key, val):
        key = self.normalize_key_fn(key)
        val = self.normalize_val_fn(val)
        dict.__setitem__(self, key, val)


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
