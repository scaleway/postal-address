# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause


__version__ = '1.1.2'

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

from .address import Address
