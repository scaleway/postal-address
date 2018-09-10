# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2018 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

import re
import unittest
from operator import attrgetter

from pycountry import countries, subdivisions

from postal_address.address import (
    Address,
    subdivision_metadata,
    subdivision_type_id
)
from postal_address.territory import (
    COUNTRY_ALIASES,
    SUBDIVISION_COUNTRIES,
    country_aliases,
    country_from_subdivision,
    default_subdivision_code,
    normalize_territory_code,
    supported_country_codes,
    supported_subdivision_codes,
    supported_territory_codes,
    territory_attachment,
    territory_children_codes,
    territory_parents_codes,
    FOREIGN_TERRITORIES_MAPPING, RESERVED_COUNTRY_CODES)

PYCOUNTRY_CC = set(map(attrgetter('alpha_2'), countries))
PYCOUNTRY_SUB = set(map(attrgetter('code'), subdivisions))


class TestTerritory(unittest.TestCase):
    # Test territory utils

    def test_supported_territory_codes(self):
        self.assertIn('FR', supported_territory_codes())
        self.assertIn('FR-59', supported_territory_codes())
        self.assertNotIn('FRE', supported_territory_codes())

    def test_supported_country_codes(self):
        self.assertIn('FR', supported_country_codes())
        self.assertIn('FX', supported_country_codes())
        self.assertIn('UK', supported_country_codes())
        self.assertNotIn('FR-59', supported_country_codes())

    def test_supported_subdivision_codes(self):
        self.assertIn('FR-59', supported_subdivision_codes())
        self.assertNotIn('FR', supported_subdivision_codes())
        self.assertNotIn('UK', supported_subdivision_codes())

    def test_territory_code_overlap(self):
        # Check that all codes from each classifications we rely on are not
        # overlapping.
        self.assertFalse(PYCOUNTRY_CC.intersection(PYCOUNTRY_SUB))

    def test_foreign_territory_definition(self):
        for foreign, country in FOREIGN_TERRITORIES_MAPPING.items():
            self.assertIn(foreign, PYCOUNTRY_CC)
            self.assertIn(country, PYCOUNTRY_CC)

    def test_territory_exception_definition(self):
        # Check that all codes used in constants to define exceptional
        # treatment are valid and recognized.
        for subdiv_code, alias_code in SUBDIVISION_COUNTRIES.items():
            self.assertIn(subdiv_code, supported_subdivision_codes())
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            self.assertIn(alias_code, PYCOUNTRY_CC.union(PYCOUNTRY_SUB))

        for country_code, alias_code in COUNTRY_ALIASES.items():
            # Aliased country codes are not supposed to be supported by
            # pycountry, as it's the main reason to define an alias in the
            # first place.
            self.assertNotIn(country_code, PYCOUNTRY_CC)
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            self.assertIn(alias_code, PYCOUNTRY_CC.union(PYCOUNTRY_SUB))

        for country_code, alias_code in RESERVED_COUNTRY_CODES.items():
            self.assertNotIn(country_code, PYCOUNTRY_CC)
            self.assertIn(alias_code, PYCOUNTRY_CC.union(PYCOUNTRY_SUB))

    def test_country_from_subdivision(self):
        # Test reconciliation of ISO 3166-2 and ISO 3166-1 country codes.
        for subdiv_code in SUBDIVISION_COUNTRIES.keys():
            target_code = SUBDIVISION_COUNTRIES[subdiv_code]
            if len(target_code) != 2:
                target_code = subdivisions.get(code=target_code).country_code
            self.assertEquals(
                country_from_subdivision(subdiv_code), target_code)
        for subdiv_code in PYCOUNTRY_SUB.difference(SUBDIVISION_COUNTRIES):
            self.assertEquals(
                country_from_subdivision(subdiv_code),
                subdivisions.get(code=subdiv_code).country_code)

    def test_default_subdivision_code(self):
        self.assertEquals(default_subdivision_code('FR'), None)
        self.assertEquals(default_subdivision_code('GU'), 'US-GU')
        self.assertEquals(default_subdivision_code('SJ'), None)

    def test_territory_children_codes(self):
        self.assertEquals(territory_children_codes('GQ'),
                          {'GQ-C', 'GQ-I', 'GQ-AN', 'GQ-BN', 'GQ-BS', 'GQ-CS',
                           'GQ-KN', 'GQ-LI', 'GQ-WN'})
        self.assertEquals(territory_children_codes('GQ-I'),
                          {'GQ-AN', 'GQ-BN', 'GQ-BS'})
        self.assertEquals(territory_children_codes('GQ-AN'), set())
        self.assertEquals(territory_children_codes(
            'GQ-AN', include_self=True), {'GQ-AN'})

    def test_territory_parents_codes(self):
        self.assertEquals(
            list(territory_parents_codes('FR-59')),
            ['FR-59', 'FR-HDF', 'FR'])
        self.assertEquals(
            list(territory_parents_codes('FR-59', include_country=False)),
            ['FR-59', 'FR-HDF'])
        self.assertEquals(
            list(territory_parents_codes('FR')),
            ['FR'])
        self.assertEquals(
            list(territory_parents_codes('FR', include_country=False)),
            [])

    def test_alias_normalization(self):
        # Check country alias to a country.
        self.assertEquals(
            list(territory_parents_codes('DG')),
            ['IO'])

        # Check country alias to a subdivision.
        self.assertEquals(
            list(territory_parents_codes('SH-TA')),
            ['SH-TA', 'SH'])
        self.assertEquals(
            list(territory_parents_codes('TA')),
            ['SH-TA', 'SH'])

        # Check subdivision alias to a country.
        self.assertEquals(
            list(territory_parents_codes('MQ')),
            ['MQ'])
        self.assertEquals(
            list(territory_parents_codes('FR-MQ')),
            ['MQ'])

        # Check subdivision alias to a subdivision.
        self.assertEquals(
            list(territory_parents_codes('BQ-SE')),
            ['BQ-SE', 'BQ'])
        self.assertEquals(
            list(territory_parents_codes('NL-BQ3')),
            ['BQ-SE', 'BQ'])

        # Non 1:1 alias mapping should be non-destructive and keep the
        # subdivision.
        # self.assertEquals(
        #     list(territory_parents_codes('NO-22')),
        #     ['NO-22', 'SJ'])

    def test_country_aliases(self):
        self.assertEquals(country_aliases('UM-67'), {'US', 'UM'})
        self.assertEquals(country_aliases('UM'), {'US', 'UM'})
        self.assertEquals(country_aliases('US'), {'US'})

        self.assertEquals(country_aliases('BQ-BO'), {'NL', 'BQ'})
        self.assertEquals(country_aliases('NL-BQ2'), {'NL', 'BQ'})

        self.assertEquals(country_aliases('NO-21'), {'SJ', 'NO'})

        self.assertEquals(country_aliases('DG'), {'DG', 'IO', 'GB'})
        self.assertEquals(country_aliases('IO'), {'IO', 'GB'})

        self.assertEquals(country_aliases('FR'), {'FR'})

        # CP is not an official ISO-3166 country code
        # self.assertEquals(country_aliases('FR-CP'), {'FR', 'CP'})
        # self.assertEquals(country_aliases('CP'), {'FR', 'CP'})

        self.assertEquals(country_aliases('FR-RE'), {'FR', 'RE'})
        self.assertEquals(country_aliases('RE'), {'FR', 'RE'})

        self.assertEquals(country_aliases('GB'), {'GB'})
        self.assertEquals(country_aliases('UK'), {'UK', 'GB'})

        self.assertEquals(country_aliases('GR'), {'GR'})
        self.assertEquals(country_aliases('EL'), {'EL', 'GR'})

        self.assertEquals(country_aliases('IM'), {'IM', 'GB'})

        self.assertEquals(country_aliases('MC'), {'MC'})

    def test_subdivision_type_id_conversion(self):
        # Conversion of subdivision types into IDs must be python friendly
        attribute_regexp = re.compile('[a-z][a-z0-9_]*$')
        for subdiv in subdivisions:
            self.assertTrue(attribute_regexp.match(
                subdivision_type_id(subdiv)))

    def test_subdivision_type_id_city_classification(self):
        city_like_subdivisions = [
            'TM-S',  # Aşgabat, Turkmenistan, City
            'TW-CYI',  # Chiay City, Taiwan, Municipality
            'TW-TPE',  # Taipei City, Taiwan, Special Municipality
            'ES-ML',  # Melilla, Spain, Autonomous city
            'GB-LND',  # City of London, United Kingdom, City corporation
            'KP-01',  # P’yŏngyang, North Korea, Capital city
            'KP-13',  # Nasŏn (Najin-Sŏnbong), North Korea, Special city
            'KR-11',  # Seoul Teugbyeolsi, South Korea, Capital Metropolitan
            # City
            'HU-HV',  # Hódmezővásárhely, Hungary, City with county rights
            'LV-RIX',  # Rīga, Latvia, Republican City
            'ME-15',  # Plužine, Montenegro, Municipality
            'NL-BQ1',  # Bonaire, Netherlands, Special municipality
            'KH-12',  # Phnom Penh, Cambodia, Autonomous municipality
        ]
        for subdiv_code in city_like_subdivisions:
            self.assertEquals(
                subdivision_type_id(subdivisions.get(code=subdiv_code)),
                'city')

    def test_subdivision_type_id_collision(self):
        # The subdivision metadata IDs we derived from subdivision types should
        # not collide with Address class internals.
        simple_address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR')

        # Check each subdivision metadata.
        for subdiv in subdivisions:

            # XXX ISO 3166-2 reuse the country type as subdivisions.
            # We really need to add proper support for these cases, as we did
            # for cities.
            if subdivision_type_id(subdiv) in ['country']:
                continue

            for metadata_id, metadata_value in subdivision_metadata(
                    subdiv).items():
                # Check collision with any atrribute defined on Address class.
                if metadata_id in Address.SUBDIVISION_METADATA_WHITELIST:
                    self.assertTrue(hasattr(simple_address, metadata_id))
                else:
                    self.assertFalse(hasattr(simple_address, metadata_id))

    def test_subdivision_parent_code(self):
        # See https://bitbucket.org/flyingcircus/pycountry/issues/13389
        self.assertEqual("GB-ENG", subdivisions.get(code='GB-STS').parent_code)
        self.assertEqual("CZ-20", subdivisions.get(code='CZ-205').parent_code)

    def test_foreign_territory_mapping(self):
        self.assertEqual("FR", territory_attachment("GP"))
        self.assertEqual("NL", territory_attachment("BQ"))

    def test_normalize_territory_code(self):
        self.assertEqual("GR", normalize_territory_code("EL"))
        self.assertEqual("FR", normalize_territory_code("FX"))
        self.assertEqual("TW", normalize_territory_code("CN-71"))
        # Sub-territories will not change by default
        self.assertEqual("BQ", normalize_territory_code("BQ"))
        self.assertEqual("GP", normalize_territory_code("FR-GP"))

        self.assertEqual("BQ-BO", normalize_territory_code("NL-BQ1"))

    def test_normalize_territory_code_with_foreign_territory(self):
        resolved = normalize_territory_code("BQ",
                                            resolve_top_country=True)
        self.assertEqual("NL", resolved)

        resolved = normalize_territory_code("VI",
                                            resolve_top_country=True)
        self.assertEqual("US", resolved)

        resolved = normalize_territory_code("FR-GP",
                                            resolve_top_country=True)
        self.assertEqual("FR", resolved)

        resolved = normalize_territory_code("NL-BQ1",
                                            resolve_top_country=True)

        self.assertEqual("BQ-BO", resolved)
