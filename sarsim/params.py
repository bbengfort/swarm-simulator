# sarsim.params
# Loads the parameter configuration from a YAML file
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Tue Apr 08 10:56:37 2014 -0400
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: params.py [] bengfort@cs.umd.edu $

"""
Loads the parameter configuration from a YAML file.
Note that I'm using a Configuration methodology I've used in the past, so
I'm conflating "settings" with parameters. For the most part, they'll be
used similarly (and multiple configuration files can be loaded), but we
can generate this file with the parameters as our genotype, and then the
phenotype will be the execution of the simulation with those parameters.

Configuration class for specifying specific paramaterization via a
YAML configuration file format. The main configuration class provides
utilities for loading the configuration from disk and iterating across all
the settings. Subclasses of the Configuration specify defaults that can be
updated via the configuration files.

General usage:

    from sarsim.params import parameters
    mysetting = parameters.get('mysetting', default)

You can also get settings via a dictionary like access:

    mysetting = parameters['mysetting']

However, this will raise an exception if the setting is not found.

Note: Keys are CASE insensitive

Note: Parameters can be modified directly by parameters.myparam = newparam
however, this is not recommended, and settings should be fetched via the
dictionary-like access.
"""

##########################################################################
## Imports
##########################################################################

import os
import yaml

from copy import deepcopy

##########################################################################
## Configuration Base Class
##########################################################################

class Configuration(object):
    """
    Base configuration class specifies how configurations should be
    handled and provides helper methods for iterating through options and
    configuring the base class.

    Subclasses should provide defaults for the various configurations as
    directly set class level properties. Note, however, that ANY directive
    set in a configuration file (whether or not it has a default) will be
    added to the configuration.

    Example:

        class MyParams(Configuration):

            mysetting = True
            logpath   = "/var/log/myapp.log"
            appname   = "MyApp"

    The configuration is then loaded via the classmethod `load`:

        parameters = MyParams.load()

    Access to properties is done two ways:

        parameters['mysetting']
        parameters.get('mysetting', True)

    Note: None settings are not allowed!
    """

    CONF_PATHS = [
        '/etc/sarsim/params.yaml',                    # The global configuration
        os.path.expanduser('~/.sarsim/params.yaml'),  # User specific configuration
        os.path.abspath('conf/params.yaml')           # Local directory configuration
    ]

    @classmethod
    def load(klass):
        """
        Insantiates the configuration by attempting to load the
        configuration from YAML files specified by the CONF_PATH module
        variable. This should be the main entry point for configuration.
        """
        config = klass()
        for path in klass.CONF_PATHS:
            if os.path.exists(path):
                with open(path, 'r') as conf:
                    config.configure(yaml.load(conf))
        return config

    def configure(self, conf={}):
        """
        Allows updating of the configuration via a dictionary of
        configuration terms or a configuration object. Generally speaking,
        this method is utilized to configure the object from a JSON or
        YAML parsing.
        """
        if not conf: return
        if isinstance(conf, Configuration):
            conf = dict(conf.options())

        keys = conf.keys()
        for key in keys:
            opt = self.get(key, None)
            if isinstance(opt, Configuration):
                opt.configure(conf.pop(key))
        self.__dict__.update(conf)

    def options(self):
        """
        Returns an iterable of sorted option names in order to loop
        through all the configuration directives specified in the class.
        """
        keys = self.__class__.__dict__.copy()
        keys.update(self.__dict__)
        keys = keys.keys()
        keys.sort()

        for opt in keys:
            val = self.get(opt)
            if val is not None: yield opt, val

    def get(self, key, default=None):
        """
        Fetches a key from the configuration without raising a KeyError
        exception if the key doesn't exist in the config, instead it
        returns the default (None).
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        """
        Main configuration access method. Performs a case insensitive
        lookup of the key on the class, filtering methods and pseudo
        private properties. Raises KeyError if not found. Note, this makes
        all properties that are uppercase invisible to the options.
        """
        key = key.lower()
        if hasattr(self, key):
            attr = getattr(self, key)
            if not callable(attr) and not key.startswith('_'):
                return attr
        raise KeyError("%s has no configuration '%s'" % (self.__class__.__name__, key))

    def __repr__(self):
        return str(self)

    def __str__(self):
        s = ""
        for opt, val in self.options():
            r = repr(val)
            r = " ".join(r.split())
            wlen = 76-max(len(opt),10)
            if len(r) > wlen:
                r = r[:wlen-3]+"..."
            s += "%-10s = %s\n" % (opt, r)
        return s[:-1]

##########################################################################
## Velocity Component Parameter
##########################################################################

class VelocityComponent(Configuration):
    """
    Configuration of Velocity Component Parameters for use with the
    dynamics system. This class will be instantiated multiple times for
    different components and movement behaviors.
    """

    priority = 1            # Integer, ordered priority of component
    weight   = 0.5          # Wight for non-linear combination of vectors
    radius   = 100          # The distance a particle can see neighbors at
    alpha    = 180          # The degrees of the vision of the particle

    def __init__(self, priority=1, weight=0.5, radius=100, alpha=180):
        """
        Allows for quick instantiation of Velocity component parameters.
        This is not a normal use of Configurations but is necessary to
        enable many different Velocity components
        """
        self.priority = priority
        self.weight   = weight
        self.radius   = radius
        self.alpha    = alpha

##########################################################################
## Movement Behavior Parameter
##########################################################################

class MovementBehavior(Configuration):
    """
    Configuration of a Movement Behavior is essentially a dict of Velocity
    Components along with their priorities and configurations.
    """

    components = {}         # A dictionary of velocity components.

    def __init__(self, components=None):
        """
        Allows for quick instantiation of MovementBehavior parameters.
        This is not a normal use of Configurations but is necessary to
        enable many different Movement Behaviors.
        """
        self.components = components if components else {}

    def configure(self, conf={}):
        """
        Special behavior to configure VelocityComponents
        """
        if 'components' in conf:
            components = conf.pop('components')
            for name, kwargs in components.items():
                self.components[name] = VelocityComponent(**kwargs)
        return super(MovementBehavior, self).configure(conf)

##########################################################################
## Simulation Paramter Defaults
##########################################################################

class SimulationParameters(Configuration):
    """
    This object contains the default parameters for the simulation.
    """

    debug            = True
    maximum_velocity = 100

    # Spreading Movement Behavior
    spreading        = MovementBehavior({
        'avoidance':   VelocityComponent(1, 0.66, 100, 180),
        'separation':  VelocityComponent(2, 0.83, 150, 180),
        'clearance':   VelocityComponent(3, 0.83, 150, 115),
        'alignment':   VelocityComponent(4, 0.83, 250, 115),
        'cohesion':    VelocityComponent(5, 0.83, 300, 360),
    })

    # Seeking Movement Behavior
    seeking          = MovementBehavior({
        'avoidance':   VelocityComponent(1, 0.83, 100, 180),
        'seek':        VelocityComponent(2, 0.66, 250, 360),
        'separation':  VelocityComponent(3, 0.25, 50, 90),
    })

    # Caravan Movement Behavior
    caravan          = MovementBehavior({
        'avoidance':   VelocityComponent(1, 0.83, 100, 180),
        'homing':      VelocityComponent(2, 0.83, None, None),
        'separation':  VelocityComponent(3, 0.83, 100, 180),
        'clearance':   VelocityComponent(4, 0.83, 150, 60),
    })

    # Guarding Movement Behavior
    guarding         = MovementBehavior({
        'avoidance':   VelocityComponent(1, 1.0, 100, 180),
        'separation':  VelocityComponent(2, 0.62, 50, 180),
        'mineral_cohesion': VelocityComponent(3, 0.62, 150, 360),
    })



##########################################################################
## Import this loaded Configuration
##########################################################################

parameters = SimulationParameters.load()

if __name__ == '__main__':
    print parameters
