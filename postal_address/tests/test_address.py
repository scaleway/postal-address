# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#                         Julien Castets <jcastets@scaleway.com>
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

import sys
import textwrap
import unittest
from decimal import Decimal

from postal_address.address import Address, InvalidAddress, random_address
from postal_address.territory import (
    supported_country_codes,
    supported_territory_codes
)
from pycountry import countries, subdivisions


class TestAddressIO(unittest.TestCase):

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

    def test_emptiness(self):
        address = Address()
        self.assertTrue(address.empty)
        self.assertFalse(address)
        self.assertTrue(not address)

        address.line1 = '10, avenue des Champs Elysées'
        self.assertFalse(address.empty)
        self.assertTrue(address)
        self.assertFalse(not address)

    def test_unknown_field(self):
        # Test constructor.
        with self.assertRaises(KeyError):
            Address(bad_field='Blah blah blah')

        # Test item setter.
        address = random_address()
        with self.assertRaises(KeyError):
            address['bad_field'] = 'Blah blah blah'

    def test_non_string_field_value(self):
        # Test constructor.
        with self.assertRaises(TypeError):
            Address(line1=Decimal())

        # Test attribute setter.
        address = random_address()
        with self.assertRaises(TypeError):
            address.line1 = Decimal()

        # Test item setter.
        with self.assertRaises(TypeError):
            address['line1'] = Decimal()

    def test_non_string_field_id(self):
        address = random_address()

        # Test item getter.
        with self.assertRaises(TypeError):
            address[Decimal()]

        # Test item setter.
        with self.assertRaises(TypeError):
            address[Decimal()] = 'Blah blah blah'

    def test_field_deletion(self):
        address = Address(
            line1='1 Infinite Loop',
            postal_code='95014',
            city_name='Cupertino',
            subdivision_code='US-CA')

        # Base field deletion.
        self.assertIsNotNone(address['line1'])
        self.assertIsNotNone(address.line1)
        del address['line1']
        self.assertIsNone(address['line1'])
        self.assertIsNone(address.line1)

        # Territory metadata field deletion.
        self.assertIsNotNone(address['state_name'])
        self.assertIsNotNone(address.state_name)
        del address['state_name']
        with self.assertRaises(KeyError):
            self.assertIsNone(address['state_name'])
        with self.assertRaises(AttributeError):
            self.assertIsNone(address.state_name)

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
        self.assertEquals(len(address), 6)
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
        for key in address:
            self.assertEquals(getattr(address, key), address[key])

    def test_unicode_mess(self):
        address = Address(
            line1='ब ♎ 1F: ̹ƶώ㎂🐎🐙💊 ꧲⋉ ⦼ Ė꧵┵',
            line2='⫇⻛⋯ ǖ╶🐎🐙💊ᵞᚘ⎢ ⚗ ⑆  ͋ụ 0 ⇚  � ῐ ',
            postal_code='3☾Ă⻛🐎🐙💊ȁ�ƈ₟Ǆ✒὘',
            city_name='Į🐎🐙💊❤Ệ▋',
            country_code='FR')
        self.assertIsNotNone(address.line1)
        self.assertIsNotNone(address.line2)
        self.assertIsNotNone(address.postal_code)
        self.assertIsNotNone(address.city_name)

    @unittest.skipIf(sys.version_info.major > 2, "Python 2-only test.")
    def test_unicode_python2(self):
        address = random_address()
        self.assertEquals(address.render().encode('utf-8'), str(address))
        self.assertEquals(address.render(), unicode(address))

    @unittest.skipIf(sys.version_info.major < 3, "Python 3-only test.")
    def test_unicode_python3(self):
        address = random_address()
        self.assertEquals(address.render(), str(address))

    @unittest.skipIf(sys.version_info.major > 2, "Python 2-only test.")
    def test_repr_python2(self):
        address = Address(
            line1='4 place du général Leclerc',
            postal_code='91401',
            city_name='Orsay',
            country_code='FR')
        self.assertEquals(
            repr(address),
            "Address("
            "city_name=u'Orsay', "
            "country_code=u'FR', "
            "country_name=u'France', "
            "empty=False, "
            "line1=u'4 place du g\\xe9n\\xe9ral Leclerc', "
            "line2=None, "
            "postal_code=u'91401', "
            "subdivision_code=None, "
            "subdivision_name=None, "
            "subdivision_type_id=None, "
            "subdivision_type_name=None, "
            "valid=True)")

    @unittest.skipIf(sys.version_info.major < 3, "Python 3-only test.")
    def test_repr_python3(self):
        address = Address(
            line1='4 place du général Leclerc',
            postal_code='91401',
            city_name='Orsay',
            country_code='FR')
        self.assertEquals(
            repr(address),
            "Address("
            "city_name='Orsay', "
            "country_code='FR', "
            "country_name='France', "
            "empty=False, "
            "line1='4 place du général Leclerc', "
            "line2=None, "
            "postal_code='91401', "
            "subdivision_code=None, "
            "subdivision_name=None, "
            "subdivision_type_id=None, "
            "subdivision_type_name=None, "
            "valid=True)")

    def test_rendering(self):
        # Test subdivision-less rendering.
        address = Address(
            line1='BP 438',
            postal_code='75366',
            city_name='Paris CEDEX 08',
            country_code='FR')
        self.assertEquals(address.render(), textwrap.dedent("""\
            BP 438
            75366 - Paris CEDEX 08
            France"""))

        # Test rendering of a state.
        address = Address(
            line1='1600 Amphitheatre Parkway',
            postal_code='94043',
            city_name='Mountain View',
            subdivision_code='US-CA')
        self.assertEquals(address.render(), textwrap.dedent("""\
            1600 Amphitheatre Parkway
            94043 - Mountain View, California
            United States"""))

        # Test rendering of a city which is also its own state.
        address = Address(
            line1='Platz der Republik 1',
            postal_code='11011',
            city_name='Berlin',
            subdivision_code='DE-BE')
        self.assertEquals(address.render(), textwrap.dedent("""\
            Platz der Republik 1
            11011 - Berlin, Berlin
            Germany"""))

        # Test rendering of subdivision name as-is for extra precision.
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='CP')
        self.assertEquals(address.render(), textwrap.dedent("""\
            Dummy address
            F-12345 - Dummy city
            Clipperton
            France"""))

        # Test deduplication of subdivision and country.
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='RE',
            subdivision_code='FR-RE')
        self.assertEquals(address.render(), textwrap.dedent("""\
            Dummy address
            F-12345 - Dummy city
            Réunion"""))
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            country_code='IC')
        self.assertEquals(address.render(), textwrap.dedent("""\
            Dummy address
            F-12345 - Dummy city
            Canarias
            Spain"""))
        address = Address(
            line1='Dummy address',
            postal_code='F-12345',
            city_name='Dummy city',
            subdivision_code='ES-CN')
        self.assertEquals(address.render(), textwrap.dedent("""\
            Dummy address
            F-12345 - Dummy city
            Canarias
            Spain"""))

        # Test deduplication of subdivision and city.
        address = Address(
            line1='2 King Edward Street',
            postal_code='EC1A 1HQ',
            subdivision_code='GB-LND')
        self.assertEquals(address.render(), textwrap.dedent("""\
            2 King Edward Street
            EC1A 1HQ - London, City of
            United Kingdom"""))

    def test_random_address(self):
        """ Test generation, validation and rendering of random addresses. """
        for _ in range(999):
            address = random_address()
            address.validate()
            address.render()


class TestAddressValidation(unittest.TestCase):

    def test_address_validation(self):
        # Test valid address.
        address = Address(
            line1='address_line1',
            line2='address_line2',
            postal_code='75000',
            city_name='Paris',
            country_code='US',
            subdivision_code=None)
        self.assertEquals(address.valid, True)

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
        self.assertIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

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
        self.assertNotIn('required', str(err))
        self.assertIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

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
        self.assertIn('required', str(err))
        self.assertIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

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
        self.assertNotIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertIn('inconsistent', str(err))

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
        self.assertIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

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
        self.assertIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

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
        self.assertIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertNotIn('inconsistent', str(err))

    def test_space_normalization(self):
        address = Address(
            line1='   10, avenue    des \n   Champs Elysées   ',
            line2='    ',
            postal_code='   F     75008   ',
            city_name='   Paris   City    ',
            country_code=' fr          ',
            subdivision_code=' fR-75  ')
        self.assertEqual(address.line1, '10, avenue des Champs Elysées')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, 'F 75008')
        self.assertEqual(address.city_name, 'Paris City')
        self.assertEqual(address.country_code, 'FR')
        self.assertEqual(address.subdivision_code, 'FR-75')

    def test_postal_code_normalization(self):
        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='   -  f-  - -  75008 -   ',
            city_name='Paris',
            country_code='FR')
        self.assertEqual(address.postal_code, 'F-75008')

        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='--   aAA 77b   -    - - --___--- sd-  fs - df'
            'sd--$^$^$^---fsf  -sd xd --',
            city_name='Paris',
            country_code='FR')
        self.assertEqual(address.postal_code, 'AAA 77B-SD-FS-DFSD-FSF-SD XD')

        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code='J/PPB1>6/_',
            city_name='Paris',
            country_code='FR')
        self.assertEqual(address.postal_code, 'JPPB16')

        address = Address(
            line1='10, avenue des Champs Elysées',
            postal_code=' * * * aAA 77b   -    -',
            city_name='Paris',
            country_code='FR')
        self.assertEqual(address.postal_code, 'AAA 77B')

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
        self.assertNotIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertIn('inconsistent', str(err))

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
        self.assertNotIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertIn('inconsistent', str(err))

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

        address = Address(
            line1='16 rue de Millo',
            postal_code='98000',
            city_name='La Condamine',
            subdivision_code='MC-CO')
        self.assertEqual(address.country_code, 'MC')
        self.assertEqual(address.subdivision_code, 'MC-CO')

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
        for address in [address1, address2]:  # address3
            self.assertEqual(address.country_code, 'UM')
            self.assertEqual(address.subdivision_code, 'UM-67')

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
        # address3 = Address(
        #     line1='Kaya Grandi 67',
        #     postal_code='XXX No postal code on Bonaire',
        #     city_name='Bonaire',
        #     country_code='NL',
        #     subdivision_code='BQ-BO')
        # address4 = Address(
        #     line1='Kaya Grandi 67',
        #     postal_code='XXX No postal code on Bonaire',
        #     city_name='Bonaire',
        #     country_code='BQ',
        #     subdivision_code='NL-BQ1')
        # address5 = Address(
        #     line1='Kaya Grandi 67',
        #     postal_code='XXX No postal code on Bonaire',
        #     city_name='Bonaire',
        #     subdivision_code='NL-BQ1')
        # address6 = Address(
        #     line1='Kaya Grandi 67',
        #     postal_code='XXX No postal code on Bonaire',
        #     city_name='Bonaire',
        #     country_code='NL',
        #     subdivision_code='NL-BQ1')
        for address in [
                address1, address2]:  # address3, address4, address5, address6
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
        # address3 = Address(
        #     line1='No.276, Zhongshan Rd.',
        #     postal_code='95001',
        #     city_name='Taitung City',
        #     country_code='CN',
        #     subdivision_code='TW-TTT')
        for address in [address1, address2]:  # address3]:
            self.assertEqual(address.country_code, 'TW')
            self.assertEqual(address.country_name, 'Taiwan')
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

    @unittest.skip(
        "Need to fix edge-case in the subdivision/state/country normalization "
        "code. See #16.")
    def test_subdivision_derived_country(self):
        address = Address(
            line1='Senate House',
            line2='Tyndall Avenue',
            postal_code='BS8 1TH',
            city_name='Bristol',
            subdivision_code='GB-ENG')

        self.assertEquals(
            address.subdivision, subdivisions.get(code='GB-ENG'))
        self.assertEquals(
            address.subdivision_code, 'GB-ENG')
        self.assertEquals(
            address.subdivision_name, 'England')
        self.assertEquals(
            address.subdivision_type_name, 'Country')
        self.assertEquals(
            address.subdivision_type_id, 'country')

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
        self.assertNotIn('required', str(err))
        self.assertNotIn('invalid', str(err))
        self.assertIn('inconsistent', str(err))

    def test_non_strict_mode_normalization(self):
        # Test city name override by subdivision code.
        address = Address(
            strict=False,
            line1='2 King Edward Street',
            postal_code='EC1A 1HQ',
            city_name='Dummy city',
            subdivision_code='GB-LND')
        self.assertEqual(address.line1, '2 King Edward Street')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, 'EC1A 1HQ')
        self.assertEqual(address.city_name, 'London, City of')
        self.assertEqual(address.country_code, 'GB')
        self.assertEqual(address.subdivision_code, 'GB-LND')

        address = Address(
            strict=False,
            line1='4 Bulevardul Nicolae Bålcescu',
            postal_code='010051',
            city_name='Dummy city',
            subdivision_code='RO-B')
        self.assertEqual(address.line1, '4 Bulevardul Nicolae Bålcescu')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, '010051')
        self.assertEqual(address.city_name, 'București')
        self.assertEqual(address.country_code, 'RO')
        self.assertEqual(address.subdivision_code, 'RO-B')

        address = Address(
            strict=False,
            line1='15 Ngô Quyền',
            postal_code='10000',
            city_name='Dummy city',
            subdivision_code='VN-HN')
        self.assertEqual(address.line1, '15 Ngô Quyền')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, '10000')
        self.assertEqual(address.city_name, 'Hà Nội')
        self.assertEqual(address.country_code, 'VN')
        self.assertEqual(address.subdivision_code, 'VN-HN')

        # Test country override by subdivision code.
        address = Address(
            strict=False,
            line1='10, avenue des Champs Elysées',
            postal_code='75008',
            city_name='Paris',
            country_code='FR',
            subdivision_code='BE-BRU')
        self.assertEqual(address.line1, '10, avenue des Champs Elysées')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, '75008')
        self.assertEqual(address.city_name, 'Paris')
        self.assertEqual(address.country_code, 'BE')
        self.assertEqual(address.subdivision_code, 'BE-BRU')

        address = Address(
            strict=False,
            line1='Barack 31',
            postal_code='XXX No postal code',
            city_name='Clipperton Island',
            country_code='CP',
            subdivision_code='FR-CP')
        self.assertEqual(address.line1, 'Barack 31')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, 'XXX NO POSTAL CODE')
        self.assertEqual(address.city_name, 'Clipperton Island')
        self.assertEqual(address.country_code, 'FR')
        self.assertEqual(address.subdivision_code, 'FR-CP')

        # Test both city and country override by subdivision code.
        address = Address(
            strict=False,
            line1='9F., No. 290, Sec. 4, Zhongxiao E. Rd.',
            postal_code='10694',
            city_name='Dummy city',
            country_code='FR',
            subdivision_code='TW-TNN')
        self.assertEqual(
            address.line1, '9F., No. 290, Sec. 4, Zhongxiao E. Rd.')
        self.assertEqual(address.line2, None)
        self.assertEqual(address.postal_code, '10694')
        self.assertEqual(address.city_name, 'Tainan City')
        self.assertEqual(address.country_code, 'TW')
        self.assertEqual(address.country_name, 'Taiwan')
        self.assertEqual(address.subdivision_code, 'TW-TNN')

    @unittest.skip(
        "Need to fix edge-case in the subdivision/state/country normalization "
        "code. See #16.")
    def test_all_country_codes(self):
        """ Validate & render random addresses with all supported countries.
        """
        for country_code in supported_country_codes():
            address = random_address()
            address.country_code = country_code
            address.subdivision_code = None
            address.normalize()
            address.validate()
            address.render()

    @unittest.skip(
        "Need to fix edge-case in the subdivision/state/country normalization "
        "code. See #16.")
    def test_all_territory_codes(self):
        """ Validate & render random addresses with all supported territories.
        """
        for territory_code in supported_territory_codes():
            address = random_address()
            address.country_code = None
            address.subdivision_code = territory_code
            address.normalize(strict=False)
            address.validate()
            address.render()
