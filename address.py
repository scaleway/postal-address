# -*- coding: utf-8 -*-
u""" Utilities for address parsing and rendering.

    « What ties us to territory is tax. »
    -- Kevin Deldycke, 2014-11-07

The reason above is why we need fine-grained and meticulous territory
management and normalization.

Postal address parsing and rendering is hard. Much hard than you expect.
Please read:
http://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/
"""

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

from itertools import chain, imap
from operator import attrgetter

from pycountry import countries, subdivisions

from slugify import slugify


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
    _base_component_ids = [
        'line1', 'line2', 'postal_code', 'city_name', 'country_code',
        'subdivision_code']

    # Still, some of the free-form fields above might be overriden by special
    # cases of ISO 3166-2 subdivision codes.
    SUBDIVISION_OVERRIDABLE_FIELDS = ['city_name']

    # Fields tested on validate().
    REQUIRED_FIELDS = ['line1', 'postal_code', 'city_name', 'country_code']

    def __init__(self, **kwargs):
        """ Set address' individual components and normalize them. """
        # Only base components are allowed to be set directly.
        unknown_components = set(kwargs).difference(self._base_component_ids)
        if unknown_components:
            raise KeyError(
                "{!r} components are not allowed to be set freely.".format(
                    unknown_components))
        # Initialize base components values.
        self._components = dict.fromkeys(self._base_component_ids)
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
        if name in self._components or name in self._base_component_ids:
            return self._components.get(name, None)
        raise AttributeError

    def __setattr__(self, name, value):
        """ Allow update of address components as an attribute. """
        if name in self._base_component_ids:
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
        if key in self._base_component_ids:
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
        if hasattr(self, 'state'):
            line3_elements.append(self.state)
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
        """ Normalize address fields between themselves.
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

        # Normalize ISO codes.
        if self.country_code:
            self.country_code = self.country_code.upper()
        if self.subdivision_code:
            self.subdivision_code = self.subdivision_code.upper()

        # Swap lines if the first is empty.
        if self.line2 and not self.line1:
            self.line1, self.line2 = self.line2, self.line1

        # Populate address components with the code and name of all
        # subdivision's parents. This part has the authority to overrides
        # city_name and and country_code fields.
        if self.subdivision_code:
            parent_data = {}
            for parent in territory_tree(self.subdivision_code):
                if parent.__class__.__name__ == 'Country':
                    parent_data['country_code'] = parent.alpha2
                else:
                    parent_type_id = subdivision_type_id(parent.type)
                    parent_data.update({
                        '{}'.format(
                            parent_type_id): parent,
                        '{}_code'.format(
                            parent_type_id): parent.code,
                        '{}_name'.format(
                            parent_type_id): parent.name,
                        '{}_type_name'.format(
                            parent_type_id): parent.type})
            for component_id, component_value in parent_data.items():
                if self._components.get(
                        component_id, None) is not None and self._components[
                            component_id] != component_value:
                    raise ValueError(
                        "{} subdivision conflicts with {}='{}' field.".format(
                            self.subdivision_code, component_id,
                            self._components[component_id]))
                self._components[component_id] = component_value

    def validate(self):
        """ Check fields consistency and requirements.
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
        if self.country_code and self.subdivision_code and subdivisions.get(
                code=self.subdivision_code).country_code != self.country_code:
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
        if self.subdivision_type_name:
            return subdivision_type_id(self.subdivision_type_name)
        return None


def territory_codes():
    """ Return the list of recognized territory codes.

    Are supported:
        * ISO 3166-1 alpha-2 country codes
        * ISO 3166-2 subdivision codes
    """
    return chain(
        imap(attrgetter('alpha2'), countries),
        imap(attrgetter('code'), subdivisions))


def territory_tree(subdivision_code, include_country=True):
    """ Return the whole hierarchy of territories, up to the country.

    Values returned by the generator are either subdivisions or country
    objects, starting from the provided subdivision and up its way to
    the top administrative territory (i.e. country).
    """
    while subdivision_code:
        subdiv = subdivisions.get(code=subdivision_code)
        yield subdiv
        if not subdiv.parent_code:
            break
        subdivision_code = subdiv.parent_code

    # Return country
    if include_country:
        yield subdivisions.get(code=subdivision_code).country


def territory_parents(subdivision_code, include_country=True):
    """ Return hierarchy of territories, but the provided subdivision. """
    for index, subdivision in enumerate(territory_tree(
            subdivision_code, include_country=include_country)):
        if index > 0:
            yield subdivision


def subdivision_type_id(subdivision_type_name):
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
    type_id = slugify(subdivision_type_name).replace('-', '_')

    # Any occurence of the 'city' or 'municipality' string in the type
    # overrides its classification as a city.
    if set(['city', 'municipality']).intersection(type_id.split('_')):
        type_id = 'city'

    return type_id
