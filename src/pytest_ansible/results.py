"""Fixme."""


class ModuleResult(dict):
    """Fixme."""

    def _check_key(self, key):
        # if 'results' in self:
        #     for res in self.get('results', []):
        #         if isinstance(res, dict):
        return self.get(key, False)

    @property
    def is_ok(self):
        """Fixme."""
        return not (
            self.is_changed or self.is_unreachable or self.is_skipped or self.is_failed
        )

    @property
    def is_changed(self):
        """Fixme."""
        return self._check_key("changed")

    @property
    def is_unreachable(self):
        """Fixme."""
        return self._check_key("unreachable")

    @property
    def is_skipped(self):
        """Fixme."""
        return self._check_key("skipped")

    @property
    def is_failed(self):
        """Fixme."""
        return self._check_key("failed") or self.get("rc", 0) != 0

    @property
    def is_successful(self):
        """Fixme."""
        return not (self.is_failed or self.is_unreachable)


class AdHocResult:
    """Fixme."""

    def __init__(self, **kwargs) -> None:
        """Fixme."""
        required_kwargs = ("contacted",)
        for kwarg in required_kwargs:
            assert kwarg in kwargs, f"Missing required keyword argument '{kwarg}'"
            setattr(self, kwarg, kwargs.get(kwarg))

    def __getitem__(self, item):
        """Return a ModuleResult instance matching the provided `item`."""
        if item in self.contacted:
            return ModuleResult(**self.contacted[item])
        raise KeyError(item)

    def __getattr__(self, attr):
        """Return a ModuleResult instance matching the provided `attr`."""
        if attr in self.contacted:
            return ModuleResult(**self.contacted[attr])
        msg = f"type AdHocResult has no attribute '{attr}'"
        raise AttributeError(msg)

    def __len__(self) -> int:
        """Return the number of contacted hosts."""
        return len(self.contacted)

    def __contains__(self, item) -> bool:
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
        for k in self.contacted:
            yield (k, getattr(self, k))

    def values(self):
        """Return a list of ModuleResult instances for each contacted inventory host."""
        return [getattr(self, k) for k in self.contacted]
