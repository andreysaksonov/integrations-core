# (C) Datadog, Inc. 2010-2018
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

from datadog_checks.checks import AgentCheck
from . import mesh, mixer
from datadog_checks.check.prometheus.base_check import Scraper


class Istio(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):
        super(Istio, self).__init__(name, init_config, agentConfig, instances)

        self.scrapers = {}

        # Instead of one check, use three
        self.mesh_check = mesh.IstioMeshCheck(name, init_config, agentConfig, instances)
        self.mixer_check = mixer.MixerCheck(name, init_config, agentConfig, instances)

        # Put them in an array, so that duplicate actions are easier
        self.checks = [self.mesh_check, self.mixer_check]

        # Agent 6 has no aggregator attached to the check
        try:
            # Make sure they all have the same aggregator so that the status page works
            for check in self.checks:
                check.aggregator = self.aggregator
        except AttributeError:
            # This means this is either run in Agent 6 or in the tests
            pass



    def check(self, instance):
        self.log.debug('running all istio checks')

        istio_mesh_endpoint = instance.get('istio_mesh_endpoint')
        mixer_endpoint = instance.get('mixer_endpoint')

        if not self.scrapers.get(istio_mesh_endpoint, None):
            istio_mesh_scraper = Scraper(self)
            self.scrapers[istio_mesh_endpoint] = istio_mesh_scraper
        else:
            istio_mesh_scraper = self.scrapers.get(istio_mesh_endpoint)

        if not self.scrapers.get(mixer_endpoint, None):
            mixer_scraper = Scraper(self)
            self.scrapers[mixer_endpoint] = mixer_scraper
        else:
            mixer_scraper = self.scrapers.get(mixer_endpoint)

        # # run the checks
        # for check in self.checks:
        #     check.check(instance)
