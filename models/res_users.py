from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    faculty_check = fields.Boolean(string='Faculty', ondelete='restrict', auto_join=True)
