"""
Copyright 2025 John Morris

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File: relations.py
Author: John Morris, jhmrrs@clemson.edu, https://orcid.org/0009-0005-6571-1959
Purpose: A list of basic relations employable with edges in the hypergraph.
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

def get_keyword_arguments(args: list, kwargs: dict, excluded_keys: list):
    """Combines all arguments except those with a given key. Returns the arguments 
    for the given keys as a dictionary
    and the remaining arguments as a list.
    
    Note that keys not found in `kwargs` are taken from `args` in the order of the 
    `excluded_keys` list."""
    if not isinstance(excluded_keys, list):
        excluded_keys = [excluded_keys]
    exceptional_vals, to_combine = {}, []

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
    args, kwargs = get_keyword_arguments(args, kwargs, 's1')
    return kwargs['s1'] - sum(args)

def Rdivide(*args, **kwargs):
    """Divides `s1` by all other arguments."""
    args, kwargs = get_keyword_arguments(args, kwargs, 's1')
    s1 = kwargs['s1']
    for s in args:
        s1 /= s
    return s1

def Rceiling(*args, **kwargs):
    """Returns the ceiling of the first argument"""
    args = extend(args, kwargs)
    return np.ceil(args[0])

def Rfloor(*args, **kwargs):
    """Returns the floor of the first argument"""
    args = extend(args, kwargs)
    return np.floor(args[0])

def Rfloor_divide(*args, **kwargs):
    """Returns the largest integer smaller or equal to the division of s1 and s2."""
    args, kwargs = get_keyword_arguments(args, kwargs, ['s1', 's2'])
    return kwargs['s1'] // kwargs['s2']

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

def Rsame(*args, **kwargs):
    """Returns true if all arguments are equivalent."""
    args = set(extend(args, kwargs))
    return len(args) == 1

def mult_and_sum(mult_identifiers: list, sum_identifiers: list):
    """Convenient shorthand for multiplying the values identified in 
    `mult_identifiers` and adding them to the values identified in `sum_identifiers`."""
    if not isinstance(mult_identifiers, list):
        mult_identifiers = [mult_identifiers]
    if not isinstance(sum_identifiers, list):
        sum_identifiers = [sum_identifiers]
    labels = mult_identifiers + sum_identifiers
    def Rmultandsum(*args, **kwargs):
        out = 1.0
        args, kwargs = get_keyword_arguments(args, kwargs, labels)
        for label in mult_identifiers:
            out *= kwargs[label]
        for label in sum_identifiers:
            out += kwargs[label]
        return out
    return Rmultandsum

# BOOLEAN MATH
def Rall(*args, **kwargs):
    """Returns true if all arguments are true."""
    args = extend(args, kwargs)
    return all(args)

def Rany(*args, **kwargs):
    """Returns true if any of the arguments are true."""
    args = extend(args, kwargs)
    return any(args)

def Rxor(*args, **kwargs):
    """Returns true if only one of the arguments is true."""
    args = [a for a in extend(args, kwargs) if isinstance(a, bool)]
    return sum(args) == 1

def Rnot_any(*args, **kwargs):
    """Returns true if none of the arguments are true."""
    args = extend(args, kwargs)
    return not any(args)

def Rnot(*args, **kwargs):
    """Returns the logical negation of the first boolean argument."""
    args = extend(args, kwargs)
    for a in args:
        if isinstance(a, bool):
            return not a
    return not args[0]

# OPERATIONS
def Rincrement(*args, **kwargs):
    """Increments the maximum source by 1."""
    args = extend(args, kwargs)
    return max(args) + 1

def Rfirst(*args, **kwargs):
    """Returns the first argument."""
    args, kwargs = get_keyword_arguments(args, kwargs, 's1')
    return kwargs['s1']

def equal(identifier: str):
    """Returns a method that returns the argument with the same keyword as 
    `identifier`."""
    def Requal(*args, **kwargs):
        args, kwargs = get_keyword_arguments(args, kwargs, identifier)
        return kwargs[identifier]
    return Requal

def geq(identifier: str, val: int):
    """Returns a method that returns True if the identifier is greater than or equal 
    to `val`."""
    def Rcyclecounter(*args, **kwargs):
        args, kwargs = get_keyword_arguments(args, kwargs, identifier)
        return kwargs[identifier] >= val
    return Rcyclecounter

# TRIGONOMETRY
def Rsin(*args, **kwargs):
    """Returns the sine of the mean of all arguments."""
    args = extend(args, kwargs)
    return np.sin(np.mean(args))

def Rcos(*args, **kwargs):
    """Returns the cosine of the mean of all arguments."""
    args = extend(args, kwargs)
    return np.cos(np.mean(args))

def Rtan(*args, **kwargs):
    """Returns the tangent of the mean of all arguments."""
    args = extend(args, kwargs)
    return np.tan(np.mean(args))

# Types
def Rlist(*args, **kwargs):
    """Returns a list of all node values in the order specified."""
    out = extend(args, kwargs)
    return out

def Rtuple(*args, **kwargs):
    """Returns a tuple of all node values in the order specified."""
    out = extend(args, kwargs)
    out = tuple(out)
    return out

def Rdict(*args, **kwargs):
    """Returns a dictionary with either the keyed argument `key` or the first argument 
    as the dict key."""
    args, kwargs = get_keyword_arguments(args, kwargs, 'key')
    key = kwargs.get['key', None]
    if key is None:
        key = args.pop[-1]
    if len(args) == 1:
        out = {key: args[0]}
    else:
        out = {key: args}
    return out
