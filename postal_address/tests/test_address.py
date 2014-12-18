# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014 Online SAS and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@ocs.online.net>
#                         Julien Castets <jcastets@ocs.online.net>
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

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

from operator import attrgetter
import re
import unittest

from pycountry import countries, subdivisions

from postal_address.address import (
    Address, default_subdivision_code, normalize_country_code,
    supported_territory_codes, country_aliases,
    territory_parents_codes, COUNTRY_ALIASES, SUBDIVISION_ALIASES,
    subdivision_metadata, subdivision_type_id)

try:
    from itertools import imap
except ImportError:  # pragma: no cover
    basestring = (str, bytes)
    unicode = str
    imap = map


class TestAddress(unittest.TestCase):

    def test_emptiness(self):
        address = Address()
        self.assertTrue(address.empty)
        self.assertFalse(address)
        self.assertTrue(not address)

        address.line1 = '10, avenue des Champs Elysées'
        self.assertFalse(address.empty)
        self.assertTrue(address)
        self.assertFalse(not address)

    def test_default_values(self):
        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR')
        self.assertEquals(address.line1, '10, avenue des Champs Elysées')
        self.assertEquals(address.line2, None)
        self.assertEquals(address.postal_code, '75008')
        self.assertEquals(address.city_name, 'Paris')
        self.assertEquals(address.country_code, 'FR')
        self.assertEquals(address.subdivision_code, None)

    def test_dict_access(self):
        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR')
        self.assertSequenceEqual(set([
            'line1',
            'line2',
            'postal_code',
            'city_name',
            'country_code',
            'subdivision_code',
        ]), set(address.keys()))
        self.assertEquals(
            set([None, '10, avenue des Champs Elysées',
                 '75008', 'Paris', 'FR']),
            set(address.values()))
        self.assertEquals({
            'line1': '10, avenue des Champs Elysées',
            'line2': None,
            'postal_code': '75008',
            'city_name': 'Paris',
            'country_code': 'FR',
            'subdivision_code': None,
        }, dict(address.items()))
        for key in address.keys():
            self.assertEquals(getattr(address, key), address[key])

    def test_blank_string_normalization(self):
        address = Address(
            line1='10, avenue des Champs Elysées',
            line2='',
            postal_code='75008',
            city_name='Paris',
            country_code='FR',
            subdivision_code='')
        self.assertEquals(address.line2, None)
        self.assertEquals(address.subdivision_code, None)

    def test_space_normalization(self):
        address = Address(
            line1='   10, avenue des Champs Elysées   ',
            line2='    ',
            postal_code='   75008   ',
            city_name='   Paris  ',
            country_code=' fr          ',
            subdivision_code=' fR-75  ')
        self.assertEqual(address.line1, '10, avenue des Champs Elysées')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, '75008')
        self.assertEqual(address.city_name, 'Paris')
        self.assertEqual(address.country_code, 'FR')
        self.assertEqual(address.subdivision_code, 'FR-75')

    def test_blank_line_swap(self):
        address = Address(
            line1='',
            line2='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR')
        self.assertEquals(address.line1, '10, avenue des Champs Elysées')
        self.assertEquals(address.line2, None)

    def test_country_subdivision_validation(self):
        Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR',
            subdivision_code='FR-75')
        with self.assertRaises(ValueError):
            Address(
                line1='10, avenue des Champs Elysées',
                postal_code='75008',
                city_name='Paris',
                country_code='FR',
                subdivision_code='BE-BRU')
        with self.assertRaises(ValueError):
            Address(
                line1='10, avenue des Champs Elysées',
                postal_code='75008',
                city_name='Paris',
                country_code='FR',
                subdivision_code='US-GU')

    def test_country_subdivision_reconciliation(self):
        # Perfect, already normalized country and subdivision.
        address1 = Address(
            line1='1273 Pale San Vitores Road',
            postal_code='96913',
            city_name='Tamuning',
            country_code='GU',
            subdivision_code='US-GU')

        # Non-normalized country.
        address2 = Address(
            line1='1273 Pale San Vitores Road',
            postal_code='96913',
            city_name='Tamuning',
            country_code='US',
            subdivision_code='US-GU')

        # Country only, from which we guess the subdivision.
        address3 = Address(
            line1='1273 Pale San Vitores Road',
            postal_code='96913',
            city_name='Tamuning',
            country_code='GU')

        # Subdivision only, from which we derive the country.
        address4 = Address(
            line1='1273 Pale San Vitores Road',
            postal_code='96913',
            city_name='Tamuning',
            subdivision_code='US-GU')

        for address in [address1, address2, address3, address4]:
            self.assertEqual(address.line1, '1273 Pale San Vitores Road')
            self.assertEqual(address.line2, None)
            self.assertEqual(address.postal_code, '96913')
            self.assertEqual(address.city_name, 'Tamuning')
            self.assertEqual(address.country_code, 'GU')
            self.assertEqual(address.subdivision_code, 'US-GU')

    def test_country_alias_normalization(self):
        address = Address(
            line1='Barack 31',
            postal_code='XXX No postal code on this atoll',
            city_name='Clipperton Island',
            country_code='CP')
        self.assertEqual(address.country_code, 'FR')
        self.assertEqual(address.subdivision_code, 'FR-CP')

        # Test normalization of non-normalized country of a subdivision
        # of a country aliased subdivision.
        address1 = Address(
            line1='Bunker building 746',
            postal_code='XXX No postal code on this atoll',
            city_name='Johnston Atoll',
            country_code='UM',
            subdivision_code='UM-67')
        address2 = Address(
            line1='Bunker building 746',
            postal_code='XXX No postal code on this atoll',
            city_name='Johnston Atoll',
            subdivision_code='UM-67')
        for address in [address1, address2]:
            self.assertEqual(address.country_code, 'UM')
            self.assertEqual(address.subdivision_code, 'UM-67')

        # Test normalization of TW subdivisions.
        address1 = Address(
            line1='No.276, Zhongshan Rd.',
            postal_code='95001',
            city_name='Taitung City',
            country_code='TW',
            subdivision_code='TW-TTT')
        address2 = Address(
            line1='No.276, Zhongshan Rd.',
            postal_code='95001',
            city_name='Taitung City',
            subdivision_code='TW-TTT')
        for address in [address1, address2]:
            self.assertEqual(address.country_code, 'TW')
            self.assertEqual(address.subdivision_code, 'TW-TTT')

    def test_subdivision_derived_fields(self):
        address = Address(
            line1='31, place du Théatre',
            postal_code='59000',
            city_name='Lille',
            subdivision_code='FR-59')

        self.assertEquals(
            address.subdivision, subdivisions.get(code='FR-59'))
        self.assertEquals(
            address.subdivision_code, 'FR-59')
        self.assertEquals(
            address.subdivision_name, 'Nord')
        self.assertEquals(
            address.subdivision_type_name, 'Metropolitan department')
        self.assertEquals(
            address.subdivision_type_id, 'metropolitan_department')

        self.assertEquals(
            address.metropolitan_department, subdivisions.get(code='FR-59'))
        self.assertEquals(
            address.metropolitan_department_code, 'FR-59')
        self.assertEquals(
            address.metropolitan_department_name, 'Nord')
        self.assertEquals(
            address.metropolitan_department_type_name,
            'Metropolitan department')

        self.assertEquals(
            address.metropolitan_region, subdivisions.get(code='FR-O'))
        self.assertEquals(
            address.metropolitan_region_code, 'FR-O')
        self.assertEquals(
            address.metropolitan_region_name, 'Nord - Pas-de-Calais')
        self.assertEquals(
            address.metropolitan_region_type_name,
            'Metropolitan region')

        self.assertEquals(
            address.country, countries.get(alpha2='FR'))
        self.assertEquals(
            address.country_code, 'FR')
        self.assertEquals(
            address.country_name, 'France')

    def test_subdivision_derived_city_fields(self):
        address = Address(
            line1='2 King Edward Street',
            postal_code='EC1A 1HQ',
            subdivision_code='GB-LND')

        self.assertEquals(
            address.subdivision, subdivisions.get(code='GB-LND'))
        self.assertEquals(
            address.subdivision_code, 'GB-LND')
        self.assertEquals(
            address.subdivision_name, 'London, City of')
        self.assertEquals(
            address.subdivision_type_name, 'City corporation')
        self.assertEquals(
            address.subdivision_type_id, 'city')

        self.assertEquals(
            address.city, subdivisions.get(code='GB-LND'))
        self.assertEquals(
            address.city_code, 'GB-LND')
        self.assertEquals(
            address.city_name, 'London, City of')
        self.assertEquals(
            address.city_type_name, 'City corporation')

        self.assertEquals(address.country_code, 'GB')

    def test_city_override_by_subdivision(self):
        Address(
            line1='2 King Edward Street',
            postal_code='EC1A 1HQ',
            city_name='London, City of',
            subdivision_code='GB-LND')
        with self.assertRaises(ValueError):
            Address(
                line1='2 King Edward Street',
                postal_code='EC1A 1HQ',
                city_name='Paris',
                subdivision_code='GB-LND')


class TestTerritory(unittest.TestCase):
    # Test territory utils

    def test_supported_territory_codes(self):
        self.assertIn('FR', supported_territory_codes())
        self.assertIn('FR-59', supported_territory_codes())
        self.assertNotIn('FRE', supported_territory_codes())

    def test_territory_code_overlap(self):
        # Check that all codes from each classifications we rely on are not
        # overlapping.
        self.assertFalse(
            set(imap(attrgetter('alpha2'), countries)).intersection(
                imap(attrgetter('code'), subdivisions)))

    def test_territory_exception_definition(self):
        # Check that all codes used in constants to define exceptionnal
        # treatment are valid and recognized.
        for subdiv_code, alias_code in SUBDIVISION_ALIASES.items():
            self.assertIn(subdiv_code, supported_territory_codes())
            self.assertIn(alias_code, supported_territory_codes())
        for subdiv_code, alias_code in COUNTRY_ALIASES.items():
            self.assertIn(alias_code, supported_territory_codes())
            # Aliased country codes are not supposed to be supported by
            # pycountry, as it's the main reason to define an alias in the
            # first place.
            self.assertNotIn(
                subdiv_code, imap(attrgetter('alpha2'), countries))

    def test_country_code_reconciliation(self):
        # Test reconciliation of ISO 3166-2 and ISO 3166-1 country codes.
        for subdiv_code in SUBDIVISION_ALIASES.keys():
            target_code = SUBDIVISION_ALIASES[subdiv_code]
            if len(target_code) != 2:
                target_code = subdivisions.get(code=target_code).country_code
            self.assertEquals(
                normalize_country_code(subdiv_code), target_code)
        for subdiv_code in set(
                imap(attrgetter('code'), subdivisions)).difference(
                    SUBDIVISION_ALIASES):
            self.assertEquals(
                normalize_country_code(subdiv_code),
                subdivisions.get(code=subdiv_code).country_code)

    def test_default_subdivision_code(self):
        self.assertEquals(default_subdivision_code('FR'), None)
        self.assertEquals(default_subdivision_code('GU'), 'US-GU')
        self.assertEquals(default_subdivision_code('SJ'), None)

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

    def test_country_aliases(self):
        self.assertEquals(country_aliases('UM-67'), set(['US', 'UM']))
        self.assertEquals(country_aliases('UM'), set(['US', 'UM']))
        self.assertEquals(country_aliases('US'), set(['US']))
        self.assertEquals(country_aliases('BQ-BO'), set(['NL', 'BQ']))

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
