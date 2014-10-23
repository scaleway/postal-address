# -*- coding: utf-8 -*-
""" Utilities for address parsing and rendering. """

from __future__ import (unicode_literals, print_function, absolute_import,
                        division)


class Address(object):
    """ Defines an address.

    Only provides address validation for the moment, but may be used in the
    future for l10n-aware normalization and rendering.

    Addresses are not persisted (yet ?), as we don't allow organizations to
    have more than one active at the same time.

    TODO: add helpers to normalize country and regions around ISO codes ? See:
        https://pypi.python.org/pypi/pycountry
    """
    # Set default values
    line1 = None
    line2 = None
    zip_code = None
    state = None
    city = None
    country = None

    # Fields tested on validate()
    REQUIRED_FIELDS = ['line1', 'zip_code', 'city', 'country']

    def __init__(self, line1=None, line2=None, zip_code=None, state=None,
                 city=None, country=None):
        self.line1 = line1
        self.line2 = line2
        self.zip_code = zip_code
        self.state = state
        self.city = city
        self.country = country

    def __repr__(self):
        """ Print all components of the address. """
        return '{}(line1={}, line2={}, zip_code={}, state={}, city={}, ' \
            'country={})'.format(
                self.__class__.__name__, self.line1, self.line2, self.zip_code,
                self.state, self.city, self.country)

    def __str__(self):
        """ Returns a simple string representation of the address block. """
        return self.render()

    def render(self, separator='\n'):
        """ Render a human-friendly address block.

        ``line1`` & ``line2`` are rendered as-is.
        A third line is composed of ``zip_code``, ``city`` and ``state``.
        The last line feature the ``country``.
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
        if self.country:
            lines.append(self.country)
        # Render the address block.
        return separator.join(lines)

    def validate(self):
        """ Checks required fields are set. """
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field):
                raise ValueError("Address requires {}.".format(field))

    @property
    def valid(self):
        """ Returns a boolean indicating if the address is valid. """
        try:
            self.validate()
        except ValueError:
            return False
        return True

    @property
    def empty(self):
        """ Returns True only if all fields are empty. """
        if (self.line1 or self.line2 or self.zip_code or self.state or
                self.city or self.country):
            return False
        return True
