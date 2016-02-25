# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016 Scaleway and Contributors. All Rights Reserved.
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

from postal_address.address import (
    Address,
    subdivision_metadata,
    subdivision_type_id
)
from postal_address.territory import (
    COUNTRY_ALIASES,
    SUBDIVISION_ALIASES,
    country_aliases,
    country_from_subdivision,
    default_subdivision_code,
    supported_country_codes,
    supported_subdivision_codes,
    supported_territory_codes,
    territory_children_codes,
    territory_parents_codes
)
from pycountry import countries, subdivisions


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
        self.assertFalse(
            set(map(attrgetter('alpha2'), countries)).intersection(
                map(attrgetter('code'), subdivisions)))

    def test_territory_exception_definition(self):
        # Check that all codes used in constants to define exceptionnal
        # treatment are valid and recognized.
        for subdiv_code, alias_code in SUBDIVISION_ALIASES.items():
            self.assertIn(subdiv_code, supported_subdivision_codes())
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            self.assertIn(
                alias_code, set(map(attrgetter('alpha2'), countries)).union(
                    map(attrgetter('code'), subdivisions)))

        for country_code, alias_code in COUNTRY_ALIASES.items():
            # Aliased country codes are not supposed to be supported by
            # pycountry, as it's the main reason to define an alias in the
            # first place.
            self.assertNotIn(
                country_code, map(attrgetter('alpha2'), countries))
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            self.assertIn(
                alias_code, set(map(attrgetter('alpha2'), countries)).union(
                    map(attrgetter('code'), subdivisions)))

    def test_country_from_subdivision(self):
        # Test reconciliation of ISO 3166-2 and ISO 3166-1 country codes.
        for subdiv_code in SUBDIVISION_ALIASES.keys():
            target_code = SUBDIVISION_ALIASES[subdiv_code]
            if len(target_code) != 2:
                target_code = subdivisions.get(code=target_code).country_code
            self.assertEquals(
                country_from_subdivision(subdiv_code), target_code)
        for subdiv_code in set(
                map(attrgetter('code'), subdivisions)).difference(
                    SUBDIVISION_ALIASES):
            self.assertEquals(
                country_from_subdivision(subdiv_code),
                subdivisions.get(code=subdiv_code).country_code)

    def test_default_subdivision_code(self):
        self.assertEquals(default_subdivision_code('FR'), None)
        self.assertEquals(default_subdivision_code('GU'), 'US-GU')
        self.assertEquals(default_subdivision_code('SJ'), None)

    def test_territory_children_codes(self):
        self.assertEquals(territory_children_codes('GQ'), set([
            'GQ-C', 'GQ-I', 'GQ-AN', 'GQ-BN', 'GQ-BS', 'GQ-CS', 'GQ-KN',
            'GQ-LI', 'GQ-WN']))
        self.assertEquals(territory_children_codes('GQ-I'), set([
            'GQ-AN', 'GQ-BN', 'GQ-BS']))
        self.assertEquals(territory_children_codes('GQ-AN'), set())
        self.assertEquals(territory_children_codes(
            'GQ-AN', include_self=True), set(['GQ-AN']))

    def test_territory_parents_codes(self):
        self.assertEquals(
            list(territory_parents_codes('FR-59')),
            ['FR-59', 'FR-O', 'FR'])
        self.assertEquals(
            list(territory_parents_codes('FR-59', include_country=False)),
            ['FR-59', 'FR-O'])
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
        #self.assertEquals(
        #    list(territory_parents_codes('NO-22')),
        #    ['NO-22', 'SJ'])

    def test_country_aliases(self):
        self.assertEquals(country_aliases('UM-67'), set(['US', 'UM']))
        self.assertEquals(country_aliases('UM'), set(['US', 'UM']))
        self.assertEquals(country_aliases('US'), set(['US']))

        self.assertEquals(country_aliases('BQ-BO'), set(['NL', 'BQ']))
        #self.assertEquals(country_aliases('NL-BQ2'), set(['NL', 'BQ']))

        #self.assertEquals(country_aliases('NO-21'), set(['SJ', 'NO']))

        #self.assertEquals(country_aliases('DG'), set(['DG', 'IO']))
        self.assertEquals(country_aliases('IO'), set(['DG', 'IO']))

        self.assertEquals(country_aliases('FR'), set(['FR', 'FX']))

        self.assertEquals(country_aliases('FR-CP'), set(['FR', 'CP', 'FX']))
        #self.assertEquals(country_aliases('CP'), set(['FR', 'CP', 'FX']))

        #self.assertEquals(country_aliases('FR-RE'), set(['FR', 'FX', 'RE']))
        self.assertEquals(country_aliases('RE'), set(['FR', 'FX', 'RE']))

        self.assertEquals(country_aliases('GB'), set(['UK', 'GB']))
        #self.assertEquals(country_aliases('UK'), set(['UK', 'GB']))

        self.assertEquals(country_aliases('IM'), set(['IM']))

        self.assertEquals(country_aliases('MC'), set(['MC']))

    def test_subdivision_type_id_conversion(self):
        # Conversion of subdivision types into IDs must be python friendly
        attribute_regexp = re.compile('[a-z][a-z0-9_]*$')
        for subdiv in subdivisions:
            self.assertTrue(attribute_regexp.match(
                subdivision_type_id(subdiv)))

    def test_subdivision_type_id_city_classification(self):
        city_like_subdivisions = [
            'TM-S',    # Aşgabat, Turkmenistan, City
            'TW-CYI',  # Chiay City, Taiwan, Municipality
            'TW-TPE',  # Taipei City, Taiwan, Special Municipality
            'ES-ML',   # Melilla, Spain, Autonomous city
            'GB-LND',  # City of London, United Kingdom, City corporation
            'KP-01',   # P’yŏngyang, North Korea, Capital city
            'KP-13',   # Nasŏn (Najin-Sŏnbong), North Korea, Special city
            'KR-11',   # Seoul Teugbyeolsi, South Korea, Capital Metropolitan
                       # City
            'HU-HV',   # Hódmezővásárhely, Hungary, City with county rights
            'LV-RIX',  # Rīga, Latvia, Republican City
            'ME-15',   # Plužine, Montenegro, Municipality
            'NL-BQ1',  # Bonaire, Netherlands, Special municipality
            'KH-12',   # Phnom Penh, Cambodia, Autonomous municipality
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
