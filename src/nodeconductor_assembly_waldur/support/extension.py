from __future__ import unicode_literals

from datetime import timedelta

from nodeconductor.core import NodeConductorExtension


class SupportExtension(NodeConductorExtension):

    class Settings(object):
        WALDUR_SUPPORT = {
            'CREDENTIALS': {
                'server': 'http://example.com/',
                'username': 'USERNAME',
                'password': 'PASSWORD',
                'verify_ssl': False,
            },
            'PROJECT': {
                'key': 'PROJECT',
                'impact_field': 'Impact',
                'reporter_field': 'Original Reporter',
                'caller_field': 'Caller',
            },
            'ISSUE_TYPES': ['Informational', 'Service request', 'Change request', 'Incident'],
            'DEFAULT_ISSUE_TYPE': 'Informational',
            'ACTIVE_BACKEND': 'JiraBackend',
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_assembly_waldur.support'

    @staticmethod
    def django_urls():
        from .urls import urlpatterns
        return urlpatterns

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def is_assembly():
        return True

    @staticmethod
    def celery_tasks():
        return {
            'pull-support-users': {
                'task': 'support.SupportUserPullTask',
                'schedule': timedelta(hours=6),
                'args': (),
            },
        }