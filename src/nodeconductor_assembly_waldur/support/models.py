from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from nodeconductor.core import models as core_models
from nodeconductor.structure import models as structure_models

from . import backend


@python_2_unicode_compatible
class Issue(core_models.UuidMixin, structure_models.StructureLoggableMixin, TimeStampedModel):
    class Meta:
        ordering = ['-modified']

    class Permissions(object):
        customer_path = 'customer'
        project_path = 'project'

    class Type(object):
        INFORMATIONAL = 'informational'
        SERVICE_REQUEST = 'service_request'
        CHANGE_REQUEST = 'change_request'
        INCIDENT = 'incident'

        CHOICES = (
            (INFORMATIONAL, _('Informational')),
            (SERVICE_REQUEST, _('Service request')),
            (CHANGE_REQUEST, _('Change request')),
            (INCIDENT, _('Incident')),
        )

    backend_id = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=30, choices=Type.CHOICES, default=Type.INFORMATIONAL)

    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=255)
    resolution = models.CharField(blank=True, max_length=255)

    reporter = models.ForeignKey('SupportUser', related_name='reported_issues')
    caller = models.ForeignKey('SupportUser', related_name='created_issues')
    assignee = models.ForeignKey('SupportUser', related_name='issues', blank=True, null=True)

    customer = models.ForeignKey(structure_models.Customer, related_name='issues', blank=True, null=True)
    project = models.ForeignKey(structure_models.Project, related_name='issues', blank=True, null=True)

    resource_content_type = models.ForeignKey(ContentType, null=True)
    resource_object_id = models.PositiveIntegerField(null=True)
    resource = GenericForeignKey('resource_content_type', 'resource_object_id')

    def get_backend(self):
        return backend.IssueBackend()

    def get_log_fields(self):
        return ('uuid', 'type', 'status', 'summary', 'reporter', 'creator', 'customer', 'project', 'resource')

    def __str__(self):
        return '{}: {}'.format(self.key or '???', self.summary)


@python_2_unicode_compatible
class SupportUser(core_models.UuidMixin, core_models.NameMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', blank=True, null=True)
    backend_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Comment(core_models.UuidMixin, models.Model):
    issue = models.ForeignKey(Issue, related_name='comments')
    author = models.ForeignKey(SupportUser, related_name='comments')
    description = models.TextField()
    is_public = models.BooleanField(default=True)
    backend_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description[:50]
