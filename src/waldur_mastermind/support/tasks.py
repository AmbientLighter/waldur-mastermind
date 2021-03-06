from __future__ import unicode_literals

import logging
from smtplib import SMTPException

from celery import shared_task
from celery.task import Task as CeleryTask
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from waldur_core.core import utils as core_utils

from . import backend, models

logger = logging.getLogger(__name__)


class SupportUserPullTask(CeleryTask):
    """ Pull support users from backend """
    name = 'support.SupportUserPullTask'

    def run(self):
        if not settings.WALDUR_SUPPORT['ENABLED']:
            return

        backend_users = backend.get_active_backend().get_users()
        for backend_user in backend_users:
            user, created = models.SupportUser.objects.get_or_create(
                backend_id=backend_user.backend_id, defaults={'name': backend_user.name})
            if not created and user.name != backend_user.name:
                user.name = backend_user.name
                user.save()
        models.SupportUser.objects.exclude(backend_id__in=[u.backend_id for u in backend_users]).delete()


@shared_task(name='waldur_mastermind.support.send_issue_updated_notification')
def send_issue_updated_notification(serialized_issue):
    issue = core_utils.deserialize_instance(serialized_issue)
    _send_issue_notification(issue, 'issue_updated')


@shared_task(name='waldur_mastermind.support.send_comment_added_notification')
def send_comment_added_notification(serialized_comment):
    comment = core_utils.deserialize_instance(serialized_comment)

    # Skip notifications about comments added to an issue by caller himself
    if comment.author.user != comment.issue.caller:
        _send_issue_notification(comment.issue, 'comment_added')


def _send_issue_notification(issue, template, receiver=None):
    if not settings.WALDUR_SUPPORT['ENABLED']:
        return

    if settings.SUPPRESS_NOTIFICATION_EMAILS:
        message = ('Issue notifications are suppressed. '
                   'Please set SUPPRESS_NOTIFICATION_EMAILS to False to send notifications.')
        logger.info(message)
        return

    if not receiver:
        receiver = issue.caller

    context = {
        'issue_url': settings.ISSUE_LINK_TEMPLATE.format(uuid=issue.uuid),
        'site_name': settings.WALDUR_CORE['SITE_NAME'],
    }

    subject = render_to_string('support/notification_%s_subject.txt' % template).strip()
    text_message = render_to_string('support/notification_%s.txt' % template, context)
    html_message = render_to_string('support/notification_%s.html' % template, context)

    logger.debug('About to send an issue update notification to %s' % receiver.email)

    try:
        send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, [receiver.email], html_message=html_message)
    except SMTPException as e:
        message = 'Failed to notify a user about an issue update. Issue uuid: %s. Error: %s' % (issue.uuid, e.message)
        logger.warning(message)


@shared_task(name='waldur_mastermind.support.remove_terminated_offerings')
def remove_terminated_offerings():
    """
    Request based offering lifetime must be specified in Waldur support settings with parameter
    "TERMINATED_OFFERING_LIFETIME". If terminated offering lifetime is expired, offering is removed.
    """
    if not settings.WALDUR_SUPPORT['ENABLED']:
        return

    expiration_date = timezone.now() - settings.WALDUR_SUPPORT['TERMINATED_OFFERING_LIFETIME']
    offerings = models.Offering.objects.filter(
        state=models.Offering.States.TERMINATED,
        terminated_at__lte=expiration_date,
    )
    # Bulk delete all expired offerings
    offerings.delete()
