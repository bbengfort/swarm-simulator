# tests.params_tests
# Testing the parameters module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Nov 20 15:15:30 2013 -0500
#
# Copyright (C) 2013 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: params_tests.py [] benjamin@bengfort.com $

"""
Taken from the testing module for the configuration of another project.
"""

##########################################################################
## Imports
##########################################################################

import os
import yaml
import unittest
import tempfile

from copy import copy
from swarm.params import *

##########################################################################
## Configuration Unit Tests
##########################################################################

class ConfigurationTests(unittest.TestCase):

    FIXTURE = {
        "myprop": "Allen",
        "mysetting": False,
        "items": ["apples", "bananas", "oranges"],
        "nested": {"level": "floor", "empty": ["full",]}
    }

    def setUp(self):
        self.original_conf_paths = copy(Configuration.CONF_PATHS)
        Configuration.CONF_PATHS = []

        self.config_file = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False).name
        with open(self.config_file, "w") as conf:
            yaml.dump(self.FIXTURE, conf, default_flow_style=False)

    def tearDown(self):
        Configuration.CONF_PATHS = self.original_conf_paths
        os.remove(self.config_file)

    def test_search_path(self):
        """
        Assert there are directories to search for a configuration
        """
        self.assertGreater(len(self.original_conf_paths), 0)

    def test_empty_conf_path(self):
        """
        Test that an empty conf path raises no exceptions
        """
        config = TestConfiguration.load()
        self.assertEquals(len(Configuration.CONF_PATHS), 0)
        self.assertTrue(config['mysetting'])
        self.assertIsNone(config.get('myprop'))

    def test_load_config(self):
        """
        Assert config can load from YAML
        """
        Configuration.CONF_PATHS.append(self.config_file)

        config = TestConfiguration.load()
        self.assertIsNotNone(config.get('myprop'))
        self.assertEqual(config.get('myprop'), "Allen")
        self.assertTrue(isinstance(config.get('nested'), NestedConfiguration))
        self.assertEqual(config.get("nested").get("level"), "floor")

    def test_load_override(self):
        """
        Assert that loading config overrides default
        """
        Configuration.CONF_PATHS.append(self.config_file)

        config = TestConfiguration.load()
        self.assertFalse(config["mysetting"])

    def test_configure_by_dict(self):
        """
        Check configuration by dictionary
        """
        config = TestConfiguration.load()
        config.configure({"anoption":45, "foo":"bar"})
        self.assertEqual(config["anoption"], 45)
        self.assertEqual(config["foo"], "bar")

    def test_configure_by_conf(self):
        """
        Check configuration by other configuration
        """
        configa = TestConfiguration.load()
        configb = TestConfiguration.load()

        self.assertEqual(configa["anoption"], configb["anoption"])

        configa.anoption = 80
        self.assertNotEqual(configa["anoption"], configb["anoption"])

        configb.configure(configa)
        self.assertEqual(configa["anoption"], configb["anoption"])

    def test_configure_with_none(self):
        """
        Ensure None passed to configure doesn't break
        """
        config = TestConfiguration.load()
        try:
            config.configure(None)
        except Exception:
            self.fail("None passed to configure raised an error!")

    def test_nested_configure(self):
        """
        Ensure nested configurations work
        """
        config = TestConfiguration.load()
        data   = {"nested": {"nested": {"level":"basement"}, "level": "lobby"}}
        config.configure(data)
        self.assertEqual(type(config.get('nested')), NestedConfiguration)
        self.assertEqual(type(config.get('nested').get('nested')), SubNestedConfiguration)
        self.assertEqual(config.get('nested').get('level'), 'lobby')
        self.assertEqual(config.get('nested').get('nested').get('level'), 'basement')

    def test_options(self):
        """
        Test the options method
        """
        config = TestConfiguration.load()
        options = dict(config.options())

        self.assertIn("mysetting", options)
        self.assertIn("anoption", options)
        self.assertIn("paththere", options)

        self.assertNotIn("_notanopt", options)
        self.assertNotIn("amethod", options)
        self.assertNotIn("NOTANOPT", options)

    def test_get(self):
        """
        Assert that get returns default or key
        """
        config = TestConfiguration.load()
        self.assertTrue(config.get("mysetting"))
        self.assertNotIn("notanopt", dict(config.options()))
        self.assertEqual(config.get("notanopt", 1), 1)

    def test__get__(self):
        """
        Check the getkey method
        """
        config = TestConfiguration.load()
        self.assertTrue(config["mysetting"])

    def test_case_insensitivity(self):
        """
        Assert case insensitivity in getitem
        """
        config = TestConfiguration.load()
        self.assertTrue(config["MYSETTING"])

    def test_key_error(self):
        """
        Assert not found key raises an exception
        """
        with self.assertRaises(KeyError):
            config = TestConfiguration.load()
            self.assertTrue(config["notanopt"])

    @unittest.skip
    def test_configure_back_to_empty(self):
        """
        Can override an empty list or dictionary from configuration
        """
        # Setup normal configuration
        Configuration.CONF_PATHS.append(self.config_file)
        config = TestConfiguration.load()
        self.assertGreater(len(config.nested.empty), 0, "Configuration not loaded")

        # Now reoverride with orignal settings - like the TestingConfig
        config.configure(NestedConfiguration())
        self.assertEqual(config.nested.level, 1)
        self.assertEqual(len(config.nested.empty), 0)

class SubNestedConfiguration(Configuration):

    level = 2

class NestedConfiguration(Configuration):

    level  = 1
    empty  = []
    nested = SubNestedConfiguration()

class TestConfiguration(Configuration):
    """
    A subclass of the Configuration class for testing purposes.
    """

    _notanopt = "joe"
    NOTANOPT  = "bob"
    mysetting = True
    anoption  = 42
    paththere = "/var/log/there.pth"
    nested    = NestedConfiguration()

    def amethod(self):
        return True
