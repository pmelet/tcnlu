import re, sys

def get(data, path, donepath=[], default=None, transform=None, sep=".", verbose=False):
    if verbose : print >>sys.stderr, path, donepath, 
    if data is None:
        return None
    if type(path) != list:
        path = path.split(sep)
    head, tail = path[0], path[1:]
    sub = None

    m = re.match(r"\[(.*)=(.*)\]", head)
    if m:
        key, value = m.group(1), m.group(2)
        if type(data) == list:
            for item in data:
                if type(item) == dict and item.get(key) == value:
                    sub = item
                    break
        else:
            raise ValueError("%s.%s=%s: type(data) == %s" % (sep.join(donepath), key, value, type(data)))        
    else:
        try:
            head_as_int = int(head)
            if type(data) == list:
                sub = data[head_as_int]
            else:
                raise ValueError("%s.%d: type(data) == %s" % (sep.join(donepath), head_as_int, type(data)))
        except ValueError:
            if type(data) == dict:
                sub = data.get(head)
            else:
                raise ValueError("%s.%s: type(data) == %s" % (sep.join(donepath), head, type(data)))
    if verbose : print >>sys.stderr, "=>", type(sub)
    if len(tail)>0 and sub is not None:
        if verbose : print >>sys.stderr, "recurse"
        sub = get(sub, tail, default=default, donepath=donepath+[head])
        if verbose : print >>sys.stderr, " <= ", sub, default
        if transform:
            try:
                return transform(sub)
            except:
                return default
        return default if sub is None else sub
    if verbose : print >>sys.stderr, "leave", sub, default
    if transform:
        try:
            return transform(sub)
        except:
            return default
    return default if sub is None else sub  


def enforce_list(o):
    if type(o) == list:
        return o
    return [o]


def flatten(list_of_lists, flat_list=[]):
    for item in list_of_lists:
        if type(item) == list:
            flatten(item, flat_list=flat_list)
        else:
            flat_list.append(item)
    return flat_list