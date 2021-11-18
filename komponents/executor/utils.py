
def get(obj, key):
    x, *xs = key

    if not xs:
        return obj[x]

    if x not in obj:
        return None

    return get(obj[x], xs)

def set(obj, key, value):
    x, *xs = key

    if not xs:
        obj[x] = value
        return

    if x not in obj:
        obj[x] = {}
    
    set(obj[x], xs, value)
