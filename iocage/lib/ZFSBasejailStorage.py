# Copyright (c) 2014-2017, iocage
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""iocage ZFS basejail storage backend."""
import iocage.lib.helpers


class ZFSBasejailStorage:
    """iocage ZFS basejail storage backend."""

    def apply(self, release=None):
        """Attach the jail storage."""
        if release is None:
            release = self.jail.cloned_release

        return ZFSBasejailStorage.clone(self, release)

    def setup(self, release):
        """Configure the jail storage."""
        iocage.lib.StandaloneJailStorage.StandaloneJailStorage.setup(
            self, release)

    def clone(self, release):
        """Clone ZFS basejail datasets from a release."""
        current_basejail_type = self.jail.config["basejail_type"]
        if not current_basejail_type == "zfs":
            raise iocage.lib.errors.InvalidJailConfigValue(
                property_name="basejail_type",
                reason="Expected ZFS, but saw {current_basejail_type}",
                logger=self.logger
            )

        ZFSBasejailStorage._create_mountpoints(self)

        basedirs = iocage.lib.helpers.get_basedir_list(
            distribution_name=self.jail.host.distribution.name
        )

        for basedir in basedirs:
            source_dataset_name = f"{release.base_dataset.name}/{basedir}"
            target_dataset_name = f"{self.jail.root_dataset_name}/{basedir}"
            self.clone_zfs_dataset(source_dataset_name, target_dataset_name)

    def _create_mountpoints(self):
        for basedir in ["dev", "etc"]:
            self.create_jail_mountpoint(basedir)
