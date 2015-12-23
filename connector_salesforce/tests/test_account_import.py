# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2015 Camptocamp SA
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
from mock import MagicMock
from .common import CommonTest, mock_simple_salesforce
from . import fixture


class AccountImportTest(CommonTest):

    def setUp(self):
        super(AccountImportTest, self).setUp()
        self.model_name = 'connector.salesforce.account'
        self.imported_model = self.env[self.model_name]
        self.conn_env = self.get_connector_env(self.model_name)

    def test_simple_import(self):
        pl_version = self.get_euro_pricelist_version()
        self.env['connector.salesforce.pricebook.entry.mapping'].create(
            {
                'backend_id': self.backend.id,
                'currency_id': pl_version.pricelist_id.currency_id.id,
                'pricelist_version_id': pl_version.id,
            }
        )
        response = MagicMock(name='simple_account_import')
        response.side_effect = [
            {'records': [{'Id': 'uuid_account_01'}]},
            {'records': [{'dummy': 'dummy'}]},
            fixture.account,
        ]
        with mock_simple_salesforce(response):
            self.backend.import_sf_account()

        imported = self.imported_model.search(
            [('salesforce_id', '=', 'uuid_account_01'),
             ('backend_id', '=', self.backend.id)]
        )
        self.assertTrue(imported)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported.name, 'Main name')
        self.assertEqual(imported.street, 'Main street')
        self.assertEqual(imported.city, 'Main city')
        self.assertEqual(imported.fax, '+41 21 619 10 10')
        self.assertEqual(imported.phone, '+41 21 619 10 12')
        self.assertEqual(imported.vat, 'Main vat')
        self.assertEqual(imported.zip, 'Main zip')
        self.assertEqual(imported.state_id.name, 'Main state')
        self.assertEqual(imported.country_id.code, 'CH')
        self.assertEqual(imported.property_product_pricelist.currency_id.name,
                         'EUR')
        self.assertTrue(imported.is_company)
        shipping_partner = imported.sf_shipping_partner_id
        self.assertTrue(shipping_partner)
        self.assertFalse(shipping_partner.is_company)
        self.assertEqual(shipping_partner.name, 'Main name')
        self.assertEqual(shipping_partner.parent_id, imported.openerp_id)
        self.assertEqual(shipping_partner.street, 'Shipping street')
        self.assertEqual(shipping_partner.zip, 'Shipping zip')
        self.assertEqual(shipping_partner.state_id.name, 'Shipping state')
        self.assertEqual(shipping_partner.country_id.code, 'CH')