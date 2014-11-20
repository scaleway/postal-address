# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

import re

import unittest
from pycountry import countries, subdivisions

from address import Address, territory_codes, subdivision_type_id


class TestAddress(unittest.TestCase):

    def test_default_values(self):
        address = Address(
            line1='10 Downing Street',
            postal_code='12345',
            city_name='Paris',
            country_code='FR')
        self.assertEquals(address.line1, '10 Downing Street')
        self.assertEquals(address.line2, None)
        self.assertEquals(address.postal_code, '12345')
        self.assertEquals(address.city_name, 'Paris')
        self.assertEquals(address.country_code, 'FR')
        self.assertEquals(address.subdivision_code, None)

    def test_dict_access(self):
        address = Address(
            line1='10 Downing Street',
            postal_code='12345',
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
            set([None, '10 Downing Street', '12345', 'Paris', 'FR']),
            set(address.values()))
        self.assertEquals({
            'line1': '10 Downing Street',
            'line2': None,
            'postal_code': '12345',
            'city_name': 'Paris',
            'country_code': 'FR',
            'subdivision_code': None,
        }, dict(address.items()))
        for key in address.keys():
            self.assertEquals(getattr(address, key), address[key])

    def test_blank_string_normalization(self):
        address = Address(
            line1='10 Downing Street',
            line2='',
            postal_code='12345',
            city_name='Paris',
            country_code='FR',
            subdivision_code='')
        self.assertEquals(address.line2, None)
        self.assertEquals(address.subdivision_code, None)

    def test_blank_line_swap(self):
        address = Address(
            line1='',
            line2='10 Downing Street',
            postal_code='12345',
            city_name='Paris',
            country_code='FR')
        self.assertEquals(address.line1, '10 Downing Street')
        self.assertEquals(address.line2, None)

    def test_normalization(self):
        address = Address(
            line1='666, hell street',
            line2='',
            postal_code='F-6666',
            city_name='Satantown',
            country_code=' fr          ',
            subdivision_code='fR-66  ')
        self.assertEqual(address.line1, '666, hell street')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, 'F-6666')
        self.assertEqual(address.city_name, 'Satantown')
        self.assertEqual(address.country_code, 'FR')
        self.assertEqual(address.subdivision_code, 'FR-66')

    def test_country_subdivision_consistency(self):
        Address(
            line1='10 Downing Street',
            postal_code='12345',
            city_name='Paris',
            country_code='FR',
            subdivision_code='FR-75')
        with self.assertRaises(ValueError):
            Address(
                line1='10 Downing Street',
                postal_code='12345',
                city_name='Paris',
                country_code='FR',
                subdivision_code='BE-BRU')

    def test_subdivision_derived_fields(self):
        address = Address(
            line1='10 Downing Street',
            postal_code='12345',
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
            line1='10 Downing Street',
            postal_code='12345',
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
            line1='10 Downing Street',
            postal_code='12345',
            city_name='London, City of',
            subdivision_code='GB-LND')
        with self.assertRaises(ValueError):
            Address(
                line1='10 Downing Street',
                postal_code='12345',
                city_name='Paris',
                subdivision_code='GB-LND')


class TestTerritory(unittest.TestCase):

    def test_territory_codes(self):
        self.assertIn('FR', territory_codes())
        self.assertIn('FR-59', territory_codes())
        self.assertNotIn('FRE', territory_codes())

    def test_subdivision_type_id_conversion(self):
        # Conversion of subdivision types into IDs must be python friendly
        attribute_regexp = re.compile('[a-z][a-z0-9_]*$')
        subdiv_types = set([subdiv.type for subdiv in subdivisions])
        for subdiv_type in subdiv_types:
            self.assertTrue(attribute_regexp.match(
                subdivision_type_id(subdiv_type)))

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
                subdivision_type_id(subdivisions.get(code=subdiv_code).type),
                'city')

    def test_subdivision_type_id_collision(self):
        simple_address = Address(
            line1='10 Downing Street',
            postal_code='12345',
            city_name='Paris',
            country_code='FR')
        # Subdivision type IDs should not collide with address fields
        subdiv_types = set([subdiv.type for subdiv in subdivisions])
        for subdiv_type_id in map(subdivision_type_id, subdiv_types):

            # XXX ISO 3166-2 reuse the country type as subdivisions.
            # We really need to add proper support for these cases, as we did
            # for cities.
            if subdiv_type_id in ['country']:
                continue

            for component_id_template in [
                    '{}', '{}_code', '{}_name', '{}_type_name']:
                component_id = component_id_template.format(subdiv_type_id)
                if component_id in Address.SUBDIVISION_OVERRIDABLE_FIELDS:
                    self.assertIn(component_id, Address.BASE_COMPONENT_IDS)
                    self.assertTrue(hasattr(simple_address, component_id))
                else:
                    self.assertFalse(hasattr(simple_address, component_id))
