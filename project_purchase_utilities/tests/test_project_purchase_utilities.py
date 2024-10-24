# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tools.safe_eval import safe_eval
from odoo.tests import common
from odoo.osv import expression


@common.at_install(False)
@common.post_install(True)
class TestProjectPurchaseUtilities(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectPurchaseUtilities, cls).setUpClass()
        cls.project_model = cls.env['project.project']
        cls.project = cls.project_model.create({
            'name': 'Test Project',
        })
        cls.purchase_model = cls.env['purchase.order']
        cls.purchase = cls.purchase_model.search([
            ('state', 'in', ('draft', 'sent')),
        ], limit=1)
        cls.invoice_model = cls.env['account.invoice']

    def test_project_purchase(self):
        self.assertTrue(self.purchase)
        self.purchase.write({
            'invoice_status': 'to invoice',
        })
        self.assertFalse(self.project.purchase_count)
        self.assertFalse(self.project.purchase_line_count)
        self.assertFalse(self.project.in_invoice_count)
        self.assertFalse(self.project.in_invoiced)
        self.purchase.order_line[:1].write({
            'account_analytic_id': self.project.analytic_account_id.id,
        })
        self.project.invalidate_cache()
        self.assertEquals(self.project.purchase_count, 1)
        self.assertEquals(self.project.purchase_line_count, 1)
        self.assertFalse(self.project.in_invoice_count)
        self.assertFalse(self.project.in_invoiced)
        self.purchase.button_confirm()
        invoice = self.invoice_model.create({
            'partner_id': self.purchase.partner_id.id,
            'purchase_id': self.purchase.id,
            'type': 'in_invoice',
        })
        invoice.purchase_order_change()
        self.project.invalidate_cache()
        self.assertEquals(self.project.in_invoice_count, 1)
        self.assertEquals(self.project.in_invoiced,
                          sum(invoice.mapped("invoice_line_ids.price_subtotal_signed")))
        purchase_domain = [
            ('account_analytic_id', 'in',
             self.project.mapped('analytic_account_id').ids)]
        purchase_lines = self.env['purchase.order.line'].search(
            purchase_domain)
        order_domain = [('id', 'in', purchase_lines.mapped('order_id').ids)]
        purchase_dict = self.project.button_open_purchase_order()
        self.assertEquals(purchase_dict.get('domain'), order_domain)
        purchase_line_dict = self.project.button_open_purchase_order_line()
        self.assertEquals(
            purchase_line_dict.get('domain'), purchase_domain)
        invoice_lines = self.project._get_in_invoices()
        invoice_action = self.browse_ref('account.action_invoice_tree')
        invoice_domain = expression.AND([
            [('id', 'in', invoice_lines.mapped('invoice_id').ids)],
            safe_eval(invoice_action.domain or '[]')])
        invoice_dict = self.project.button_open_purchase_invoice()
        self.assertEquals(invoice_dict.get('domain'), invoice_domain)
        invoice_line_domain = self.project._get_in_invoices(domain=True)
        invoice_line_dict = self.project.button_open_purchase_invoice_line()
        self.assertEquals(invoice_line_dict.get('domain'), invoice_line_domain)
