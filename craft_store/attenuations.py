# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Attenuations for Snap Store and Charmhub discharged Macaroons.

=======================
Read write attenuations
=======================

.. data:: ACCOUNT_REGISTER_PACKAGE

    Register or request a new package name under a given account.

.. data:: PACKAGE_MANAGE

    Meta permission for easing creation of a complete RW token,
    it grants all the package-manage-* permissions.

.. data:: PACKAGE_MANAGE_ACL

    Add, invite or remove collaborators.

.. data:: PACKAGE_MANAGE_LIBRARY

    Register or request a new library name under a given package.

.. data:: PACKAGE_MANAGE_METADATA

    Edit metadata, add or remove media, etc.

.. data:: PACKAGE_MANAGE_RELEASES

    Release revisions, close channels and update version pattern for a track.

.. data:: PACKAGE_MANAGE_REVISIONS

    Upload new blobs, check for upload status, reject a revision blocked on
    manual review or request manual review.

======================
Read only attenuations
======================

.. data:: ACCOUNT_VIEW_PACKAGES

    List packages owned by the account and packages for which this account
    has collaborator rights.

.. data:: PACKAGE_VIEW

    Meta permission for easing creation of a complete RO token grants all the
    package-view-* perms

.. data:: PACKAGE_VIEW_ACL

    list the collaborators for a package and privacy settings.

.. data:: PACKAGE_VIEW_METADATA

    View the metadata for a package, including media.

.. data:: PACKAGE_VIEW_METRICS

    View the metrics of a package.

.. data:: PACKAGE_VIEW_RELEASES

    List the current releases (channel map) for a package and the release
    history of a package.

.. data:: PACKAGE_VIEW_REVISIONS
    list the existing revisions for a package, along with status information
"""

# read/write access.
ACCOUNT_REGISTER_PACKAGE = "account-register-package"
PACKAGE_MANAGE = "package-manage"
PACKAGE_MANAGE_ACL = "package-manage-acl"
PACKAGE_MANAGE_LIBRARY = "package-manage-library"
PACKAGE_MANAGE_METADATA = "package-manage-metadata"
PACKAGE_MANAGE_RELEASES = "package-manage-releases"
PACKAGE_MANAGE_REVISIONS = "package-manage-revisions"

# read only access.
ACCOUNT_VIEW_PACKAGES = "account-view-packages"
PACKAGE_VIEW = "package-view"
PACKAGE_VIEW_ACL = "package-view-acl"
PACKAGE_VIEW_METADATA = "package-view-metadata"
PACKAGE_VIEW_METRICS = "package-view-metrics"
PACKAGE_VIEW_RELEASES = "package-view-releases"
PACKAGE_VIEW_REVISIONS = "package-view-revisions"
