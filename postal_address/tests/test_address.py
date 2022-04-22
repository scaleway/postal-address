# Copyright (c) 2013-2022 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#                         Julien Castets <jcastets@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause
import textwrap
from decimal import Decimal

import pytest
from pycountry import countries, subdivisions

from postal_address.address import Address, InvalidAddress, random_address
from postal_address.territory import (
    supported_country_codes,
    supported_subdivision_codes,
)


class TestAddressIO:
    def test_default_values(self) -> None:
        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
        )
        assert address.line1 == "10, avenue des Champs Elysées"
        assert address.line2 is None
        assert address.postal_code == "75008"
        assert address.city_name == "Paris"
        assert address.country_code == "FR"
        assert address.subdivision_code is None

    def test_emptiness(self) -> None:
        address = Address()
        assert address.empty is True
        assert not address

        address.line1 = "10, avenue des Champs Elysées"
        assert address.empty is False
        assert address

    def test_unknown_field(self) -> None:
        # Test constructor.
        with pytest.raises(KeyError):
            Address(bad_field="Blah blah blah")

        # Test item setter.
        address = random_address()
        with pytest.raises(KeyError):
            address["bad_field"] = "Blah blah blah"

    def test_non_string_field_value(self) -> None:
        # Test constructor.
        with pytest.raises(TypeError):
            Address(line1=Decimal())  # type: ignore

        # Test attribute setter.
        address = random_address()
        with pytest.raises(TypeError):
            address.line1 = Decimal()  # type: ignore

        # Test item setter.
        with pytest.raises(TypeError):
            address["line1"] = Decimal()

    def test_non_string_field_id(self) -> None:
        address = random_address()

        # Test item getter.
        with pytest.raises(TypeError):
            address[Decimal()]  # type: ignore

        # Test item setter.
        with pytest.raises(TypeError):
            address[Decimal()] = "Blah blah blah"  # type: ignore

    def test_field_deletion(self) -> None:
        address = Address(
            line1="1 Infinite Loop",
            postal_code="95014",
            city_name="Cupertino",
            subdivision_code="US-CA",
        )

        # Base field deletion.
        assert address["line1"] is not None
        assert address.line1 is not None
        del address["line1"]
        assert address["line1"] is None
        assert address.line1 is None

        # Territory metadata field deletion.
        assert address["state_name"] is not None
        assert address.state_name is not None
        del address["state_name"]
        with pytest.raises(KeyError):
            assert address["state_name"] is None
        with pytest.raises(AttributeError):
            assert address.state_name is None

    def test_dict_access(self) -> None:
        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
        )
        assert {
            "line1",
            "line2",
            "postal_code",
            "city_name",
            "country_code",
            "subdivision_code",
        } == set(address)

        assert len(address) == 6
        assert {"10, avenue des Champs Elysées", "75008", "Paris", "FR", None} == set(
            address.values()
        )
        assert {
            "line1": "10, avenue des Champs Elysées",
            "line2": None,
            "postal_code": "75008",
            "city_name": "Paris",
            "country_code": "FR",
            "subdivision_code": None,
        } == dict(address.items())
        for key in address:
            assert getattr(address, key) == address[key]

    def test_unicode_mess(self) -> None:
        address = Address(
            line1="ब ♎ 1F: ̹ƶώ㎂🐎🐙💊 ꧲⋉ ⦼ Ė꧵┵",
            line2="⫇⻛⋯ ǖ╶🐎🐙💊ᵞᚘ⎢ ⚗ ⑆  ͋ụ 0 ⇚  � ῐ ",
            postal_code="3☾Ă⻛🐎🐙💊ȁ�ƈ₟Ǆ✒὘",
            city_name="Į🐎🐙💊❤Ệ▋",
            country_code="FR",
        )
        assert address.line1 is not None
        assert address.line2 is not None
        assert address.postal_code is not None
        assert address.city_name is not None

    def test_render(self) -> None:
        address = random_address()
        assert address.render() == str(address)

    def test_repr(self) -> None:
        address = Address(
            line1="4 place du général Leclerc",
            postal_code="91401",
            city_name="Orsay",
            country_code="FR",
        )
        assert repr(address) == (
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
            "valid=True)"
        )

    def test_rendering(self) -> None:
        # Test subdivision-less rendering.
        address = Address(
            line1="BP 438",
            postal_code="75366",
            city_name="Paris CEDEX 08",
            country_code="FR",
        )
        assert address.render() == textwrap.dedent(
            """\
            BP 438
            75366 - Paris CEDEX 08
            France"""
        )

        # Test rendering of a state.
        address = Address(
            line1="1600 Amphitheatre Parkway",
            postal_code="94043",
            city_name="Mountain View",
            subdivision_code="US-CA",
        )
        assert address.render() == textwrap.dedent(
            """\
            1600 Amphitheatre Parkway
            94043 - Mountain View, California
            United States"""
        )

        # Test rendering of a city which is also its own state.
        address = Address(
            line1="Platz der Republik 1",
            postal_code="11011",
            city_name="Berlin",
            subdivision_code="DE-BE",
        )
        assert address.render() == textwrap.dedent(
            """\
            Platz der Republik 1
            11011 - Berlin
            Germany"""
        )

        # Test rendering of subdivision name as-is for extra precision.
        address = Address(
            line1="Dummy address",
            postal_code="F-12345",
            city_name="Dummy city",
            country_code="CP",
        )  # This is not an official country_code
        assert address.render() == textwrap.dedent(
            """\
            Dummy address
            F-12345 - Dummy city
            Clipperton
            France"""
        )

        # Test deduplication of subdivision and country.
        address = Address(
            line1="Dummy address",
            postal_code="F-12345",
            city_name="Dummy city",
            country_code="RE",
            subdivision_code="FR-RE",
        )
        assert address.render() == textwrap.dedent(
            """\
            Dummy address
            F-12345 - Dummy city
            La Réunion
            Réunion"""
        )
        address = Address(
            line1="Dummy address",
            postal_code="F-12345",
            city_name="Dummy city",
            country_code="IC",
        )  # This is not an official country_code
        assert address.render() == textwrap.dedent(
            """\
            Dummy address
            F-12345 - Dummy city
            Canarias
            Spain"""
        )
        address = Address(
            line1="Dummy address",
            postal_code="F-12345",
            city_name="Dummy city",
            subdivision_code="ES-CN",
        )
        assert address.render() == textwrap.dedent(
            """\
            Dummy address
            F-12345 - Dummy city
            Canarias
            Spain"""
        )

        # Test deduplication of subdivision and city.
        address = Address(
            line1="2 King Edward Street",
            postal_code="EC1A 1HQ",
            subdivision_code="GB-LND",
        )
        assert address.render() == textwrap.dedent(
            """\
            2 King Edward Street
            EC1A 1HQ - London, City of
            United Kingdom"""
        )

    def test_random_address(self) -> None:
        """Test generation, validation and rendering of random addresses."""
        for _ in range(999):
            address = random_address()
            address.validate()
            address.render()


class TestAddressValidation:
    def test_address_validation(self) -> None:
        # Test valid address.
        address = Address(
            line1="address_line1",
            line2="address_line2",
            postal_code="75000",
            city_name="Paris",
            country_code="US",
            subdivision_code=None,
        )
        assert address.valid is True

        # Test required fields at validation.
        address = Address(
            line1=None, postal_code=None, city_name=None, country_code=None
        )
        assert address.valid is False
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == {
            "line1",
            "postal_code",
            "city_name",
            "country_code",
        }
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == set()
        assert "required" in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" not in str(err)

        # Test post-normalization validation of invalid country and subdivision
        # codes.
        address = Address(
            line1="Dummy street", postal_code="12345", city_name="Dummy city"
        )
        assert address.valid is False
        address.country_code = "invalid-code"
        address.subdivision_code = "stupid-code"
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == set()
        assert err.invalid_fields == {
            "country_code": "invalid-code",
            "subdivision_code": "stupid-code",
        }
        assert err.inconsistent_fields == set()
        assert "required" not in str(err)
        assert "invalid" in str(err)
        assert "inconsistent" not in str(err)

        # Mix invalid and required fields in post-normalization validation.
        address = Address(
            line1="Dummy street", postal_code="12345", city_name="Dummy city"
        )
        assert address.valid is False
        address.country_code = None
        address.subdivision_code = "stupid-code"
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == {"country_code"}
        assert err.invalid_fields == {"subdivision_code": "stupid-code"}
        assert err.inconsistent_fields == set()
        assert "required" in str(err)
        assert "invalid" in str(err)
        assert "inconsistent" not in str(err)

        # Test post-normalization validation of inconsistent country and
        # subdivision codes.
        address = Address(
            line1="Dummy street", postal_code="12345", city_name="Dummy city"
        )
        assert address.valid is False
        address.country_code = "FR"
        address.subdivision_code = "US-CA"
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == set()
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == {("country_code", "subdivision_code")}
        assert "required" not in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" in str(err)

    def test_blank_string_normalization(self) -> None:
        address = Address(
            line1="10, avenue des Champs Elysées",
            line2="",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
            subdivision_code="",
        )
        assert address.line2 is None
        assert address.subdivision_code is None

    def test_invalid_code_normalization(self) -> None:
        # Invalid country and subdivision codes are normalized to None.
        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            subdivision_code="42",
        )
        assert address.country_code is None
        assert address.subdivision_code is None
        assert address.valid is False
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == {"country_code"}
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == set()
        assert "required" in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" not in str(err)

        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="MARS",
        )
        assert address.country_code is None
        assert address.subdivision_code is None
        assert address.valid is False
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == {"country_code"}
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == set()
        assert "required" in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" not in str(err)

        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="MARS",
            subdivision_code="42",
        )
        assert address.country_code is None
        assert address.subdivision_code is None
        assert address.valid is False
        with pytest.raises(InvalidAddress) as expt:
            address.validate()
        err = expt.value
        assert err.required_fields == {"country_code"}
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == set()
        assert "required" in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" not in str(err)

    def test_space_normalization(self) -> None:
        address = Address(
            line1="   10, avenue    des \n   Champs Elysées   ",
            line2="    ",
            postal_code="   F     75008   ",
            city_name="   Paris   City    ",
            country_code=" fr          ",
            subdivision_code=" fR-75  ",
        )
        assert address.line1 == "10, avenue des Champs Elysées"
        assert address.line2 is None
        assert address.postal_code == "F 75008"
        assert address.city_name == "Paris City"
        assert address.country_code == "FR"
        assert address.subdivision_code == "FR-75"

    def test_postal_code_normalization(self) -> None:
        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="   -  f-  - -  75008 -   ",
            city_name="Paris",
            country_code="FR",
        )
        assert address.postal_code == "F-75008"

        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="--   aAA 77b   -    - - --___--- sd-  fs - df"
            "sd--$^$^$^---fsf  -sd xd --",
            city_name="Paris",
            country_code="FR",
        )
        assert address.postal_code == "AAA 77B-SD-FS-DFSD-FSF-SD XD"

        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="J/PPB1>6/_",
            city_name="Paris",
            country_code="FR",
        )
        assert address.postal_code == "JPPB16"

        address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code=" * * * aAA 77b   -    -",
            city_name="Paris",
            country_code="FR",
        )
        assert address.postal_code == "AAA 77B"

    def test_blank_line_swap(self) -> None:
        address = Address(
            line1="",
            line2="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
        )
        assert address.line1 == "10, avenue des Champs Elysées"
        assert address.line2 is None

    def test_country_subdivision_validation(self) -> None:
        Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
            subdivision_code="FR-75",
        )

        with pytest.raises(InvalidAddress) as expt:
            Address(
                line1="10, avenue des Champs Elysées",
                postal_code="75008",
                city_name="Paris",
                country_code="FR",
                subdivision_code="BE-BRU",
            )
        err = expt.value
        assert err.required_fields == set()
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == {("country_code", "subdivision_code")}
        assert "required" not in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" in str(err)

        with pytest.raises(InvalidAddress) as expt:
            Address(
                line1="10, avenue des Champs Elysées",
                postal_code="75008",
                city_name="Paris",
                country_code="FR",
                subdivision_code="US-GU",
            )
        err = expt.value
        assert err.required_fields == set()
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == {("country_code", "subdivision_code")}
        assert "required" not in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" in str(err)

    @pytest.mark.parametrize(
        "address",
        [
            # Perfect, already normalized country and subdivision.
            Address(
                line1="1273 Pale San Vitores Road",
                postal_code="96913",
                city_name="Tamuning",
                country_code="GU",
                subdivision_code="US-GU",
            ),
            # Non-normalized country.
            Address(
                line1="1273 Pale San Vitores Road",
                postal_code="96913",
                city_name="Tamuning",
                country_code="US",
                subdivision_code="US-GU",
            ),
            # Country only, from which we guess the subdivision.
            Address(
                line1="1273 Pale San Vitores Road",
                postal_code="96913",
                city_name="Tamuning",
                country_code="GU",
            ),
            # Subdivision only, from which we derive the country.
            Address(
                line1="1273 Pale San Vitores Road",
                postal_code="96913",
                city_name="Tamuning",
                subdivision_code="US-GU",
            ),
        ],
    )
    def test_country_subdivision_reconciliation(self, address: Address) -> None:
        assert address.line1 == "1273 Pale San Vitores Road"
        assert address.line2 is None
        assert address.postal_code == "96913"
        assert address.city_name == "Tamuning"
        assert address.country_code == "GU"
        assert address.subdivision_code == "US-GU"

    def test_country_alias_normalization(self) -> None:
        address = Address(
            line1="Barack 31",
            postal_code="XXX No postal code on this atoll",
            city_name="Clipperton Island",
            country_code="CP",
        )  # This is actually a non existing country code
        assert address.country_code == "FR"
        assert address.subdivision_code == "FR-CP"

        address = Address(
            line1="Barack 31",
            postal_code="XXX No postal code on this atoll",
            city_name="Clipperton Island",
            subdivision_code="FR-CP",
        )
        assert address.country_code == "FR"
        assert address.subdivision_code == "FR-CP"

        address = Address(
            line1="16 rue de Millo",
            postal_code="98000",
            city_name="La Condamine",
            subdivision_code="MC-CO",
        )
        assert address.country_code == "MC"
        assert address.subdivision_code == "MC-CO"

        # Test normalization of non-normalized country of a subdivision
        # of a country aliased subdivision.
        address1 = Address(
            line1="Bunker building 746",
            postal_code="XXX No postal code on this atoll",
            city_name="Johnston Atoll",
            country_code="UM",
            subdivision_code="UM-67",
        )
        address2 = Address(
            line1="Bunker building 746",
            postal_code="XXX No postal code on this atoll",
            city_name="Johnston Atoll",
            subdivision_code="UM-67",
        )
        # address3 = Address(
        #     line1='Bunker building 746',
        #     postal_code='XXX No postal code on this atoll',
        #     city_name='Johnston Atoll',
        #     country_code='US',
        #     subdivision_code='UM-67')
        for address in [address1, address2]:  # address3
            assert address.country_code == "UM"
            assert address.subdivision_code == "UM-67"

        # Test normalization of non-normalized country of a subdivision
        # aliased to a subdivision.
        address1 = Address(
            line1="Kaya Grandi 67",
            postal_code="XXX No postal code on Bonaire",
            # city_name='Kralendijk',
            city_name="Bonaire",
            country_code="BQ",
            subdivision_code="BQ-BO",
        )
        address2 = Address(
            line1="Kaya Grandi 67",
            postal_code="XXX No postal code on Bonaire",
            city_name="Bonaire",
            subdivision_code="BQ-BO",
        )
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
        for address in [address1, address2]:  # address3, address4, address5, address6
            assert address.country_code == "BQ"
            assert address.subdivision_code == "BQ-BO"

        # Test normalization of TW subdivisions.
        address1 = Address(
            line1="No.276, Zhongshan Rd.",
            postal_code="95001",
            city_name="Taitung City",
            country_code="TW",
            subdivision_code="TW-TTT",
        )
        address2 = Address(
            line1="No.276, Zhongshan Rd.",
            postal_code="95001",
            city_name="Taitung City",
            subdivision_code="TW-TTT",
        )
        # address3 = Address(
        #     line1='No.276, Zhongshan Rd.',
        #     postal_code='95001',
        #     city_name='Taitung City',
        #     country_code='CN',
        #     subdivision_code='TW-TTT')
        for address in [address1, address2]:  # address3]:
            assert address.country_code == "TW"
            assert address.country_name == "Taiwan"
            assert address.subdivision_code == "TW-TTT"

    def test_subdivision_derived_fields(self) -> None:
        address = Address(
            line1="31, place du Théatre",
            postal_code="59000",
            city_name="Lille",
            subdivision_code="FR-59",
        )

        assert address.subdivision == subdivisions.get(code="FR-59")
        assert address.subdivision_code == "FR-59"
        assert address.subdivision_name == "Nord"
        assert address.subdivision_type_name == "Metropolitan department"
        assert address.subdivision_type_id == "metropolitan_department"

        assert address.metropolitan_department == subdivisions.get(code="FR-59")
        assert address.metropolitan_department_area_code == "FR-59"
        assert address.metropolitan_department_name == "Nord"
        assert address.metropolitan_department_type_name == "Metropolitan department"

        assert address.metropolitan_region == subdivisions.get(code="FR-HDF")
        assert address.metropolitan_region_area_code == "FR-HDF"
        assert address.metropolitan_region_name == "Hauts-de-France"
        assert address.metropolitan_region_type_name == "Metropolitan region"

        assert address.country == countries.get(alpha_2="FR")
        assert address.country_code == "FR"
        assert address.country_name == "France"

    @pytest.mark.parametrize("replace_city_name", [True, False])
    def test_subdivision_derived_city_fields(self, replace_city_name: bool) -> None:
        address = Address(
            line1="2 King Edward Street",
            postal_code="EC1A 1HQ",
            subdivision_code="GB-LND",
            replace_city_name=replace_city_name,
        )

        assert address.subdivision == subdivisions.get(code="GB-LND")
        assert address.subdivision_code == "GB-LND"
        assert address.subdivision_name == "London, City of"
        assert address.subdivision_type_name == "City corporation"
        assert address.subdivision_type_id == "city"

        assert address.city == subdivisions.get(code="GB-LND")
        assert address.city_area_code == "GB-LND"
        assert address.city_name == "London, City of"
        assert address.city_type_name == "City corporation"

        assert address.country_code == "GB"

    def test_subdivision_derived_country(self) -> None:
        address = Address(
            line1="Senate House",
            line2="Tyndall Avenue",
            postal_code="BS8 1TH",
            city_name="Bristol",
            subdivision_code="GB-BST",
        )

        assert address.subdivision == subdivisions.get(code="GB-BST")
        assert address.subdivision_code == "GB-BST"
        assert address.subdivision_name == "Bristol, City of"
        assert address.subdivision_type_name == "Unitary authority"
        assert address.subdivision_type_id == "unitary_authority"

        assert address.country_code == "GB"

    def test_city_override_by_subdivision(self) -> None:
        Address(
            line1="2 King Edward Street",
            postal_code="EC1A 1HQ",
            city_name="London, City of",
            subdivision_code="GB-LND",
        )

        with pytest.raises(InvalidAddress) as expt:
            Address(
                line1="2 King Edward Street",
                postal_code="EC1A 1HQ",
                city_name="Paris",
                subdivision_code="GB-LND",
            )
        err = expt.value
        assert err.required_fields == set()
        assert err.invalid_fields == {}
        assert err.inconsistent_fields == {("city_name", "subdivision_code")}
        assert "required" not in str(err)
        assert "invalid" not in str(err)
        assert "inconsistent" in str(err)

        # Make sure no error is raised when using replace_city_name=False
        address = Address(
            line1="2 King Edward Street",
            postal_code="EC1A 1HQ",
            city_name="Paris",
            subdivision_code="GB-LND",
            replace_city_name=False,
        )
        assert address.city_name == "Paris"

    def test_non_strict_mode_normalization(self) -> None:
        # Test city name override by subdivision code.
        address = Address(
            strict=False,
            line1="2 King Edward Street",
            postal_code="EC1A 1HQ",
            city_name="Dummy city",
            subdivision_code="GB-LND",
        )
        assert address.line1 == "2 King Edward Street"
        assert address.line2 is None
        assert address.postal_code == "EC1A 1HQ"
        assert address.city_name == "London, City of"
        assert address.country_code == "GB"
        assert address.subdivision_code == "GB-LND"

        address = Address(
            strict=False,
            line1="4 Bulevardul Nicolae Bålcescu",
            postal_code="010051",
            city_name="Dummy city",
            subdivision_code="RO-B",
        )
        assert address.line1 == "4 Bulevardul Nicolae Bålcescu"
        assert address.line2 is None
        assert address.postal_code == "010051"
        assert address.city_name == "București"
        assert address.country_code == "RO"
        assert address.subdivision_code == "RO-B"

        address = Address(
            strict=False,
            line1="15 Ngô Quyền",
            postal_code="10000",
            city_name="Dummy city",
            subdivision_code="VN-HN",
        )
        assert address.line1 == "15 Ngô Quyền"
        assert address.line2 is None
        assert address.postal_code == "10000"
        assert address.city_name == "Hà Nội"
        assert address.country_code == "VN"
        assert address.subdivision_code == "VN-HN"

        # Test country override by subdivision code.
        address = Address(
            strict=False,
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
            subdivision_code="BE-BRU",
        )
        assert address.line1 == "10, avenue des Champs Elysées"
        assert address.line2 is None
        assert address.postal_code == "75008"
        assert address.city_name == "Paris"
        assert address.country_code == "BE"
        assert address.subdivision_code == "BE-BRU"

        address = Address(
            strict=False,
            line1="Barack 31",
            postal_code="XXX No postal code",
            city_name="Clipperton Island",
            country_code="CP",
            subdivision_code="FR-CP",
        )
        assert address.line1 == "Barack 31"
        assert address.line2 is None
        assert address.postal_code == "XXX NO POSTAL CODE"
        assert address.city_name == "Clipperton Island"
        assert address.country_code == "FR"
        assert address.subdivision_code == "FR-CP"

        # Test both city and country override by subdivision code.
        address = Address(
            strict=False,
            line1="9F., No. 290, Sec. 4, Zhongxiao E. Rd.",
            postal_code="10694",
            city_name="Dummy city",
            country_code="FR",
            subdivision_code="TW-TNN",
        )
        assert address.line1 == "9F., No. 290, Sec. 4, Zhongxiao E. Rd."
        assert address.line2 is None
        assert address.postal_code == "10694"
        assert address.city_name == "Tainan"
        assert address.country_code == "TW"
        assert address.country_name == "Taiwan"
        assert address.subdivision_code == "TW-TNN"

    def test_all_country_codes(self) -> None:
        """Validate & render random addresses with all supported countries."""
        for country_code in supported_country_codes():
            address = random_address()
            address.country_code = country_code
            address.subdivision_code = None
            address.normalize()
            address.validate()
            address.render()

    def test_all_territory_codes(self) -> None:
        """Validate & render random addresses with all supported territories."""
        for territory_code in supported_subdivision_codes():
            address = random_address()
            address.country_code = None
            address.subdivision_code = territory_code
            address.normalize(strict=False)
            address.validate()
            address.render()

        for territory_code in supported_country_codes():
            address = random_address()
            address.country_code = territory_code
            address.subdivision_code = None
            address.normalize(strict=False)
            address.validate()
            address.render()
