# NOTE: ansible doesn't support importing from other files in the plugins dir
#       so we keep all the expanders in the same file to avoid having copies of 
#       the common functions

class FilterModule(object):
  def filters(self):
    return {
      'expand_bandwidths': exp_bandwidths,
      'expand_permissions': exp_permissions,
      'expand_quotas': exp_quotas,
      'expand_rules': exp_rules,
      'expand_users': exp_users
      }

# ---------------------
# ---- Expanders ------
# ---------------------

def exp_permissions(inlist, defaults):
  expandables = [
    {
      'front_name': 'share_dir',
      'back_name': 'name',
      'required': True
    },
    {
      'front_name': 'writable',
      'back_name': 'is_writable',
      'required': False
    },
    {
      'front_name': 'readonly',
      'back_name': 'is_readonly',
      'required': False
    },
    {
      'front_name': 'deny',
      'back_name': 'is_deny',
      'required': False
    },
    {
      'front_name': 'custom',
      'back_name': 'is_custom',
      'required': False
    }
  ]

  return expand_list(inlist, 'permissions', expandables, defaults)

def exp_rules(inlist, defaults):
  expandables = [
    {
      'front_name': 'type',
      'back_name': 'entity_type',
      'required': False
    },
    {
      'front_name': 'entity',
      'back_name': 'entity_name',
      'required': False
    },
    {
      'front_name': 'app',
      'back_name': 'app_id',
      'required': True
    }
  ]

  return expand_list(inlist, 'rules', expandables, defaults)

def exp_quotas(inlist, defaults):
  expandables = [
    {
      'front_name': 'share_dir',
      'back_name': 'share',
      'required': True
    },
    {
      'front_name': 'quota',
      'back_name': 'quota',
      'required': False
    }
  ]

  return expand_list(inlist, 'user_quota', expandables, defaults)

def exp_bandwidths(inlist, defaults):
  expandables = [
    {
      'front_name': 'name',
      'back_name': 'name',
      'required': False
    },
    {
      'front_name': 'upload_result',
      'back_name': 'upload_result',
      'required': False
    },
    {
      'front_name': 'download_result',
      'back_name': 'download_result',
      'required': False
    },
    {
      'front_name': 'upload_limit_1',
      'back_name': 'upload_limit_1',
      'required': False
    },
    {
      'front_name': 'download_limit_1',
      'back_name': 'download_limit_1',
      'required': False
    },
    {
      'front_name': 'upload_limit_2',
      'back_name': 'upload_limit_2',
      'required': False
    },
    {
      'front_name': 'download_limit_2',
      'back_name': 'download_limit_2',
      'required': False
    },
    {
      'front_name': 'policy',
      'back_name': 'policy',
      'required': False
    },
    {
      'front_name': 'protocol',
      'back_name': 'protocol',
      'required': False
    },
    {
      'front_name': 'protocol_ui',
      'back_name': 'protocol_ui',
      'required': False
    },
    {
      'front_name': 'owner_type',
      'back_name': 'owner_type',
      'required': False
    },
    {
      'front_name': 'schedule_plan',
      'back_name': 'schedule_plan',
      'required': False
    }
  ]

  return expand_list(inlist, 'bandwidths', expandables, defaults)

def exp_users(inlist):
  expandables = [
    {
      'front_name': 'name'
    }
  ]

  return expand_list(inlist, 'name', expandables, fmt=['simple'])

# ---------------------
# ----- Common --------
# ---------------------

def expand_list(inlist, keyname, expandables, defaults={}, fmt=[]):
  """[summary]
  Output is a a dictionary of an element that has an array
  of elements each has expandables set to the inlist values
  and for any optional value, revert to the default list.
  Example:
      inlist = [{"name": "abc", "writable": True},{"name":"def", "readonly": False}]
      keyname = "permissions"
      expandables = {"name": "required", "writable": "optional", "readonly": "optional"}
      defaults = {"writable": True, "readonly": True}
  
  Arguments:
      inlist {list(dict)} -- a list of the elements that will be expanded
      keyname {string} -- a string of the output key name
      expandables {list(dict)} -- a list of the expandables names,
                                  each has value that influences how the processing
                                  occurs, ie: optional would fallback to the defaults
                                  and required would not fallback to the defaults
                                  NOTE: an optional value is a fallback-able one
      defaults {dict} -- default values of the optional exapandables
      fmt {list(string)} -- format options that influces the final shape of the output
                            a `simple` formatis one that doesn't have a key
                            just a plain value list

  """
  outstr = "\"{}\": [\n".format(keyname)

  for elem, has_more in lookahead(inlist):
    if ('simple' in fmt):
      outstr += get_simple_elem_str(elem, expandables, defaults)
    else:
      outstr += get_elem_str(elem, expandables, defaults)

    if (has_more):
      outstr += "  ,\n"
    else:
      # last element
      pass

  outstr += "]"
  return outstr

def get_elem_str(elem, expandables, defaults):
  elemstr = "  {\n"

  for expandable, has_more in lookahead(expandables):
    if  expandable['required'] == True:
      value = elem[expandable['front_name']]
      value = quote(value)
      elemstr += "    \"{}\": {}".format(expandable['back_name'], value)

    else:
      if expandable['front_name'] in elem:
        value = elem[expandable['front_name']]
      else:
        value = defaults[expandable['front_name']]

      value = quote(value)
      elemstr += "    \"{}\": {}".format(expandable['back_name'], value)

    if (has_more):
      elemstr += ",\n"
    else:
      # last element
      elemstr += "\n"

  elemstr += "  }\n"

  return elemstr

def get_simple_elem_str(elem, expandables, defaults):
  elemstr = ""

  # NOTE: There should be only one expandable
  for expandable in expandables:
    value = elem[expandable['front_name']]
    value = quote(value)
    elemstr += "    {}".format(value)

  return elemstr


def quote(value):
  if type(value) == bool:
    if (value):
      return "true"
    else:
      return "false"
  elif type(value) == int:
    return value
  else:
    return "\"{}\"".format(value)

def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False