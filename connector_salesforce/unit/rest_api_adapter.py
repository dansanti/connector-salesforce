# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from __future__ import unicode_literals
from contextlib import contextmanager
import logging
try:
    from simple_salesforce import Salesforce
    from simple_salesforce.login import SalesforceAuthenticationFailed
except ImportError:
    logger = logging.getLogger('connector_salesforce_rest_adapter_import')
    logger.warning('Library simple_salesforce is not available')

from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from . import exceptions as connector_exception
from ..lib.date_convertion import convert_to_utc_datetime


_logger = logging.getLogger('connector_salesforce_rest_adapter')


@contextmanager
def error_handler():
    try:
        yield
    except SalesforceAuthenticationFailed:
        raise connector_exception.SalesforceSecurityError(
            'An authentication error occur please validate your credentials '
            'in backend'
        )
    except Exception as exc:
        # simple salesforce exception does not devrive form common exception
        if type(exc).__name__.startswith('Salesforce'):
            # TODO get quota excedded error here
            raise connector_exception.SalesforceRESTAPIError(exc)
        else:
            raise


class SalesforceRestAdapter(BackendAdapter):
    """Salesforce adapter for REST API"""
    _sf_type = None

    def __init__(self, connector_environment):
        super(SalesforceRestAdapter, self).__init__(connector_environment)
        self.sf = self.get_sf_connection()
        if not self._sf_type:
            raise ValueError('Salesforce model is not set (_sf_type property)')
        self.sf_type = self.sf.__getattr__(self._sf_type)

    def _sf_from_login_password(self):
        with error_handler():
            sf = Salesforce(
                instance_url=self.backend_record.url,
                username=self.backend_record.username,
                password=self.backend_record.password,
                security_token=self.backend_record.security_token,
            )
        return sf

    def _sf_from_oauth2(self):
        with error_handler():
            sf = Salesforce(
                instance_url=self.backend_record.url,
                session_id=self.backend_record.consumer_token,
                sandbox=self.backend_record.sandbox
            )
        return sf

    def _sf_from_organization_id(self):
        with error_handler():
            sf = Salesforce(
                username=self.backend_record.username,
                password=self.backend_record.password,
                organizationId=self.backend_record.organization_uuid
            )
        return sf

    def get_sf_connection(self):
        assert self.backend_record, 'Backend record not available'
        if self.backend_record.authentication_method == 'oauth2':
            return self._sf_from_oauth2()
        elif self.backen_record.authentication_method == 'pwd_token':
            return self._sf_from_login_password()
        elif self.backend_record.authentication_method == 'ip_filtering':
            return self._sf_from_organization_id()
        else:
            raise NotImplementedError('Authentication method not supported')

    def get_updated(self, start_datetime_str=None, end_datetime_str=None):
        if start_datetime_str:
            if end_datetime_str is None:
                end_datetime_str = '2100-01-01 00:00:00UTC'
            start = convert_to_utc_datetime(start_datetime_str)
            end = convert_to_utc_datetime(end_datetime_str)
            with error_handler():
                return self.sf_type.updated(start, end)['ids']
        else:
            # helper to manage long result does not correspond to SF queryAll
            with error_handler():
                result = self.sf_type.query_all("Select id from %s" % self._sf_type)
            if result['records']:
                return (x['id'] for x in result['records'])
            else:
                return []

    def read(self, sf_id):
        with error_handler():
            return self.sf_type.get(sf_id)