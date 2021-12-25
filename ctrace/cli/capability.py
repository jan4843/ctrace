from ctrace.lookup import capabilities


def main(query=None):
    if query is None:
        for id_, name in capabilities.names.items():
            print(id_, name)
        return 0

    id_ = None
    try:
        id_ = int(query)
    except ValueError:
        pass
    try:
        if id_ is not None:
            print(capabilities.names[id_])
        else:
            print(capabilities.ids[query])
    except KeyError:
        return 1

    return 0
