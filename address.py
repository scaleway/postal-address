# -*- coding: utf-8 -*-
""" Utilities for address parsing and rendering. """

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)

from itertools import chain, imap
from operator import attrgetter

from pycountry import countries, subdivisions


class Address(object):

    """ Define an address.

    Only provides address validation for the moment, but may be used in the
    future for l10n-aware normalization and rendering.

    ``country_code`` is an ISO 3166-1 alpha-2 code.
    ``subdivision_code`` is an ISO 3166-2 code.
    """

    # List IDs ofaddress' base-components.
    _components = [
        'line1', 'line2', 'zip_code', 'state', 'city',
        'country_code', 'subdivision_code']

    # Fields tested on validate()
    REQUIRED_FIELDS = ['line1', 'zip_code', 'city', 'country_code']

    def __init__(self, **kwargs):
        """ Set address' individual components and normalize them. """
        # Filters out unknown address components.
        unknown_components = set(kwargs.keys()).difference(self._components)
        if unknown_components:
            raise KeyError(
                "Unsupported {!r} address components.".format(
                    unknown_components))
        # Register writable instance attributes.
        self.__dict__.update(dict.fromkeys(self._components))
        # Load provided components.
        for component_id in self._components:
            setattr(self, component_id, kwargs.get(component_id, None))
        self.normalize()

    def __repr__(self):
        """ Print all components of the address. """
        return '{}(line1={}, line2={}, zip_code={}, state={}, city={}, ' \
            'country_code={}, subdivision_code={})'.format(
                self.__class__.__name__, self.line1, self.line2, self.zip_code,
                self.state, self.city, self.country_code,
                self.subdivision_code)

    def __str__(self):
        """ Return a simple string representation of the address block. """
        return self.render()

    def render(self, separator='\n'):
        """ Render a human-friendly address block.

        ``line1`` & ``line2`` are rendered as-is.
        A third line is composed of ``zip_code``, ``city`` and ``state``.
        The last line feature country's common name.
        """
        lines = []
        if self.line1:
            lines.append(self.line1)
        if self.line2:
            lines.append(self.line2)
        # Build the third line.
        line3_elements = []
        if self.city:
            line3_elements.append(self.city)
        if self.state:
            line3_elements.append(self.state)
        # Separate city and state by a comma.
        line3_elements = [', '.join(line3_elements)]
        if self.zip_code:
            line3_elements.insert(0, self.zip_code)
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
        """ Normalize address fields. """
        if self.country_code:
            self.country_code = self.country_code.strip().upper()
        if self.subdivision_code:
            self.subdivision_code = self.subdivision_code.strip().upper()
        # Normalize empty/blank strings to None.
        for component_id in self._components:
            if not getattr(self, component_id):
                setattr(self, component_id, None)

    def validate(self):
        """ Check required fields and their values. """
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field):
                raise ValueError("Address requires {}.".format(field))

        # Check the country code exists.
        try:
            countries.get(alpha2=self.country_code)
        except KeyError:
            raise ValueError(
                "Invalid {!r} country code.".format(self.country_code))

        if self.subdivision_code:
            # Check the subdivision code exists.
            try:
                subdiv = subdivisions.get(code=self.subdivision_code)
            except KeyError:
                raise ValueError(
                    "Invalid {!r} subdivision code.".format(
                        self.subdivision_code))
            # Check country is a parent of subdivision.
            if subdiv.country_code != self.country_code:
                raise ValueError(
                    "{!r} country is not a parent {!r} subdivision.".format(
                        self.country_code, self.subdivision_code))

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
        if (self.line1 or self.line2 or self.zip_code or self.state or
                self.city or self.country_code):
            return False
        return True

    @property
    def country_name(self):
        """ Return country's name. """
        if self.country_code:
            return countries.get(alpha2=self.country_code).name
        return None

    @property
    def subdivision_name(self):
        """ Return subdivision's name. """
        if self.subdivision_code:
            return subdivisions.get(code=self.subdivision_code).name
        return None

    @property
    def subdivision_type(self):
        """ Return subdivision's type. """
        if self.subdivision_code:
            return subdivisions.get(code=self.subdivision_code).type
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
