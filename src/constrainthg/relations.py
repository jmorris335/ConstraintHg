"""
File: relations.py
Author: John Morris, jhmrrs@clemson.edu, https://orcid.org/0009-0005-6571-1959
Purpose: A list of basic relations employable with edges in the hypergraph.
License: All rights reserved.
Versions:
- 0.0, 7 Oct. 2024: initialized
Notes:
- Generally imported as import relations as R
- All relationship functions begin with a capital R, so that they are normally called 
as `R.Rfunction`
- Each relationships should have *args, and **kwargs as its arguments and only 
arguments. Specific keywords referenced in kwargs should be `s1`, `s2`, ... only.
"""

import numpy as np

# AUX FUNCTIONS
def extend(args: list, kwargs: dict)-> list:
    """Combines all arguments into a single list, with args leading."""
    return list(args) + list(kwargs.values())

def getKeywordArguments(args: list, kwargs: dict, excluded_keys: list):
    """Combines all arguments except those with a given key. Returns the arguments 
    for the given keys as a dictionary
    and the remaining arguments as a list.
    
    Note that keys not found in `kwargs` are taken from `args` in the order of the 
    `excluded_keys` list."""
    if not isinstance(excluded_keys, list):
        excluded_keys = [excluded_keys]
    exceptional_vals, to_combine = dict(), list()

    for key, val in kwargs.items():
        if key in excluded_keys:
            exceptional_vals[key] = val
        else:
            to_combine.append(val)

    i = 0
    for key in excluded_keys:
        if key not in exceptional_vals:
            exceptional_vals[key] = args[i]
            i += 1

    to_combine += list(args[i:]) 
    return to_combine, exceptional_vals

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
    args, kwargs = getKeywordArguments(args, kwargs, 's1')
    return kwargs['s1'] - sum(args)
    
def Rdivide(*args, **kwargs):
    """Divides `s1` by all other arguments."""
    args, kwargs = getKeywordArguments(args, kwargs, 's1')
    s1 = kwargs['s1']
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

def Rmax(*args, **kwargs):
    """Returns the maximum of all arguments."""
    args = extend(args, kwargs)
    return max(args)

def Rmin(*args, **kwargs):
    """Returns the minimum of all arguments."""
    args = extend(args, kwargs)
    return min(args)


# OPERATIONS
def Rincrement(*args, **kwargs):
    """Increments the maximum source by 1."""
    args = extend(args, kwargs)
    return max(args) + 1

def Rfirst(*args, **kwargs):
    """Returns the first argument."""
    args, kwargs = getKeywordArguments(args, kwargs, 's1')
    return kwargs['s1']

def equal(identifier: str):
    """Returns the a method that returns the argument with the same keyword as 
    `identifier`."""
    def Requal(*args, **kwargs):
        args, kwargs = getKeywordArguments(args, kwargs, identifier)
        return kwargs[identifier]
    return Requal

# TRIGONOMETRY
def Rsin(*args, **kwargs):
    """Returns the sine of the mean of all arguments."""
    args = extend(args, kwargs)
    return np.sin(np.mean(args))


if __name__ == '__main__':
    a = Rsubtract(4, s1=10)
    print(a)