# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2015 Online SAS and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@ocs.online.net>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

u""" Utilities to normalize and reconcile territory codes.

.. data:: COUNTRY_ALIASES

.. data:: SUBDIVISION_ALIASES

   Map subdivision ISO 3166-2 codes to their officially assigned ISO 3166-1
   alpha-2 country codes. Source: https://en.wikipedia.org/wiki
   /ISO_3166-2#Subdivisions_included_in_ISO_3166-1

.. data:: REVERSE_MAPPING

   Reverse index of the SUBDIVISION_ALIASES mapping defined above.
"""

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

from itertools import chain
from operator import attrgetter
import warnings

from pycountry import countries, subdivisions

try:
    from itertools import imap
except ImportError:  # pragma: no cover
    imap = map


COUNTRY_ALIASES = {
    # Source:
    # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Exceptional_reservations
    'AC': 'SH-AC',  # Ascension Island
    'CP': 'FR-CP',  # Clipperton Island
    'DG': 'IO',     # Diego Garcia
    # 'EA': ['ES-ML', 'ES-CE'],  # Ceuta and Melilla
    'FX': 'FR',     # France, Metropolitan
    'IC': 'ES-CN',  # Canary Islands
    'TA': 'SH-TA',  # Tristan da Cunha
    # European Commision country code exceptions.
    # Source: http://publications.europa.eu/code/pdf/370000en.htm#pays
    'UK': 'GB',  # United Kingdom
    'EL': 'GR',  # Greece
}


SUBDIVISION_ALIASES = {
    'CN-71': 'TW',  # Taiwan
    'CN-91': 'HK',  # Hong Kong
    'CN-92': 'MO',  # Macao
    'FI-01': 'AX',  # Åland
    'FR-BL': 'BL',  # Saint Barthélemy
    'FR-GF': 'GF',  # French Guiana
    'FR-GP': 'GP',  # Guadeloupe
    'FR-MF': 'MF',  # Saint Martin
    'FR-MQ': 'MQ',  # Martinique
    'FR-NC': 'NC',  # New Caledonia
    'FR-PF': 'PF',  # French Polynesia
    'FR-PM': 'PM',  # Saint Pierre and Miquelon
    'FR-RE': 'RE',  # Réunion
    'FR-TF': 'TF',  # French Southern Territories
    'FR-WF': 'WF',  # Wallis and Futuna
    'FR-YT': 'YT',  # Mayotte
    'NL-AW': 'AW',  # Aruba
    'NL-BQ1': 'BQ-BO',  # Bonaire
    'NL-BQ2': 'BQ-SA',  # Saba
    'NL-BQ3': 'BQ-SE',  # Sint Eustatius
    'NL-CW': 'CW',  # Curaçao
    'NL-SX': 'SX',  # Sint Maarten
    'NO-21': 'SJ',  # Svalbard
    'NO-22': 'SJ',  # Jan Mayen
    'US-AS': 'AS',  # American Samoa
    'US-GU': 'GU',  # Guam
    'US-MP': 'MP',  # Northern Mariana Islands
    'US-PR': 'PR',  # Puerto Rico
    'US-UM': 'UM',  # United States Minor Outlying Islands
    'US-VI': 'VI',  # Virgin Islands, U.S.
}


# Build the reverse index of aliases defined above.
REVERSE_MAPPING = {}
for mapping in [COUNTRY_ALIASES, SUBDIVISION_ALIASES]:
    for alias_code, target_code in mapping.items():
        REVERSE_MAPPING.setdefault(target_code, set()).add(alias_code)


def supported_territory_codes():
    """ Return a set of recognized territory codes.

    Are supported:
        * ISO 3166-1 alpha-2 country codes
        * ISO 3166-2 subdivision codes
    """
    return set(chain(
        imap(attrgetter('alpha2'), countries),
        imap(attrgetter('code'), subdivisions),
        COUNTRY_ALIASES.keys()))


def normalize_territory_code(territory_code, resolve_aliases=True):
    """ Normalize any string into a territory code. """
    territory_code = territory_code.strip().upper()
    if territory_code not in supported_territory_codes():
        raise ValueError(
            'Unrecognized {!r} territory code.'.format(territory_code))
    if resolve_aliases:
        territory_code = COUNTRY_ALIASES.get(territory_code, territory_code)
        territory_code = SUBDIVISION_ALIASES.get(
            territory_code, territory_code)
    return territory_code


def normalize_country_code(subdivision_code):
    """ Return the normalized country code from a subdivision code.

    If no country is found, or the subdivision code is incorrect, ``None`` is
    returned.

    For subdivisions having their own ISO 3166-1 alpha-2 country code, returns
    the later instead of the parent ISO 3166-2 top entry.

    .. deprecated:: 0.3.0

       Use country_from_subdivision instead.
    """
    warnings.warn('Please use country_from_subdivision', DeprecationWarning)
    return country_from_subdivision(subdivision_code)


def country_from_subdivision(subdivision_code):
    """ Return the normalized country code from a subdivision code.

    If no country is found, or the subdivision code is incorrect, ``None`` is
    returned.

    For subdivisions having their own ISO 3166-1 alpha-2 country code, returns
    the later instead of the parent ISO 3166-2 top entry.
    """
    # Resolve subdivision alias.
    code = SUBDIVISION_ALIASES.get(subdivision_code, subdivision_code)

    # We have a country code, return it right away.
    if code in imap(attrgetter('alpha2'), countries):
        return code

    # Try to extract country code from subdivision.
    try:
        subdiv = subdivisions.get(code=code)
    except KeyError:
        return None
    return subdiv.country_code


def default_subdivision_code(country_code):
    """ Return the default subdivision code of a country.

    The result can be guessed only if there is a 1:1 mapping between a country
    code and a subdivision code.
    """
    # Build the reverse index of the subdivision/country alias mapping.
    default_subdiv = {}
    for subdiv_code, alias_code in SUBDIVISION_ALIASES.items():
        # Skip non-country
        if len(alias_code) == 2:
            default_subdiv.setdefault(alias_code, set()).add(subdiv_code)

    # Include countries directly mapping to a subdivision.
    for alias_code, subdiv_code in COUNTRY_ALIASES.items():
        # Skip non-subdiv
        if len(subdiv_code) > 3:
            default_subdiv.setdefault(alias_code, set()).add(subdiv_code)

    default_subdivisions = default_subdiv.get(country_code)
    if default_subdivisions and len(default_subdivisions) == 1:
        return default_subdivisions.pop()


def territory_tree(territory_code, include_country=True):
    """ Return the whole hierarchy of territories, up to the country.

    Values returned by the generator are either subdivisions or country
    objects, starting from the provided subdivision and up its way to
    the top administrative territory (i.e. country).

    .. deprecated:: 0.1.0

       Use territory_parents instead.
    """
    warnings.warn('Please use territory_parents', DeprecationWarning)
    return territory_parents(territory_code, include_country)


def territory_parents(territory_code, include_country=True):
    """ Return the whole hierarchy of territories, up to the country.

    Values returned by the generator are either subdivisions or country
    objects, starting from the provided territory and up its way to the top
    administrative territory (i.e. country).
    """
    tree = []

    # If the provided territory code is a country, return it right away.
    territory_code = normalize_territory_code(territory_code)
    if territory_code in imap(attrgetter('alpha2'), countries):
        if include_country:
            tree.append(countries.get(alpha2=territory_code))
        return tree

    # Else, resolve the territory as if it's a subdivision code.
    subdivision_code = territory_code
    while subdivision_code:
        subdiv = subdivisions.get(code=subdivision_code)
        tree.append(subdiv)
        if not subdiv.parent_code:
            break
        subdivision_code = subdiv.parent_code

    # Return country
    if include_country:
        tree.append(subdivisions.get(code=subdivision_code).country)

    return tree


def territory_parents_codes(territory_code, include_country=True):
    """ Like territory_parents but return normalized codes instead of objects.
    """
    for territory in territory_parents(
            territory_code, include_country=include_country):
        full_class_name = '{}.{}'.format(
            territory.__module__, territory.__class__.__name__)
        if full_class_name == 'pycountry.db.Country':
            yield territory.alpha2
        elif full_class_name == 'pycountry.db.Subdivision':
            yield territory.code
        else:
            raise "Unrecognized {!r} territory.".format(territory)


def country_aliases(territory_code):
    """ List valid country code aliases of a territory.

    Mainly used to check if a non-normalized country code can safely be
    replaced by its normalized form.
    """
    country_codes = set()

    # Add a country code right away in our aliases.
    if territory_code in imap(attrgetter('alpha2'), countries):
        country_codes.add(territory_code)

    # A subdivision code triggers a walk along the non-normalized parent tree
    # and look for aliases at each level.
    else:
        subdiv = subdivisions.get(code=territory_code)
        parent_code = subdiv.parent_code
        if not parent_code:
            parent_code = subdiv.country.alpha2
        country_codes.update(country_aliases(parent_code))

    # Hunt for aliases
    for mapped_code in REVERSE_MAPPING.get(territory_code, []):
        country_codes.update(country_aliases(mapped_code))

    return country_codes
