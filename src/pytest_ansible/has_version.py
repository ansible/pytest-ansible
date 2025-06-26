"""Fixme."""

from __future__ import annotations

import ansible

from packaging.version import parse as parse_version


has_ansible_v2 = parse_version(ansible.__version__) >= parse_version("2.0.0")
has_ansible_v24 = parse_version(ansible.__version__) >= parse_version("2.4.0")
has_ansible_v28 = parse_version(ansible.__version__) >= parse_version("2.8.0.dev0")
has_ansible_v29 = parse_version(ansible.__version__) >= parse_version("2.9.0")
has_ansible_v212 = parse_version(ansible.__version__) >= parse_version("2.12.0")
has_ansible_v213 = parse_version(ansible.__version__) >= parse_version("2.13.0")
has_ansible_v219 = parse_version(ansible.__version__) >= parse_version("2.19.0.dev0")
