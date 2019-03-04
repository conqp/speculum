"""Filtering functions."""

from argparse import Namespace


__all__ = ['match']


def match(args: Namespace, mirror: dict) -> bool:   # pylint: disable=R0911
    """Filters the respective mirrors."""

    if args.countries is not None:
        country = mirror.get('country')
        match_country = country and country.lower() in args.countries
        country_code = mirror.get('country_code')
        match_code = country_code and country_code.lower() in args.countries

        if not match_country and not match_code:
            return False

    if args.protocols is not None and not mirror['protocol'] in args.protocols:
        return False

    if args.max_age is not None and mirror['age'] > args.max_age:
        return False

    if args.match is not None and not args.match.match(mirror['url']):
        return False

    if args.nomatch is not None and args.nomatch.match(mirror['url']):
        return False

    if args.complete and mirror.get('completion_pct', 0) < 1:
        return False

    if args.active and not mirror.get('active'):
        return False

    if args.ipv4 and not mirror.get('ipv4'):
        return False

    if args.ipv6 and not mirror.get('ipv6'):
        return False

    if args.isos and not mirror.get('isos'):
        return False

    return True
