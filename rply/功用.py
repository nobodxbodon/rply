import sys

if sys.version_info >= (3, 3):
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


class IdentityDict(MutableMapping):
    def __init__(自身):
        自身._contents = {}
        自身._keepalive = []

    def __getitem__(自身, key):
        return 自身._contents[id(key)][1]

    def __setitem__(自身, key, value):
        idx = len(自身._keepalive)
        自身._keepalive.append(key)
        自身._contents[id(key)] = key, value, idx

    def __delitem__(自身, key):
        del 自身._contents[id(key)]
        for idx, obj in enumerate(自身._keepalive):
            if obj is key:
                del 自身._keepalive[idx]
                break

    def __len__(自身):
        return len(自身._contents)

    def __iter__(自身):
        for key, _, _ in itervalues(自身._contents):
            yield key


class Counter(object):
    def __init__(自身):
        自身.value = 0

    def incr(自身):
        自身.value += 1


if sys.version_info >= (3,):
    def itervalues(d):
        return d.values()

    def iteritems(d):
        return d.items()
else:
    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()
