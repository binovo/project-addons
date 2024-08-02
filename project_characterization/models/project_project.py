# Copyright 2018 Xanti Pablo - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    funding_ids = fields.One2many(
        comodel_name="funding.source.project",
        inverse_name="project_id",
        string="Funding Sources",
    )
    code = fields.Char(related="analytic_account_id.code")
    justification_deadline = fields.Date(
        related="analytic_account_id.justification_deadline"
    )
    nonoperative = fields.Boolean(related="analytic_account_id.nonoperative")
    num_code = fields.Char(related="analytic_account_id.num_code")
    op_space_id = fields.Many2one(related="analytic_account_id.op_space_id")
    res_area_id = fields.Many2one(related="analytic_account_id.res_area_id")
    res_area_type_id = fields.Many2one(related="analytic_account_id.res_area_type_id")
    res_character_id = fields.Many2one(related="analytic_account_id.res_character_id")
    res_target_id = fields.Many2one(related="analytic_account_id.res_target_id")
    res_team_id = fields.Many2one(related="analytic_account_id.res_team_id")

    @api.onchange("res_area_id")
    def _onchange_area_id(self):
        self.ensure_one()
        self.nonoperative = self.res_area_id.nonoperative

    @api.onchange("res_area_id", "res_area_type_id")
    def _onchange_area_type(self):
        if self.analytic_account_id:
            self.analytic_account_id._onchange_area_type()


class ResArea(models.Model):
    _inherit = "res.area"

    nonoperative = fields.Boolean(string="Non Operative")
    related_operative_area_ids = fields.Many2many(
        comodel_name="res.area",
        relation="rel_nonop2op_area",
        column1="nonop_area_id",
        column2="op_area_id",
        domain="[('nonoperative', '=', False)]",
    )
