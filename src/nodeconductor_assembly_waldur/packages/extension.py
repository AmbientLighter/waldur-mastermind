from __future__ import unicode_literals

from nodeconductor.core import NodeConductorExtension


class PackagesExtension(NodeConductorExtension):
    class Settings(object):
        WALDUR_PACKAGES = {
            'MANAGER_CAN_CREATE_PACKAGES': False,
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_assembly_waldur.packages'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def is_assembly():
        return True
