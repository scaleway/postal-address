# Copyright (c) 2013-2022 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#                         Gilles Dartiguelongue <gdartiguelongue@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

"""Utilities for address parsing and rendering.

Only provides address validation for the moment, but may be used in the future
for localized rendering (see issue #4).
"""
import contextlib
import random
import re
from typing import (
    Any,
    Dict,
    ItemsView,
    Iterator,
    KeysView,
    Optional,
    Set,
    Tuple,
    ValuesView,
)

import faker
import pycountry
from boltons.strutils import slugify
from pycountry import countries, subdivisions

from .territory import (
    country_from_subdivision,
    default_subdivision_code,
    normalize_territory_code,
    territory_children_codes,
    territory_parents,
)


class InvalidAddress(ValueError):
    """Custom exception providing details about address failing validation."""

    def __init__(
        self,
        required_fields: Optional[Set[str]] = None,
        invalid_fields: Optional[Dict[str, str]] = None,
        inconsistent_fields: Optional[Set[Tuple[str, ...]]] = None,
        extra_msg: Optional[str] = None,
    ):
        """Exception keep internally a classification of bad fields."""
        super(InvalidAddress, self).__init__()
        self.required_fields = required_fields if required_fields else set()
        self.invalid_fields = invalid_fields if invalid_fields else {}
        self.inconsistent_fields = inconsistent_fields if inconsistent_fields else set()
        self.extra_msg = extra_msg

    def __str__(self) -> str:
        """Human-readable error."""
        reasons = []
        if self.required_fields:
            required_fields_str = ", ".join(sorted(self.required_fields))
            be = "is" if len(self.required_fields) == 1 else "are"
            reasons.append(f"{required_fields_str} {be} required")
        if self.invalid_fields:
            invalid_fields_str = (
                ", ".join(
                    sorted([f"{k}={v!r}" for k, v in self.invalid_fields.items()])
                ),
            )
            be = "is" if len(self.required_fields) == 1 else "are"
            reasons.append(f"{invalid_fields_str} {be} invalid")
        if self.inconsistent_fields:
            for field_id_1, field_id_2 in sorted(self.inconsistent_fields):
                reasons.append(f"{field_id_1} is inconsistent with {field_id_2}")
        if self.extra_msg:
            reasons.append(self.extra_msg)
        return f"{'; '.join(reasons)}."


class Address:
    """Define a postal address.

    All addresses share the following fields:
    * ``line1`` (required): a non-constrained string.
    * ``line2``: a non-constrained string.
    * ``postal_code`` (required): a non-constrained string (see issue #2).
    * ``city_name`` (required): a non-constrained string.
    * ``country_code`` (required): an ISO 3166-1 alpha-2 code.
    * ``subdivision_code``: an ISO 3166-2 code.

    At instanciation, the ``normalize()`` method is called. The latter try to
    clean-up the data and populate empty fields that can be derived from
    others. As such, ``city_name`` can be overriden by ``subdivision_code``.
    See the internal ``SUBDIVISION_METADATA_WHITELIST`` constant.

    If inconsistencies are found at the normalization step, they are left as-is
    to give a chance to the ``validate()`` method to catch them. Which means
    that, after each normalization (including the one at initialization), it is
    your job to call the ``validate()`` method manually to check that the
    address is good.
    """

    # Fields common to any postal address. Those are free-form fields, allowed
    # to be set directly by the user, although their values might be normalized
    # and clean-up automatticaly by the validation method.
    BASE_FIELD_IDS = frozenset(
        [
            "line1",
            "line2",
            "postal_code",
            "city_name",
            "country_code",
            "subdivision_code",
        ]
    )

    # List of subdivision-derived metadata IDs which are allowed to collide
    # with base field IDs.
    SUBDIVISION_METADATA_WHITELIST = frozenset(["city_name"])
    assert SUBDIVISION_METADATA_WHITELIST.issubset(BASE_FIELD_IDS)

    # Fields tested on validate().
    REQUIRED_FIELDS = frozenset(["line1", "postal_code", "city_name", "country_code"])
    assert REQUIRED_FIELDS.issubset(BASE_FIELD_IDS)

    def __init__(
        self,
        strict: bool = True,
        replace_city_name: bool = True,
        line1: Optional[str] = None,
        line2: Optional[str] = None,
        postal_code: Optional[str] = None,
        city_name: Optional[str] = None,
        country_code: Optional[str] = None,
        subdivision_code: Optional[str] = None,
        **kwargs: Any,
    ):
        """Set address' individual fields and normalize them.

        By default, normalization is ``strict``.
        """
        # Only common fields are allowed to be set directly.
        unknown_fields = set(kwargs) - self.BASE_FIELD_IDS
        if unknown_fields:
            raise KeyError(
                f"{unknown_fields!r} fields are not allowed to be set freely."
            )

        # Load fields.
        self._fields: Dict[str, Any] = {}

        self.line1 = line1
        self.line2 = line2
        self.postal_code = postal_code
        self.city_name = city_name
        self.country_code = country_code
        self.subdivision_code = subdivision_code

        # Normalize addresses fields.
        self.normalize(strict=strict, replace_city_name=replace_city_name)

    def __repr__(self) -> str:
        """Print all fields available from the address.

        Also include internal fields disguised as properties.
        """
        # Repr all plain fields.
        fields_repr = [f"{k}={v!r}" for k, v in self.items()]
        # Repr all internal properties.
        for internal_id in [
            "valid",
            "empty",
            "country_name",
            "subdivision_name",
            "subdivision_type_name",
            "subdivision_type_id",
        ]:
            fields_repr.append(f"{internal_id}={getattr(self, internal_id)!r}")
        return f"{self.__class__.__name__}({', '.join(sorted(fields_repr))})"

    def __str__(self) -> str:
        return self.render()

    def __getattr__(self, name: str) -> Any:
        """Expose fields as attributes."""
        if name in self._fields:
            return self._fields[name]
        raise AttributeError

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow update of address fields as attributes."""
        if name in self.BASE_FIELD_IDS:
            self[name] = value
            return
        super(Address, self).__setattr__(name, value)

    # Let an address be accessed like a dict of its fields IDs & values.
    # This is a proxy to the internal _fields dict.

    def __len__(self) -> int:
        """Return the number of fields."""
        return len(self._fields)

    def __getitem__(self, key: str) -> Any:
        """Return the value of a field."""
        if not isinstance(key, str):
            raise TypeError
        return self._fields[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a field's value.

        Only base fields are allowed to be set explicitely.
        """
        if not isinstance(key, str):
            raise TypeError
        if not (isinstance(value, str) or value is None):
            raise TypeError
        if key not in self.BASE_FIELD_IDS:
            raise KeyError
        self._fields[key] = value

    def __delitem__(self, key: str) -> None:
        """Remove a field."""
        if key in self.BASE_FIELD_IDS:
            self._fields[key] = None
        else:
            del self._fields[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over field IDs."""
        yield from self._fields

    def keys(self) -> KeysView[str]:
        """Return a list of field IDs."""
        return self._fields.keys()

    def values(self) -> ValuesView[Any]:
        """Return a list of field values."""
        return self._fields.values()

    def items(self) -> ItemsView[str, Any]:
        """Return a list of field IDs & values."""
        return self._fields.items()

    def render(self, separator: str = "\n") -> str:
        """Render a human-friendly address block.

        The block is composed of:
        * The ``line1`` field rendered as-is if not empty.
        * The ``line2`` field rendered as-is if not empty.
        * A third line made of the postal code, the city name and state name if
          any is set.
        * A fourth optionnal line with the subdivision name if its value does
          not overlap with the city, state or country name.
        * The last line feature country's common name.
        """
        lines = []

        if self.line1:
            lines.append(self.line1)

        if self.line2:
            lines.append(self.line2)

        # Build the third line.
        line3_elements = []
        if self.city_name:
            line3_elements.append(self.city_name)
        if hasattr(self, "state_name"):
            # XXX It might not be a good idea to deduplicate state and city.
            # See: https://en.wikipedia.org/wiki
            # /List_of_U.S._cities_named_after_their_state
            line3_elements.append(self.state_name)
        # Separate city and state by a comma.
        line3_elements = [", ".join(line3_elements)]
        if self.postal_code:
            line3_elements.insert(0, self.postal_code)
        # Separate the leading zip code and the rest by a dash.
        line3 = " - ".join(line3_elements)
        if line3:
            lines.append(line3)

        # Compare the vanilla subdivision name to properties that are based on
        # it and used in the current ``render()`` method to produce a printable
        # address. If none overlap, then print an additional line with the
        # subdivision name as-is to provide extra, non-redundant, territory
        # precision.
        subdiv_based_properties = ["city_name", "state_name", "country_name"]
        subdiv_based_values = [
            getattr(self, prop_id)
            for prop_id in subdiv_based_properties
            if hasattr(self, prop_id)
        ]
        if self.subdivision_name and self.subdivision_name not in subdiv_based_values:
            lines.append(self.subdivision_name)

        # Place the country line at the end.
        if self.country_name:
            lines.append(self.country_name)

        # Render the address block with the provided separator.
        return separator.join(lines)

    def normalize(self, strict: bool = True, replace_city_name: bool = True) -> None:
        """Normalize address fields.

        If values are unrecognized or invalid, they will be set to None.

        By default, the normalization is ``strict``: metadata derived from
        territory's parents are not allowed to overwrite valid address fields
        entered by the user. If set to ``False``, territory-derived values
        takes precedence over user's.

        With ``replace_city_name`` set to False, we will use the value set by
        the user for the city in any case.

        You need to call back the ``validate()`` method afterwards to properly
        check that the fully-qualified address is ready for consumption.
        """
        # Strip postal codes of any characters but alphanumerics, spaces and
        # hyphens.
        if self.postal_code:
            self.postal_code = self.postal_code.upper()
            # Remove unrecognized characters.
            self.postal_code = re.compile(r"[^A-Z0-9 -]").sub("", self.postal_code)
            # Reduce sequences of mixed hyphens and spaces to single hyphen.
            self.postal_code = re.compile(r"[^A-Z0-9]*-+[^A-Z0-9]*").sub(
                "-", self.postal_code
            )
            # Edge case: remove leading and trailing hyphens and spaces.
            self.postal_code = self.postal_code.strip("-")

        # Normalize spaces.
        for field_id, field_value in self.items():
            if isinstance(field_value, str):
                with contextlib.suppress(KeyError):  # usually on 'subdivision_metadata'
                    self[field_id] = " ".join(field_value.split())

        # Reset empty and blank strings.
        empty_fields = [f_id for f_id, f_value in self.items() if not f_value]
        for field_id in empty_fields:
            del self[field_id]

        # Swap lines if the first is empty.
        if self.line2 and not self.line1:
            self.line1, self.line2 = self.line2, self.line1

        # Normalize territory codes. Unrecognized territory codes are reset
        # to None.
        for territory_id in ["country_code", "subdivision_code"]:
            territory_code = getattr(self, territory_id)
            if territory_code:
                try:
                    code = normalize_territory_code(
                        territory_code, resolve_aliases=False
                    )
                except ValueError:
                    code = None
                setattr(self, territory_id, code)

        # Try to set default subdivision from country if not set.
        if self.country_code and not self.subdivision_code:
            self.subdivision_code = default_subdivision_code(self.country_code)
            # If the country set its own subdivision, reset it. It will be
            # properly re-guessed below.
            if self.subdivision_code:
                self.country_code = None

        # Automatically populate address fields with metadata extracted from
        # all subdivision parents.
        if self.subdivision_code:
            parent_metadata = {
                # All subdivisions have a parent country.
                "country_code": country_from_subdivision(self.subdivision_code)
            }

            # Add metadata of each subdivision parent.
            for parent_subdiv in territory_parents(
                self.subdivision_code, include_country=False
            ):
                parent_metadata.update(subdivision_metadata(parent_subdiv))

            if self.city_name and not replace_city_name:
                parent_metadata.pop("city_name", None)

            # Parent metadata are not allowed to overwrite address fields
            # if not blank, unless strict mode is de-activated.
            if strict:
                for field_id, new_value in parent_metadata.items():
                    # New metadata are not allowed to be blank.
                    assert new_value
                    current_value = self._fields.get(field_id)
                    if current_value and field_id in self.BASE_FIELD_IDS:

                        # Build the list of substitute values that are
                        # equivalent to our new normalized target.
                        alias_values = {new_value}
                        if field_id == "country_code":
                            # Allow normalization if the current country code
                            # is the direct parent of a subdivision which also
                            # have its own country code.
                            alias_values.add(
                                subdivisions.get(
                                    code=self.subdivision_code
                                ).country_code
                            )

                        # Change of current value is allowed if it is a direct
                        # substitute to our new normalized value.
                        if current_value not in alias_values:
                            raise InvalidAddress(
                                inconsistent_fields={
                                    tuple(sorted((field_id, "subdivision_code")))
                                },
                                extra_msg=(
                                    f"{self.subdivision_code} subdivision is trying to "
                                    f"replace {field_id}={current_value!r} field by "
                                    f"{field_id}={new_value!r}"
                                ),
                            )

            self._fields.update(parent_metadata)

    def validate(self) -> None:
        """Check fields consistency and requirements in one go.

        Properly check that fields are consistent between themselves, and only
        raise an exception at the end, for the whole address object. Our custom
        exception will provide a detailed status of bad fields.
        """
        required_fields = self.check_required_fields()
        invalid_fields = self.check_invalid_fields(required_fields)
        inconsistent_fields = self.check_inconsistent_fields(
            required_fields, invalid_fields
        )

        # Raise our custom exception if any value is wrong.
        if required_fields or invalid_fields or inconsistent_fields:
            raise InvalidAddress(required_fields, invalid_fields, inconsistent_fields)

    def check_required_fields(self) -> Set[str]:
        """Check that all required fields are set.

        :return: The set of unset thus required fields.
        """
        required_fields = set()
        for field_id in self.REQUIRED_FIELDS:
            if not getattr(self, field_id):
                required_fields.add(field_id)
        return required_fields

    def check_invalid_fields(self, required_fields: Set[str]) -> Dict[str, str]:
        """Check all fields for invalidity, only if not previously flagged as required.

        :param required_fields:
        """
        invalid_fields: Dict[str, str] = {}
        if "country_code" not in required_fields and self.country_code:
            country = countries.get(alpha_2=self.country_code)
            if country is None:
                invalid_fields["country_code"] = self.country_code

        if self.subdivision_code and "subdivision_code" not in required_fields:
            subdiv = subdivisions.get(code=self.subdivision_code)
            if subdiv is None:
                invalid_fields["subdivision_code"] = self.subdivision_code
        return invalid_fields

    def check_inconsistent_fields(
        self, required_fields: Set[str], invalid_fields: Dict[str, str]
    ) -> Set[Tuple[str, ...]]:
        """Check country consistency.

        Check country consistency against subdivision, only if none of the two
        fields were previously flagged as required or invalid.

        :param required_fields: The set of missing required fields.
        :param invalid_fields: The set of invalid fields.
        :return:
        """
        inconsistent_fields = set()
        any_wrong_field = required_fields.union(invalid_fields)
        consistency_fields = {"country_code", "subdivision_code"}
        inconsistency = consistency_fields & any_wrong_field
        if not inconsistency and not self.valid_subdivision_country():
            inconsistent_fields.add(tuple(sorted(consistency_fields)))
        return inconsistent_fields

    def valid_subdivision_country(self) -> bool:
        """Validate subdivision's country.

        Validate that the country attached to the subdivision is
        the same as the Address' country_code.

        :return: True if the subdivision country is the same as the country,
        False otherwise.
        """
        if not self.subdivision_code:
            return True
        inferred_country = country_from_subdivision(self.subdivision_code)
        return inferred_country == self.country_code

    @property
    def valid(self) -> bool:
        """Return a boolean indicating if the address is valid."""
        try:
            self.validate()
        except InvalidAddress:
            return False
        return True

    @property
    def empty(self) -> bool:
        """Return True only if all fields are empty."""
        return all(not value for value in set(self.values()))

    def __bool__(self) -> bool:
        """Consider the instance to be True if not empty."""
        return not self.empty

    @property
    def country(self) -> Optional[pycountry.db.Database]:
        """Return country object."""
        if self.country_code:
            return countries.get(alpha_2=self.country_code)
        return None

    @property
    def country_name(self) -> Optional[str]:
        """Return country's name.

        Common name always takes precedence over the default name, as the
        latter isoften pompous, and sometimes false (i.e. not in sync with
        current political situation).
        """
        if self.country:
            if hasattr(self.country, "common_name"):
                return self.country.common_name
            return self.country.name
        return None

    @property
    def subdivision(self) -> Optional[pycountry.Subdivision]:
        """Return subdivision object."""
        if self.subdivision_code:
            return subdivisions.get(code=self.subdivision_code)
        return None

    @property
    def subdivision_name(self) -> Optional[str]:
        """Return subdivision's name."""
        if self.subdivision:
            return self.subdivision.name
        return None

    @property
    def subdivision_type_name(self) -> Optional[str]:
        """Return subdivision's type human-readable name."""
        if self.subdivision:
            return self.subdivision.type
        return None

    @property
    def subdivision_type_id(self) -> Optional[str]:
        """Return subdivision's type as a Python-friendly ID string."""
        if self.subdivision:
            return subdivision_type_id(self.subdivision)
        return None


# Address utils.


def random_address(locale: Optional[str] = None) -> Address:
    """Return a random, valid address.

    A ``locale`` parameter try to produce a localized-consistent address. Else
    a random locale is picked-up.
    """
    # XXX Exclude 'ar_PS' that doesn't work currently (it's defined in Faker
    # but not in pycountry).
    # See: https://github.com/scaleway/postal-address/issues/20
    while locale in [None, "ar_PS"]:
        locale = random.choice(list(faker.config.AVAILABLE_LOCALES))
    fake = faker.Faker(locale=locale)

    components = {
        "line1": fake.street_address(),
        "line2": fake.sentence(),
        "postal_code": fake.postcode(),
        "city_name": fake.city(),
        "country_code": fake.country_code(),
    }

    subdiv_codes = list(territory_children_codes(components["country_code"]))
    if subdiv_codes:
        components["subdivision_code"] = random.choice(subdiv_codes)

    return Address(strict=False, **components)


# Subdivisions utils.


def subdivision_type_id(subdivision: pycountry.Subdivision) -> str:
    r"""Normalize subdivision type name into a Python-friendly ID.

    Here is the list of all subdivision types defined by ``pycountry`` v1.8::

        >>> print('\n'.join(sorted({x.type for x in subdivisions})))
        Administration
        Administrative Region
        Administrative Territory
        Administrative atoll
        Administrative region
        Arctic Region
        Area
        Autonomous City
        Autonomous District
        Autonomous Province
        Autonomous Region
        Autonomous city
        Autonomous community
        Autonomous municipality
        Autonomous province
        Autonomous region
        Autonomous republic
        Autonomous sector
        Autonomous territorial unit
        Borough
        Canton
        Capital District
        Capital Metropolitan City
        Capital Territory
        Capital city
        Capital district
        Capital territory
        Chains (of islands)
        City
        City corporation
        City with county rights
        Commune
        Constitutional province
        Council area
        Country
        County
        Department
        Dependency
        Development region
        District
        District council area
        Division
        Economic Prefecture
        Economic region
        Emirate
        Entity
        Federal Dependency
        Federal District
        Federal Territories
        Federal district
        Geographical Entity
        Geographical region
        Geographical unit
        Governorate
        Included for completeness
        Indigenous region
        Island
        Island council
        Island group
        Local council
        London borough
        Metropolitan cities
        Metropolitan department
        Metropolitan district
        Metropolitan region
        Municipalities
        Municipality
        Oblast
        Outlying area
        Overseas region/department
        Overseas territorial collectivity
        Parish
        Popularates
        Prefecture
        Province
        Quarter
        Rayon
        Region
        Regional council
        Republic
        Republican City
        Self-governed part
        Special District
        Special Municipality
        Special Region
        Special administrative region
        Special city
        Special island authority
        Special municipality
        Special zone
        State
        Territorial unit
        Territory
        Town council
        Two-tier county
        Union territory
        Unitary authority
        Unitary authority (England)
        Unitary authority (Wales)
        district
        state
        zone

    This method transform and normalize any of these into Python-friendly IDs.
    """
    type_id = slugify(subdivision.type)

    # Any occurence of the 'city' or 'municipality' string in the type
    # overrides its classification to a city.
    if {"city", "municipality"} & set(type_id.split("_")):
        type_id = "city"

    return type_id


def subdivision_metadata(subdivision: pycountry.Subdivision) -> Dict[str, str]:
    """Return a serialize dict of subdivision metadata.

    Metadata IDs are derived from subdivision type.
    """
    subdiv_type_id = subdivision_type_id(subdivision)
    metadata = {
        str(subdiv_type_id): subdivision,
        # Rename 'code' to 'area_code' to avoid overriding 'country_code'
        # See https://github.com/scaleway/postal-address/issues/16
        f"{subdiv_type_id}_area_code": subdivision.code,
        f"{subdiv_type_id}_name": subdivision.name,
        f"{subdiv_type_id}_type_name": subdivision.type,
    }

    # Check that we are not producing metadata IDs colliding with address
    # fields.
    assert (
        not set(metadata)
        .difference(Address.SUBDIVISION_METADATA_WHITELIST)
        .issubset(Address.BASE_FIELD_IDS)
    )

    return metadata
