from odoo import models, fields, api, _


class YoutubeFacultyRate(models.Model):
    _name = 'youtube.faculty.rate'
    _description = 'Youtube Faculty Rate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True, domain="[('name.youtube_faculty', '=', True)]")
    rate = fields.Float(string='Salary Per Hour', required=True)
