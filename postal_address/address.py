# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2015 Online SAS and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@ocs.online.net>
#                         Gilles Dartiguelongue <gdartiguelongue@ocs.online.net>
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

u""" Utilities for address parsing and rendering.

.. data:: COUNTRY_ALIASES

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. data:: SUBDIVISION_ALIASES

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. data:: REVERSE_MAPPING

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: supported_territory_codes()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: normalize_territory_code()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: normalize_country_code()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: default_subdivision_code()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: territory_tree()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: territory_parents()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: territory_parents_codes()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

.. function:: country_aliases()

   .. deprecated:: 0.3.0

      Import from ``postal_address.territory`` instead of
      ``postal_address.address``.

"""

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

try:
    basestring
except NameError:  # pragma: no cover
    basestring = (str, bytes)

import warnings

from pycountry import countries, subdivisions
from slugify import slugify

from .territory import country_from_subdivision

# Territory utils below are not used locally but provides backward-
# compatibility following their splitting out of the ``address`` module.
# See issue #8 and commit b7eb50.
warnings.warn(
    'COUNTRY_ALIASES has been moved from postal_address.address to '
    'postal_address.territory.', DeprecationWarning)
warnings.warn(
    'SUBDIVISION_ALIASES has been moved from postal_address.address to '
    'postal_address.territory.', DeprecationWarning)
warnings.warn(
    'REVERSE_MAPPING has been moved from postal_address.address to '
    'postal_address.territory.', DeprecationWarning)
from .territory import (
    COUNTRY_ALIASES,
    SUBDIVISION_ALIASES,
    REVERSE_MAPPING,
)


class Address(object):

    """ Define a postal address.

    Only provides address validation for the moment, but may be used in the
    future for l10n-aware normalization and rendering.

    ``country_code`` is an ISO 3166-1 alpha-2 code.
    ``subdivision_code`` is an ISO 3166-2 code.
    """

    # All normalized IDs and values of postal address components are stored
    # here.
    # _components = {}

    # Base components of postal address. Those are free-form fields, allowed
    # to be set directly by the user, although their values might be normalized
    # and clean-up automatticaly by the validation method.
    BASE_COMPONENT_IDS = frozenset([
        'line1', 'line2', 'postal_code', 'city_name', 'country_code',
        'subdivision_code'])

    # List of subdivision-derived metadata IDs which are allowed to collide
    # with base component IDs.
    SUBDIVISION_METADATA_WHITELIST = frozenset(['city_name'])
    assert SUBDIVISION_METADATA_WHITELIST.issubset(BASE_COMPONENT_IDS)

    # Fields tested on validate().
    REQUIRED_FIELDS = frozenset([
        'line1', 'postal_code', 'city_name', 'country_code'])
    assert REQUIRED_FIELDS.issubset(BASE_COMPONENT_IDS)

    def __init__(self, **kwargs):
        """ Set address' individual components and normalize them. """
        # Only base components are allowed to be set directly.
        unknown_components = set(kwargs).difference(self.BASE_COMPONENT_IDS)
        if unknown_components:
            raise KeyError(
                "{!r} components are not allowed to be set freely.".format(
                    unknown_components))
        # Initialize base components values.
        self._components = dict.fromkeys(self.BASE_COMPONENT_IDS)
        # Load provided components.
        self._components.update(kwargs)
        # Normalize addresses fields.
        self.normalize()

    def __repr__(self):
        """ Print all components of the address. """
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join([
                '{}={!r}'.format(k, v) for k, v in self._components.items()]))

    def __str__(self):
        """ Return a simple string representation of the address block. """
        return self.render()

    def __getattr__(self, name):
        """ Expose components as attributes. """
        if name in self._components or name in self.BASE_COMPONENT_IDS:
            return self._components.get(name, None)
        raise AttributeError

    def __setattr__(self, name, value):
        """ Allow update of address components as an attribute. """
        if name in self.BASE_COMPONENT_IDS:
            self._components[name] = value
            return
        super(Address, self).__setattr__(name, value)

    # Let an address be accessed like a dict of its components IDs & values.

    def __len__(self):
        """ Return the number of components. """
        return len(self._components)

    def __getitem__(self, key):
        """ Return value of a component. """
        if not isinstance(key, basestring):
            raise TypeError
        return self._components[key]

    def __setitem__(self, key, value):
        """ Set a component value. """
        if not isinstance(key, basestring):
            raise TypeError
        if key not in self._components:
            raise KeyError
        self._components[key] = value

    def __delitem__(self, key):
        """ Remove component. """
        if key in self.BASE_COMPONENT_IDS:
            self._components[key] = None
        else:
            del self._components[key]

    def __iter__(self):
        """ Iterate over component IDs. """
        for component_id in self._components:
            yield component_id

    def keys(self):
        """ Return a list of component IDs. """
        return self._components.keys()

    def values(self):
        """ Return a list of component values. """
        return self._components.values()

    def items(self):
        """ Return a list of components IDs & values. """
        return self._components.items()

    def render(self, separator='\n'):
        """ Render a human-friendly address block.

        ``line1`` & ``line2`` are rendered as-is.
        A third line is composed of ``postal_code``, ``city_name`` and
        ``state``.
        The last line feature country's common name.
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
        if hasattr(self, 'state_name'):
            line3_elements.append(self.state_name)
        # Separate city and state by a comma.
        line3_elements = [', '.join(line3_elements)]
        if self.postal_code:
            line3_elements.insert(0, self.postal_code)
        # Separate the leading zip code and the rest by a dash.
        line3 = ' - '.join(line3_elements)
        if line3:
            lines.append(line3)
        # Build the last line.
        if self.country_name:
            lines.append(self.country_name)
        # Render the address block.
        return separator.join(lines)

    def normalize(self):
        """ Normalize address fields.

        If values are unrecognized or invalid, they will be set to None.

        You need to call back ``validate`` method afterwards to properly check
        that the fully-qualified address is valid.
        """
        # Clean-up all fields.
        empty_components = []
        for component_id in self._components:
            # Remove leading and trailing white spaces.
            if isinstance(self._components[component_id], basestring):
                self._components[component_id] = self._components[
                    component_id].strip()
            # Get rid of empty/blank strings.
            if not getattr(self, component_id):
                empty_components.append(component_id)
        for component_id in empty_components:
            del self[component_id]

        # Normalize territory codes. Unrecognized territory codes are reset
        # to None.
        for territory_id in ['country_code', 'subdivision_code']:
            territory_code = getattr(self, territory_id)
            if territory_code:
                try:
                    code = normalize_territory_code(
                        territory_code, resolve_aliases=False)
                except ValueError:
                    code = None
                setattr(self, territory_id, code)

        # Swap lines if the first is empty.
        if self.line2 and not self.line1:
            self.line1, self.line2 = self.line2, self.line1

        # Try to set default subdivision from country if not set.
        if self.country_code and not self.subdivision_code:
            self.subdivision_code = default_subdivision_code(self.country_code)
            # If the country set its own subdivision, reset it. It will be
            # properly re-guessed below.
            if self.subdivision_code:
                self.country_code = None

        # Populate address components with metadata of all subdivision parents.
        if self.subdivision_code:
            parent_metadata = {
                # All subdivisions have a parent country.
                'country_code': country_from_subdivision(
                    self.subdivision_code)}

            # Add metadata of each subdivision parent.
            for parent_subdiv in territory_parents(
                    self.subdivision_code, include_country=False):
                parent_metadata.update(subdivision_metadata(parent_subdiv))

            # Parent metadata are not allowed to overwrite address components
            # if not blank.
            for component_id, new_value in parent_metadata.items():
                assert new_value  # New metadata are not allowed to be blank.
                current_value = self._components.get(component_id)
                if current_value and component_id in self.BASE_COMPONENT_IDS:

                    # Build the list of substitute values that are equivalent
                    # to our new normalized target.
                    alias_values = set([new_value])
                    if component_id == 'country_code':
                        # Allow normalization if the current country code is
                        # the direct parent of a subdivision which also have
                        # its own country code.
                        alias_values.add(subdivisions.get(
                            code=self.subdivision_code).country_code)

                    # Change of current value is allowed if it is a direct
                    # substitute to our new normalized value.
                    if current_value not in alias_values:
                        raise ValueError(
                            "{} subdivision is trying to replace {}={!r} field"
                            " by {}={!r}".format(
                                self.subdivision_code, component_id,
                                current_value, component_id, new_value))

            self._components.update(parent_metadata)

    def validate(self):
        """ Check fields consistency and requirements.

        Properly check that fields are consistent between themselves.
        """

        # Check that the subdivision code exists.
        if self.subdivision_code:
            try:
                subdivisions.get(code=self.subdivision_code)
            except KeyError:
                raise ValueError(
                    "Invalid {!r} subdivision code.".format(
                        self.subdivision_code))

        # Check that the country code exists.
        if self.country_code:
            try:
                countries.get(alpha2=self.country_code)
            except KeyError:
                raise ValueError(
                    "Invalid {!r} country code.".format(self.country_code))

        # Check country consistency against subdivision.
        if self.country_code and self.subdivision_code and \
                country_from_subdivision(
                    self.subdivision_code) != self.country_code:
            raise ValueError(
                "{!r} country is not a parent {!r} subdivision.".format(
                    self.country_code, self.subdivision_code))

        # Check that all required fields are set.
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field):
                raise ValueError("Address requires {}.".format(field))

    @property
    def valid(self):
        """ Return a boolean indicating if the address is valid. """
        try:
            self.validate()
        except ValueError:
            return False
        return True

    @property
    def empty(self):
        """ Return True only if all fields are empty. """
        for value in set(self._components.values()):
            if value:
                return False
        return True

    def __bool__(self):
        """ Consider the instance to be True if not empty. """
        return not self.empty

    def __nonzero__(self):
        """ Python2 retro-compatibility of ``__bool__()``. """
        return self.__bool__()

    @property
    def country(self):
        """ Return country object. """
        if self.country_code:
            return countries.get(alpha2=self.country_code)
        return None

    @property
    def country_name(self):
        """ Return country's name. """
        if self.country:
            return self.country.name
        return None

    @property
    def subdivision(self):
        """ Return subdivision object. """
        if self.subdivision_code:
            return subdivisions.get(code=self.subdivision_code)
        return None

    @property
    def subdivision_name(self):
        """ Return subdivision's name. """
        if self.subdivision:
            return self.subdivision.name
        return None

    @property
    def subdivision_type_name(self):
        """ Return subdivision's type human-readable name. """
        if self.subdivision:
            return self.subdivision.type
        return None

    @property
    def subdivision_type_id(self):
        """ Return subdivision's type as a Python-friendly ID string. """
        if self.subdivision:
            return subdivision_type_id(self.subdivision)
        return None


# Subdivisions utils.

def subdivision_type_id(subdivision):
    """ Normalize subdivision type name into a Python-friendly ID.

    Here is the list of all subdivision types defined by ``pycountry`` v1.8::

        >>> print '\n'.join(sorted(set([x.type for x in subdivisions])))
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

    This method transform and normalize any of these into Python-firendly IDs.
    """
    type_id = slugify(subdivision.type, to_lower=True).replace('-', '_')

    # Any occurence of the 'city' or 'municipality' string in the type
    # overrides its classification as a city.
    if set(['city', 'municipality']).intersection(type_id.split('_')):
        type_id = 'city'

    return type_id


def subdivision_metadata(subdivision):
    """ Return a serialize dict of subdivision metadata.

    Metadata IDs are derived from subdivision type.
    """
    subdiv_type_id = subdivision_type_id(subdivision)
    metadata = {
        '{}'.format(subdiv_type_id): subdivision,
        '{}_code'.format(subdiv_type_id): subdivision.code,
        '{}_name'.format(subdiv_type_id): subdivision.name,
        '{}_type_name'.format(subdiv_type_id): subdivision.type}

    # Check that we are not producing metadata IDs colliding with address
    # components.
    assert not set(metadata).difference(
        Address.SUBDIVISION_METADATA_WHITELIST).issubset(
            Address.BASE_COMPONENT_IDS)

    return metadata


def supported_territory_codes():
    """ Return a set of recognized territory codes.

    Are supported:
        * ISO 3166-1 alpha-2 country codes
        * ISO 3166-2 subdivision codes

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'supported_territory_codes has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import supported_territory_codes
    return supported_territory_codes()


def normalize_territory_code(territory_code, resolve_aliases=True):
    """ Normalize any string into a territory code.

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'normalize_territory_code has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import normalize_territory_code
    return normalize_territory_code(
        territory_code, resolve_aliases=resolve_aliases)


def normalize_country_code(subdivision_code):
    """ Return the normalized country code of a subdivisions.

    For subdivisions having their own ISO 3166-1 alpha-2 country code, returns
    the later instead of the parent ISO 3166-2 top entry.

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'normalize_country_code has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import normalize_country_code
    return normalize_country_code(subdivision_code)


def default_subdivision_code(country_code):
    """ Return the default subdivision code of a country.

    The result can be guessed only if there is a 1:1 mapping between a country
    code and a subdivision code.

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'default_subdivision_code has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import default_subdivision_code
    return default_subdivision_code(country_code)


def territory_tree(territory_code, include_country=True):
    """ Return the whole hierarchy of territories, up to the country.

    Values returned by the generator are either subdivisions or country
    objects, starting from the provided subdivision and up its way to
    the top administrative territory (i.e. country).

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'territory_tree has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import territory_tree
    return territory_tree(
        territory_code, include_country=include_country)


def territory_parents(territory_code, include_country=True):
    """ Return the whole hierarchy of territories, up to the country.

    Values returned by the generator are either subdivisions or country
    objects, starting from the provided territory and up its way to the top
    administrative territory (i.e. country).

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'territory_parents has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import territory_parents
    return territory_parents(
        territory_code, include_country=include_country)


def territory_parents_codes(territory_code, include_country=True):
    """ Like territory_parents but return normalized codes instead of objects.

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'territory_parents_codes has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import territory_parents_codes
    return territory_parents_codes(
        territory_code, include_country=include_country)


def country_aliases(territory_code):
    """ List valid country code aliases of a territory.

    Mainly used to check if a non-normalized country code can safely be
    replaced by its normalized form.

    .. deprecated:: 0.3.0

       Import from ``postal_address.territory`` instead of
       ``postal_address.address``.
    """
    warnings.warn(
        'country_aliases has been moved from postal_address.address '
        'to postal_address.territory.', DeprecationWarning)
    from .territory import country_aliases
    return country_aliases(territory_code)
