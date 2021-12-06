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
