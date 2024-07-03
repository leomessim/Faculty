from odoo import models, fields, api
from odoo.exceptions import UserError


class CrashClassRecord(models.Model):
    _name = 'crash.class.record'
    _description = 'Crash Class Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', string="Faculty", required=True)
    coordinator_id = fields.Many2one('res.users', string="Coordinator", default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    class_ids = fields.One2many('crash.daily.classes', 'crash_id', string="Classes")
    batch_id = fields.Many2one('logic.base.batch', string="Batch")
    state = fields.Selection(
        [('draft', 'Draft'), ('head_approval', 'Head Approval'), ('accounts_approval', 'Accounts Approval'),
         ('register_payment', 'Register Payment'), ('paid', 'Paid'), ('rejected', 'Rejected')],
        string='State', default='draft', tracking=True
    )

    @api.depends('class_ids.net_hour')
    def _total_hour(self):
        total = 0
        for order in self.class_ids:
            total += order.net_hour
        self.update({
            'total_hour': total,

        })

    total_hour = fields.Float(string='Total Hour', compute='_total_hour', store=True)

    def action_confirm(self):
        self.activity_schedule('faculty.mail_activity_for_crash_record_record',
                               user_id=self.coordinator_id.employee_id.parent_id.user_id.id,
                               note=f'{self.faculty_id.name.name} Crash class records have been added. Please approve.')
        self.write({'state': 'head_approval'})

    def action_head_approve(self):
        if self.env.user.id != self.coordinator_id.employee_id.parent_id.user_id.id:
            raise UserError("You are not authorized to approve this record")
        else:
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                    'activity_type_id', '=', self.env.ref('faculty.mail_activity_for_crash_record_record').id)])
            if activity_id:
                activity_id.action_feedback(feedback='Approved')
            users = self.env.ref('faculty.group_accounting_manager').users
            for i in users:
                self.activity_schedule('faculty.mail_activity_for_crash_record_record', user_id=i.id,
                                       note=f'{self.faculty_id.name.name} Crash class records have been added. Please approve.')
            self.write({'state': 'accounts_approval'})

    def action_head_reject(self):
        if self.env.user.id != self.coordinator_id.employee_id.parent_id.user_id.id:
            raise UserError("You are not authorized to approve this record")
        else:
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                    'activity_type_id', '=', self.env.ref('faculty.mail_activity_for_crash_record_record').id)])
            if activity_id:
                activity_id.action_feedback(feedback='Rejected')

            self.write({'state': 'rejected'})

    def action_accounts_approve(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('faculty.mail_activity_for_crash_record_record').id)])
        if activity_id:
            activity_id.action_feedback(feedback='Approved')
        self.write({'state': 'register_payment'})

    def action_accounts_reject(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('faculty.mail_activity_for_crash_record_record').id)])
        if activity_id:
            activity_id.action_feedback(feedback='Rejected')
        self.write({'state': 'rejected'})

    def action_register_payment(self):

        self.write({'state': 'paid'})


class CrashDailyClasses(models.Model):
    _name = 'crash.daily.classes'
    _description = 'Crash Daily Classes'
    _rec_name = 'crash_id'

    crash_id = fields.Many2one('crash.class.record', string="Crash Class", required=True)
    date = fields.Date(string="Date", required=True)
    # net_hour = fields.Float(string="Net Hour", required=True)
    subject = fields.Char(string="Subject")
    topic = fields.Char(string="Topic")
    from_time = fields.Float(string="From Time")
    to_time = fields.Float(string="To Time")

    @api.depends('from_time', 'to_time')
    def _total_time(self):
        total = 0
        for i in self:
            total = i.to_time - i.from_time
        self.update({
            'net_hour': total
        })

    net_hour = fields.Float(string='Total Time', compute='_total_time', store=True)
