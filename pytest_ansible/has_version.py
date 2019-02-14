import ansible
from pkg_resources import parse_version

has_ansible_v1 = parse_version(ansible.__version__) < parse_version('2.0.0')
has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')
has_ansible_v24 = parse_version(ansible.__version__) >= parse_version('2.4.0')
has_ansible_v28 = parse_version(ansible.__version__) >= parse_version('2.8.0.dev0') \
    or parse_version(ansible.__version__) >= parse_version('2.8.0')
