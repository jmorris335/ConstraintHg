"""
File: relations.py
Author: John Morris, jhmrrs@clemson.edu, https://orcid.org/0009-0005-6571-1959
Purpose: A list of basic relations employable with edges in the hypergraph.
License: All rights reserved.
Versions:
- 0.0, 7 Oct. 2024: initialized
Notes:
- Generally imported as import relations as R
- All relationship functions begin with a capital R, so that they are normally called as `R.Rfunction`
- Each relationships should have *args, and **kwargs as its arguments and only arguments. Specific keywords referenced in kwargs should be `s1`, `s2`, ... only.
"""

import numpy as np

# AUX FUNCTIONS
def extend(args: list, kwargs: dict)-> list:
    """Combines all arguments into a single list, with args leading."""
    return list(args) + list(kwargs.values())

def extendWithExceptions(args: list, kwargs: dict, excluded_keys: list):
    """Combines all arguments except those with a given key."""
    if not isinstance(excluded_keys, list):
        excluded_keys = [excluded_keys]
    args = list(args) + [kwargs[key] for key in kwargs if key in excluded_keys]
    return args

# ALGEBRAIC RELATIONS
def Rsum(*args, **kwargs):
    """Sums all arguments."""
    args = extend(args, kwargs)
    return sum(args)

def Rmultiply(*args, **kwargs):
    """Multiplies all arguments together."""
    args = extend(args, kwargs)
    out = 1
    for s in args:
        out *= s
    return out

def Rsubtract(*args, **kwargs):
    """Subtracts from `s1` all other arguments."""
    args = extendWithExceptions(args, kwargs, 's1')
    if 's1' in kwargs:
        return kwargs['s1'] - sum(args)
    else:
        return args[0] - sum(args[1:])
    
def Rdivide(*args, **kwargs):
    """Divides `s1` by all other arguments."""
    args = extendWithExceptions(args, kwargs, 's1')
    if 's1' in kwargs:
        s1 = kwargs['s1']
    else:
        s1 = args[0]
        args = args[1:]
    for s in args:
        s1 /= s
    return s1

def Rnegate(*args, **kwargs):
    """Returns the negative of the first argument."""
    args = extend(args, kwargs)
    return -args[0]

def Rinvert(*args, **kwargs):
    """Inverts the first argument."""
    args = extend(args, kwargs)
    return 1 / args[0]

def Rmean(*args, **kwargs):
    """Returns the mean of all arguments."""
    args = extend(args, kwargs)
    return np.mean(args)

# OPERATIONS
def Rincrement(*args, **kwargs):
    """Increments the maximum source by 1."""
    args = extend(args, kwargs)
    return max(args) + 1

if __name__ == '__main__':
    a = Rsubtract(4, s1=10)
    print(a)