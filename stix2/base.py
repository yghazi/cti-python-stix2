"""Base class for type definitions in the stix2 library."""

import collections
import datetime as dt
import json
import uuid

from .utils import format_datetime, get_timestamp, NOW

__all__ = ['STIXJSONEncoder', '_STIXBase']

DEFAULT_ERROR = "{type} must have {field}='{expected}'."


class STIXJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (dt.date, dt.datetime)):
            return format_datetime(obj)
        elif isinstance(obj, _STIXBase):
            return dict(obj)
        else:
            return super(STIXJSONEncoder, self).default(obj)


def get_required_properties(properties):
    for k, v in properties.items():
        if isinstance(v, dict):
            if v.get('required'):
                yield k
        else:  # This is a Property subclass
            if v.required:
                yield k


class _STIXBase(collections.Mapping):
    """Base class for STIX object types"""

    # TODO: remove this
    def _handle_old_style_property(self, prop_name, prop_metadata, kwargs):
        cls = self.__class__
        class_name = cls.__name__

        if prop_name not in kwargs:
            if prop_metadata.get('default'):
                default = prop_metadata['default']
                if default == NOW:
                    kwargs[prop_name] = self.__now

        if prop_metadata.get('validate'):
            if (prop_name in kwargs and
                    not prop_metadata['validate'](cls, kwargs[prop_name])):
                msg = prop_metadata.get('error_msg', DEFAULT_ERROR).format(
                    type=class_name,
                    field=prop_name,
                    expected=prop_metadata.get('expected',
                                               prop_metadata.get('default', lambda x: ''))(cls),
                )
                raise ValueError(msg)

    def _check_property(self, prop_name, prop, kwargs):
        if prop_name not in kwargs:
            if hasattr(prop, 'default'):
                kwargs[prop_name] = prop.default()
            # if default == NOW:
            #     kwargs[prop_name] = self.__now

        if prop_name in kwargs:
            try:
                kwargs[prop_name] = prop.validate(kwargs[prop_name])
            except ValueError as exc:
                msg = "Invalid value for {0} '{1}': {2}"
                raise ValueError(msg.format(self.__class__.__name__,
                                            prop_name,
                                            exc))

    def __init__(self, **kwargs):
        cls = self.__class__
        class_name = cls.__name__

        # Use the same timestamp for any auto-generated datetimes
        self.__now = get_timestamp()

        # Detect any keyword arguments not allowed for a specific type
        extra_kwargs = list(set(kwargs) - set(cls._properties))
        if extra_kwargs:
            raise TypeError("unexpected keyword arguments: " + str(extra_kwargs))

        required_fields = get_required_properties(cls._properties)
        missing_kwargs = set(required_fields) - set(kwargs)
        if missing_kwargs:
            msg = "Missing required field(s) for {type}: ({fields})."
            field_list = ", ".join(x for x in sorted(list(missing_kwargs)))
            raise ValueError(msg.format(type=class_name, fields=field_list))

        for prop_name, prop_metadata in cls._properties.items():

            if isinstance(prop_metadata, dict):
                self._handle_old_style_property(prop_name, prop_metadata, kwargs)
            else:  # This is a Property Subclasses
                self._check_property(prop_name, prop_metadata, kwargs)

        self._inner = kwargs

    def __getitem__(self, key):
        return self._inner[key]

    def __iter__(self):
        return iter(self._inner)

    def __len__(self):
        return len(self._inner)

    # Handle attribute access just like key access
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        if name != '_inner' and not name.startswith("_STIXBase__"):
            print(name)
            raise ValueError("Cannot modify properties after creation.")
        super(_STIXBase, self).__setattr__(name, value)

    def __str__(self):
        # TODO: put keys in specific order. Probably need custom JSON encoder.
        return json.dumps(self, indent=4, sort_keys=True, cls=STIXJSONEncoder,
                          separators=(",", ": "))  # Don't include spaces after commas.

    def __repr__(self):
        props = [(k, self[k]) for k in sorted(self._properties) if self.get(k)]
        return "{0}({1})".format(self.__class__.__name__,
                                 ", ".join(["{0!s}={1!r}".format(k, v) for k, v in props]))
