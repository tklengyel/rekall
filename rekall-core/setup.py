#!/usr/bin/env python

# Rekall
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Authors:
# Michael Cohen <scudette@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
"""Installation and deployment script."""
__author__ = "Michael Cohen <scudette@gmail.com>"
import platform
import os
import subprocess
import versioneer

try:
    from setuptools import find_packages, setup, Command
except ImportError:
    from distutils.core import find_packages, setup

rekall_description = "Rekall Memory Forensic Framework"

current_directory = os.path.dirname(__file__)


def find_data_files_directory(source):
    result = []
    for directory, _, files in os.walk(source):
        files = [os.path.join(directory, x) for x in files]
        result.append((directory, files))

    return result

# These versions are fixed to the exact tested configuration. Prior to release,
# please use "setup.py pip_upgrade" to test with the latest version. This
# approach ensures that any Rekall version will always work as tested - even
# when external packages are upgraded in an incompatible way.
install_requires = [
    "PyAFF4 >= 0.20",
    "PyYAML >= 3.11",
    "acora >= 1.9",
    "argparse >= 1.3.0",
    "arrow >= 0.7.0",
    "distorm3 == 3.3.0",
    "efilter == 1450268920",
    "intervaltree >= 2.1.0",
    "pycrypto >= 2.6.1",
    "pyelftools >= 0.23",
    "pytz >= 2015.7",
    "sortedcontainers >= 1.4.2",
]

if platform.system() == "Windows":
    install_requires.append("pypiwin32 == 219")


class PIPUpgrade(Command):
    description = "Upgrade all the dependencies in the current virtualenv."
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        required = [x.split()[0] for x in install_requires]
        output = subprocess.check_output(
            ["pip", "install", "--upgrade"] + required)

        # Print the current versions.
        output = subprocess.check_output(
            ["pip", "freeze"])

        result = []
        for package in required:
            result.append(
                [x for x in output.splitlines()
                 if package in x][0])

        print "\n".join(sorted(result))


class CleanCommand(Command):
    description = ("custom clean command that forcefully removes "
                   "dist/build directories")
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        if os.getcwd() != self.cwd:
            raise RuntimeError('Must be in package root: %s' % self.cwd)

        os.system('rm -rf ./build ./dist')

commands = versioneer.get_cmdclass()
commands["pip_upgrade"] = PIPUpgrade
commands["clean"] = CleanCommand

setup(
    name="rekall-core",
    version=versioneer.get_version(),
    cmdclass=commands,
    description=rekall_description,
    long_description=open(os.path.join(current_directory, "README.rst")).read(),
    license="GPL",
    url="https://www.rekall-forensic.com/",
    author="The Rekall team",
    author_email="rekall-discuss@googlegroups.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    scripts=["rekall/rekal.py"],
    package_dir={'rekall': 'rekall'},
    packages=find_packages('.'),
    include_package_data=True,
    data_files=(
        find_data_files_directory('resources')
    ),
    entry_points="""
    [rekall.plugins]
    plugins=rekall.plugins

    [console_scripts]
    rekal = rekall.rekal:main
    rekall = rekall.rekal:main
    """,
    install_requires=install_requires,
)
