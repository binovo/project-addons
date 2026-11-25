# Copyright 2018 Gontzal Gomez - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    goal_ids = fields.One2many(
        comodel_name="project.goal",
        inverse_name="project_id",
        string="Goals",
        copy=True,
        context={"active_test": False},
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        default_goals = self.env["project.goal.goal"].search(
            [
                ("default_goal", "=", True),
                ("type_id", "!=", False),
            ]
        )
        res.update(
            {
                "goal_ids": [
                    (
                        0,
                        0,
                        {
                            "type_id": x.type_id.id,
                            "goal_id": x.id,
                            "name": x.description,
                            "active": True,
                        },
                    )
                    for x in default_goals
                ],
            }
        )
        return res

    def write(self, vals):
        """Archive or unarchive the project's goals together with the project."""
        res = super().write(vals) if vals else True
        if "active" in vals:
            self.with_context(active_test=False).mapped("goal_ids").write(
                {"active": vals["active"]}
            )
        return res
