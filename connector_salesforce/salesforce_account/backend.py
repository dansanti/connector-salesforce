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
class SalesforceAccountBackend(orm.model):

    _inherit = 'connector.salesforce.backend'

    _columns = {
        'last_sf_account_import_sync_date': fields.datetime(
            'Last Account Import Date'
        ),

        'last_sf_account_Delete_sync_date': fields.datetime(
            'Last Account Delete Date'
        ),

    }

    def import_sf_account(self, cr, uid, ids, context=None):
        backend_id = self._manage_ids(ids)
        current = self.browse(cr, uid, backend_id, context=context)
        current._import(
            self._name,
            'direct',
            'last_sf_account_import_sync_date',
        )