#!/usr/bin/env python
'''Fixme.'''

import logging
import ansible.errors  # NOQA

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


class ModuleResult(dict):

    '''Pass.'''

    def _check_key(self, key):
        if 'results' in self:
            flag = False
            for res in self.get('results', []):
                if isinstance(res, dict):
                    flag |= res.get(key, False)
            return flag
        else:
            return self.get(key, False)

    @property
    def is_changed(self):
        return self._check_key('changed')

    @property
    def is_skipped(self):
        return self._check_key('skipped')

    @property
    def is_failed(self):
        return self._check_key('failed') or self.get('rc', 0) != 0


class AdHocResult(object):

    '''Pass.'''

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        required_kwargs = ('contacted',)
        for kwarg in required_kwargs:
            assert kwarg in kwargs, "Missing required keyword argument '%s'" % kwarg
            setattr(self, kwarg, kwargs.get(kwarg))

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if item in self.contacted:
                return ModuleResult(**self.contacted[item])
            else:
                raise KeyError(item)

    def __getattr__(self, attr):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        # if attr in self.__dict__:
        #     return self.__dict__[attr]
        # else:
        if attr in self.contacted:
            return ModuleResult(**self.contacted[attr])
        else:
            raise AttributeError("type AdHocResult has no attribute '%s'" % attr)

    def __len__(self):
        return len(self.contacted)

    def __contains__(self, item):
        return item in self.contacted

    def keys(self):
        return self.contacted.keys()

    def items(self):
        for k in self.contacted.keys():
            yield (k, getattr(self, k))

    def values(self):
        for k in self.contacted.keys():
            yield getattr(self, k)
