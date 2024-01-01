from odoo import models, fields, api, _


class FacultyDailyRecordLockDate(models.Model):
    _name = 'faculty.daily.record.lock.date'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lock_day'

    lock_day = fields.Integer(string='Lock Day')
