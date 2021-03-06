from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.faqs import FaqSchema
from app.models import db
from app.models.faq import Faq
from app.models.event import Event


class FaqListPost(ResourceList):
    """
    Create and List FAQs
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for required relationship with event
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound({'parameter': 'event_id'},
                                 "Event: {} not found".format(data['event_id']))

    schema = FaqSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Faq
                  }


class FaqList(ResourceList):
    """
    Show List of FAQs
    """
    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Faq)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    decorators = (jwt_required, )
    methods = ['GET', ]
    schema = FaqSchema
    data_layer = {'session': db.session,
                  'model': Faq,
                  'methods': {
                      'query': query
                  }}


class FaqDetail(ResourceDetail):
    """
    FAQ Resource
    """

    def before_get_object(self, view_kwargs):
        """
        before get method
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')

        if event:
            faq = safe_query(self, Faq, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = faq.id

    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=Faq, methods="PATCH,DELETE"), )
    schema = FaqSchema
    data_layer = {'session': db.session,
                  'model': Faq}


class FaqRelationshipRequired(ResourceRelationship):
    """
    FAQ Relationship (Required)
    """
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                                     fetch_as="event_id", model=Faq, methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = FaqSchema
    data_layer = {'session': db.session,
                  'model': Faq}
