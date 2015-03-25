# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2015 Online SAS and Contributors. All Rights Reserved.
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

import unittest

from pycountry import countries, subdivisions

from postal_address.address import Address, InvalidAddress


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

    def test_bad_field(self):
        with self.assertRaises(KeyError):
            address = Address(
                bad_field='Blah blah blah')

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

    def test_address_validation(self):
        # Test required fields at validation.
        address = Address(
            line1=None,
            postal_code=None,
            city_name=None,
            country_code=None)
        self.assertEquals(address.valid, False)
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(
            err.required_fields,
            set(['line1', 'postal_code', 'city_name', 'country_code']))
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(err.inconsistent_fields, set())

        # Test post-normalization validation of invalid country and subdivision
        # codes.
        address = Address(
            line1='Dummy street',
            postal_code='12345',
            city_name='Dummy city')
        self.assertEquals(address.valid, False)
        address.country_code = 'invalid-code'
        address.subdivision_code = 'stupid-code'
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set())
        self.assertEquals(
            err.invalid_fields, set(['country_code', 'subdivision_code']))
        self.assertEquals(err.inconsistent_fields, set())

        # Mix invalid and required fields in post-normalization validation.
        address = Address(
            line1='Dummy street',
            postal_code='12345',
            city_name='Dummy city')
        self.assertEquals(address.valid, False)
        address.country_code = None
        address.subdivision_code = 'stupid-code'
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set(['country_code']))
        self.assertEquals(err.invalid_fields, set(['subdivision_code']))
        self.assertEquals(err.inconsistent_fields, set())

        # Test post-normalization validation of inconsistent country and
        # subdivision codes.
        address = Address(
            line1='Dummy street',
            postal_code='12345',
            city_name='Dummy city')
        self.assertEquals(address.valid, False)
        address.country_code = 'FR'
        address.subdivision_code = 'US-CA'
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set())
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(
            err.inconsistent_fields,
            set([('country_code', 'subdivision_code')]))

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

    def test_invalid_code_normalization(self):
        # Invalid country and subdivision codes are normalized to None.
        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            subdivision_code='42')
        self.assertEquals(address.country_code, None)
        self.assertEquals(address.subdivision_code, None)
        self.assertEquals(address.valid, False)
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set(['country_code']))
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(err.inconsistent_fields, set())

        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='MARS')
        self.assertEquals(address.country_code, None)
        self.assertEquals(address.subdivision_code, None)
        self.assertEquals(address.valid, False)
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set(['country_code']))
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(err.inconsistent_fields, set())

        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='MARS',
            subdivision_code='42')
        self.assertEquals(address.country_code, None)
        self.assertEquals(address.subdivision_code, None)
        self.assertEquals(address.valid, False)
        with self.assertRaises(InvalidAddress) as expt:
            address.validate()
        err = expt.exception
        self.assertEquals(err.required_fields, set(['country_code']))
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(err.inconsistent_fields, set())

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

        with self.assertRaises(InvalidAddress) as expt:
            Address(
                line1='10, avenue des Champs Elysées',
                postal_code='75008',
                city_name='Paris',
                country_code='FR',
                subdivision_code='BE-BRU')
        err = expt.exception
        self.assertEquals(err.required_fields, set())
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(
            err.inconsistent_fields,
            set([('country_code', 'subdivision_code')]))

        with self.assertRaises(InvalidAddress) as expt:
            Address(
                line1='10, avenue des Champs Elysées',
                postal_code='75008',
                city_name='Paris',
                country_code='FR',
                subdivision_code='US-GU')
        err = expt.exception
        self.assertEquals(err.required_fields, set())
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(
            err.inconsistent_fields,
            set([('country_code', 'subdivision_code')]))

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
        # address3 = Address(
        #     line1='Bunker building 746',
        #     postal_code='XXX No postal code on this atoll',
        #     city_name='Johnston Atoll',
        #     country_code='US',
        #     subdivision_code='UM-67')
        for address in [address1, address2]:  # , address3]:
            self.assertEqual(address.country_code, 'UM')
            self.assertEqual(address.subdivision_code, 'UM-67')

        return

        # Test normalization of non-normalized country of a subdivision
        # aliased to a subdivision.
        address1 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            #city_name='Kralendijk',
            city_name='Bonaire',
            country_code='BQ',
            subdivision_code='BQ-BO')
        address2 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            city_name='Bonaire',
            subdivision_code='BQ-BO')
        address3 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            city_name='Bonaire',
            country_code='NL',
            subdivision_code='BQ-BO')
        address4 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            city_name='Bonaire',
            country_code='BQ',
            subdivision_code='NL-BQ1')
        address5 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            city_name='Bonaire',
            subdivision_code='NL-BQ1')
        address6 = Address(
            line1='Kaya Grandi 67',
            postal_code='XXX No postal code on Bonaire',
            city_name='Bonaire',
            country_code='NL',
            subdivision_code='NL-BQ1')
        for address in [
                address1, address2, address3, address4, address5, address6]:
            self.assertEqual(address.country_code, 'BQ')
            self.assertEqual(address.subdivision_code, 'BQ-BO')

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
        address3 = Address(
            line1='No.276, Zhongshan Rd.',
            postal_code='95001',
            city_name='Taitung City',
            country_code='CN',
            subdivision_code='TW-TTT')
        for address in [address1, address2, address3]:
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

        with self.assertRaises(InvalidAddress) as expt:
            Address(
                line1='2 King Edward Street',
                postal_code='EC1A 1HQ',
                city_name='Paris',
                subdivision_code='GB-LND')
        err = expt.exception
        self.assertEquals(err.required_fields, set())
        self.assertEquals(err.invalid_fields, set())
        self.assertEquals(
            err.inconsistent_fields, set([('city_name', 'subdivision_code')]))

    def test_rendering(self):
        # Test rendering of a state.
        address = Address(
            line1='1600 Amphitheatre Parkway',
            postal_code='94043',
            city_name='Mountain View',
            subdivision_code='US-CA')
        self.assertEquals(
            address.render(),
            """1600 Amphitheatre Parkway
94043 - Mountain View, California
United States""")

        # Test rendering of a city which is also its own state.
        address = Address(
            line1='Platz der Republik 1',
            postal_code='11011',
            city_name='Berlin',
            subdivision_code='DE-BE')
        self.assertEquals(
            address.render(),
            """Platz der Republik 1
11011 - Berlin, Berlin
Germany""")

        # Test rendering of subdivision name as-is for extra precision.
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='CP')
        self.assertEquals(
            address.render(),
            """Dummy address
F-12345 - Dummy city
Clipperton
France""")

        # Test deduplication of subdivision and country.
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='RE',
            subdivision_code='FR-RE')
        self.assertEquals(
            address.render(),
            """Dummy address
F-12345 - Dummy city
Réunion""")
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='IC')
        self.assertEquals(
            address.render(),
            """Dummy address
F-12345 - Dummy city
Canarias
Spain""")
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            subdivision_code='ES-CN')
        self.assertEquals(
            address.render(),
            """Dummy address
F-12345 - Dummy city
Canarias
Spain""")

        # Test deduplication of subdivision and city.
        address = Address(
            line1='2 King Edward Street',
            postal_code='EC1A 1HQ',
            subdivision_code='GB-LND')
        self.assertEquals(
            address.render(),
            """2 King Edward Street
EC1A 1HQ - London, City of
United Kingdom""")
