#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def parse_requirements(requirements, ignore=('setuptools',)):
    """Read dependencies from file and strip off version numbers.

    Supports extra requirements and '>=' and '<=' version qualifiers.
    """
    with open(requirements) as f:
        packages = set()
        for line in f:
            line = line.strip()
            if not line or line.startswith(('#', '-r', '--')):
                continue

            # XXX: Ugly hack!
            extras = []
            def get_extras(match):
                extras.append(match.group(1))

            line = re.sub(r'\s*\[(.*?)\]', get_extras, line)

            if '#egg=' in line:
                line = line.split('#egg=')[1]

            pkg = re.split('[=<>]=', line)[0].strip()

            if pkg not in ignore:
                if extras:
                    pkg = 'pkg [%s]' % extras[0]
                packages.add(pkg)

        return tuple(packages)


if __name__ == '__main__':
    import sys
    print("\n".join(sorted(parse_requirements(
        sys.argv[1] if sys.argv[1:] else 'requirements.txt'))))
