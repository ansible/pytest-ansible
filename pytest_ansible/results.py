"""Fixme."""

import ansible.errors  # NOQA
from pytest_ansible.logger import get_logger

log = get_logger(__name__)


class ModuleResult(dict):

    """Fixme."""

    def _check_key(self, key):
        # if 'results' in self:
        #     flag = False
        #     for res in self.get('results', []):
        #         if isinstance(res, dict):
        #             flag |= res.get(key, False)
        #     return flag
        # else:
        return self.get(key, False)

    @property
    def is_ok(self):
        return not (self.is_changed or self.is_unreachable or self.is_skipped or self.is_failed)

    @property
    def is_changed(self):
        return self._check_key('changed')

    @property
    def is_unreachable(self):
        return self._check_key('unreachable')

    @property
    def is_skipped(self):
        return self._check_key('skipped')

    @property
    def is_failed(self):
        return self._check_key('failed') or self.get('rc', 0) != 0

    @property
    def is_successful(self):
        return not (self.is_failed or self.is_unreachable)


class AdHocResult(object):

    """Fixme."""

    def __init__(self, **kwargs):
        """Fixme."""
        required_kwargs = ('contacted',)
        for kwarg in required_kwargs:
            assert kwarg in kwargs, "Missing required keyword argument '%s'" % kwarg
            setattr(self, kwarg, kwargs.get(kwarg))

    def __getitem__(self, item):
        """Return a ModuleResult instance matching the provided `item`."""
        if item in self.contacted:
            return ModuleResult(**self.contacted[item])
        else:
            raise KeyError(item)

    def __getattr__(self, attr):
        """Return a ModuleResult instance matching the provided `attr`."""
        if attr in self.contacted:
            return ModuleResult(**self.contacted[attr])
        else:
            raise AttributeError("type AdHocResult has no attribute '%s'" % attr)

    def __len__(self):
        """Return the number of contacted hosts."""
        return len(self.contacted)

    def __contains__(self, item):
        """Return whether the provided `item` was contacted."""
        return item in self.contacted

    def __iter__(self):
        """Return an iterator of the contacted inventory hosts."""
        return iter(self.contacted)

    def keys(self):
        """Return a list of contacted inventory hosts."""
        return self.contacted.keys()

    def items(self):
        """Return a list of tuples containing the inventory host key, and the ModuleResult instance."""
        for k in self.contacted.keys():
            yield (k, getattr(self, k))

    def values(self):
        """Return a list of ModuleResult instances for each contacted inventory host."""
        return [getattr(self, k) for k in self.contacted.keys()]
