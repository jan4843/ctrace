from ctrace.lookup import syscalls


def main(query=None):
    if query is None:
        for id_, name in syscalls.names.items():
            print(id_, name)
        return 0

    id_ = None
    try:
        id_ = int(query)
    except ValueError:
        pass
    try:
        if id_ is not None:
            print(syscalls.names[id_])
        else:
            print(syscalls.ids[query])
    except KeyError:
        return 1

    return 0
