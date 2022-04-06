#
# Copyright (c) 2013-2018 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause
import re

from pycountry import countries, subdivisions

from postal_address.address import Address, subdivision_metadata, subdivision_type_id
from postal_address.territory import (
    COUNTRY_ALIASES,
    FOREIGN_TERRITORIES_MAPPING,
    RESERVED_COUNTRY_CODES,
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
)

PYCOUNTRY_CC = {country.alpha_2 for country in countries}
PYCOUNTRY_SUB = {subdiv.code for subdiv in subdivisions}


class TestTerritory:
    # Test territory utils

    def test_supported_territory_codes(self) -> None:
        assert "FR" in supported_territory_codes()
        assert "FR-59" in supported_territory_codes()
        assert "FRE" not in supported_territory_codes()

    def test_supported_country_codes(self) -> None:
        assert "FR" in supported_country_codes()
        assert "FX" in supported_country_codes()
        assert "UK" in supported_country_codes()
        assert "FR-59" not in supported_country_codes()

    def test_supported_subdivision_codes(self) -> None:
        assert "FR-59" in supported_subdivision_codes()
        assert "FR" not in supported_subdivision_codes()
        assert "UK" not in supported_subdivision_codes()

    def test_territory_code_overlap(self) -> None:
        # Check that no codes from classifications we rely on are overlapping
        assert not PYCOUNTRY_CC & PYCOUNTRY_SUB

    def test_foreign_territory_definition(self) -> None:
        for foreign, country in FOREIGN_TERRITORIES_MAPPING.items():
            assert foreign in PYCOUNTRY_CC
            assert country in PYCOUNTRY_CC

    def test_territory_exception_definition(self) -> None:
        # Check that all codes used in constants to define exceptional
        # treatment are valid and recognized.
        for subdiv_code, alias_code in SUBDIVISION_COUNTRIES.items():
            assert subdiv_code in supported_subdivision_codes()
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            assert alias_code in PYCOUNTRY_CC.union(PYCOUNTRY_SUB)

        for country_code, alias_code in COUNTRY_ALIASES.items():
            # Aliased country codes are not supposed to be supported by
            # pycountry, as it's the main reason to define an alias in the
            # first place.
            assert country_code not in PYCOUNTRY_CC
            # Target alias is supposed to be a valid subdivision or country
            # recognized by pycountry right away.
            assert alias_code in PYCOUNTRY_CC.union(PYCOUNTRY_SUB)

        for country_code, alias_code in RESERVED_COUNTRY_CODES.items():
            assert country_code not in PYCOUNTRY_CC
            assert alias_code in PYCOUNTRY_CC.union(PYCOUNTRY_SUB)

    def test_country_from_subdivision(self) -> None:
        # Test reconciliation of ISO 3166-2 and ISO 3166-1 country codes.
        for subdiv_code in SUBDIVISION_COUNTRIES.keys():
            target_code = SUBDIVISION_COUNTRIES[subdiv_code]
            if len(target_code) != 2:
                target_code = subdivisions.get(code=target_code).country_code
            assert country_from_subdivision(subdiv_code) == target_code
        for subdiv_code in PYCOUNTRY_SUB.difference(SUBDIVISION_COUNTRIES):
            assert (
                country_from_subdivision(subdiv_code)
                == subdivisions.get(code=subdiv_code).country_code
            )

    def test_default_subdivision_code(self) -> None:
        assert default_subdivision_code("FR") is None
        assert default_subdivision_code("GU") == "US-GU"
        assert default_subdivision_code("SJ") is None

    def test_territory_children_codes(self) -> None:
        assert territory_children_codes("GQ") == {
            "GQ-C",
            "GQ-I",
            "GQ-AN",
            "GQ-BN",
            "GQ-BS",
            "GQ-CS",
            "GQ-DJ",
            "GQ-KN",
            "GQ-LI",
            "GQ-WN",
        }
        assert territory_children_codes("GQ-I") == {"GQ-AN", "GQ-BN", "GQ-BS"}
        assert territory_children_codes("GQ-AN") == set()
        assert territory_children_codes("GQ-AN", include_self=True) == {"GQ-AN"}

    def test_territory_parents_codes(self) -> None:
        assert list(territory_parents_codes("FR-59")) == ["FR-59", "FR-HDF", "FR"]
        assert list(territory_parents_codes("FR-59", include_country=False)) == [
            "FR-59",
            "FR-HDF",
        ]
        assert list(territory_parents_codes("FR")) == ["FR"]
        assert list(territory_parents_codes("FR", include_country=False)) == []

    def test_alias_normalization(self) -> None:
        # Check country alias to a country.
        assert list(territory_parents_codes("DG")) == ["IO"]

        # Check country alias to a subdivision.
        assert list(territory_parents_codes("SH-TA")) == ["SH-TA", "SH"]
        assert list(territory_parents_codes("TA")) == ["SH-TA", "SH"]

        # Check subdivision alias to a country.
        assert list(territory_parents_codes("MQ")) == ["MQ"]
        assert list(territory_parents_codes("FR-MQ")) == ["MQ"]

        # Check subdivision alias to a subdivision.
        assert list(territory_parents_codes("BQ-SE")) == ["BQ-SE", "BQ"]
        assert list(territory_parents_codes("NL-BQ3")) == ["BQ-SE", "BQ"]

        # Non 1:1 alias mapping should be non-destructive and keep the
        # subdivision.
        # assert list(territory_parents_codes('NO-22')) == ['NO-22', 'SJ']

    def test_country_aliases(self) -> None:
        assert country_aliases("UM-67") == {"US", "UM"}
        assert country_aliases("UM") == {"US", "UM"}
        assert country_aliases("US") == {"US"}

        assert country_aliases("BQ-BO") == {"NL", "BQ"}
        assert country_aliases("NL-BQ2") == {"NL", "BQ"}

        assert country_aliases("NO-21") == {"SJ", "NO"}

        assert country_aliases("DG") == {"DG", "IO", "GB"}
        assert country_aliases("IO") == {"IO", "GB"}

        assert country_aliases("FR") == {"FR"}

        # CP is not an official ISO-3166 country code
        # assert country_aliases('FR-CP') == {'FR', 'CP'}
        # assert country_aliases('CP') == {'FR', 'CP'}

        assert country_aliases("FR-RE") == {"FR", "RE"}
        assert country_aliases("RE") == {"FR", "RE"}

        assert country_aliases("GB") == {"GB"}
        assert country_aliases("UK") == {"UK", "GB"}

        assert country_aliases("GR") == {"GR"}
        assert country_aliases("EL") == {"EL", "GR"}

        assert country_aliases("IM") == {"IM", "GB"}

        assert country_aliases("MC") == {"MC"}

    def test_subdivision_type_id_conversion(self) -> None:
        # Conversion of subdivision types into IDs must be python friendly
        attribute_regexp = re.compile("[a-z][a-z0-9_]*$")
        for subdiv in subdivisions:
            assert attribute_regexp.match(subdivision_type_id(subdiv))

    def test_subdivision_type_id_city_classification(self) -> None:
        city_like_subdivisions = [
            "TM-S",  # Aşgabat, Turkmenistan, City
            "TW-CYI",  # Chiay City, Taiwan, Municipality
            "TW-TPE",  # Taipei City, Taiwan, Special Municipality
            "ES-ML",  # Melilla, Spain, Autonomous city
            "GB-LND",  # City of London, United Kingdom, City corporation
            "KP-01",  # P’yŏngyang, North Korea, Capital city
            "KP-13",  # Nasŏn (Najin-Sŏnbong), North Korea, Special city
            "KR-11",  # Seoul Teugbyeolsi, South Korea, Capital Metropolitan
            # City
            "HU-HV",  # Hódmezővásárhely, Hungary, City with county rights
            "LV-RIX",  # Rīga, Latvia, Republican City
            "ME-15",  # Plužine, Montenegro, Municipality
            "NL-BQ1",  # Bonaire, Netherlands, Special municipality
            "KH-12",  # Phnom Penh, Cambodia, Autonomous municipality
        ]
        for subdiv_code in city_like_subdivisions:
            assert subdivision_type_id(subdivisions.get(code=subdiv_code)) == "city"

    def test_subdivision_type_id_collision(self) -> None:
        # The subdivision metadata IDs we derived from subdivision types should
        # not collide with Address class internals.
        simple_address = Address(
            line1="10, avenue des Champs Elysées",
            postal_code="75008",
            city_name="Paris",
            country_code="FR",
        )

        # Check each subdivision metadata.
        for subdiv in subdivisions:

            # XXX ISO 3166-2 reuse the country type as subdivisions.
            # We really need to add proper support for these cases, as we did
            # for cities.
            if subdivision_type_id(subdiv) in ["country"]:
                continue

            for metadata_id in subdivision_metadata(subdiv):
                # Check collision with any atrribute defined on Address class.
                if metadata_id in Address.SUBDIVISION_METADATA_WHITELIST:
                    assert hasattr(simple_address, metadata_id)
                else:
                    assert not hasattr(simple_address, metadata_id)

    def test_subdivision_parent_code(self) -> None:
        assert subdivisions.get(code="CZ-205").parent_code == "CZ-20"

    def test_foreign_territory_mapping(self) -> None:
        assert territory_attachment("GP") == "FR"
        assert territory_attachment("BQ") == "NL"

    def test_normalize_territory_code(self) -> None:
        assert normalize_territory_code("EL") == "GR"
        assert normalize_territory_code("FX") == "FR"
        assert normalize_territory_code("CN-TW") == "TW"
        # Sub-territories will not change by default
        assert normalize_territory_code("BQ") == "BQ"
        assert normalize_territory_code("FR-GP") == "GP"

        assert normalize_territory_code("NL-BQ1") == "BQ-BO"

    def test_normalize_territory_code_with_foreign_territory(self) -> None:
        resolved = normalize_territory_code("BQ", resolve_top_country=True)
        assert resolved == "NL"

        resolved = normalize_territory_code("VI", resolve_top_country=True)
        assert resolved == "US"

        resolved = normalize_territory_code("FR-GP", resolve_top_country=True)
        assert resolved == "FR"

        resolved = normalize_territory_code("NL-BQ1", resolve_top_country=True)

        assert resolved == "BQ-BO"
