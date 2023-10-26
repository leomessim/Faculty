from odoo import fields, models, api, _


class YoutubeClassRecord(models.Model):
    _name = 'youtube.class.record'
    _description = 'Youtube Class Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True,
                                 domain="[('name.youtube_faculty', '=', True)]")
    month_of_record = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string='Month', required=True)
    youtube_ids = fields.One2many('youtube.daily.records', 'youtube_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('hr_approval', 'HR Approval'), ('accounts_approval', 'Accounts Approval'),
         ('register_payment', 'Register Payment'), ('paid', 'Paid'), ('rejected', 'Rejected')],
        string='State', default='draft', tracking=True
    )

    @api.depends('youtube_ids.net_hour')
    def _total_hour(self):
        total = 0
        for order in self.youtube_ids:
            total += order.net_hour
        self.update({
            'total_hour': total,

        })

    total_hour = fields.Float(string='Total Hour', compute='_total_hour', store=True)

    @api.depends('total_hour')
    def _month_salary(self):
        rate = self.env['youtube.faculty.rate'].search([('faculty_id', '=', self.faculty_id.id)], limit=1, order='id desc')
        for order in self:
            order.month_salary = order.total_hour * rate.rate

    month_salary = fields.Float(string='Month Salary', compute='_month_salary', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    def action_confirm(self):
        users = self.env.ref('faculty.group_hr').users
        for i in self:
            for user_id in users:
                i.activity_schedule('faculty.mail_for_youtube_activity', user_id=user_id.id,
                                    note=f'{i.faculty_id.name}  YouTube class records have been added. Please approve.')
        self.write({'state': 'hr_approval'})

    def action_hr_approve(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), (
                'activity_type_id', '=', self.env.ref('faculty.mail_for_youtube_activity').id)])
        activity_id.action_feedback(feedback=f'Youtube class approved.')

        accounts = self.env.ref('faculty.group_accounting_manager').users
        for i in self:
            for user_id in accounts:
                i.activity_schedule('faculty.mail_for_youtube_activity', user_id=user_id.id,
                                    note=f'{i.faculty_id.name}  YouTube class records have been added. Please approve.')
        self.write({'state': 'accounts_approval'})

    def action_accounts_approve(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), (
                'activity_type_id', '=', self.env.ref('faculty.mail_for_youtube_activity').id)])
        activity_id.action_feedback(feedback=f'Youtube class approved.')
        self.write({'state': 'register_payment'})

    def action_register_payment(self):
        self.write({'state': 'paid'})

    def action_reject(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), (
                'activity_type_id', '=', self.env.ref('faculty.mail_for_youtube_activity').id)])
        activity_id.action_feedback(feedback=f'Youtube class rejected.')
        self.write({'state': 'rejected'})

    def action_return_to_draft(self):
        self.write({'state': 'draft'})

    def action_payment(self):
        self.write({'state': 'paid'})


class YoutubeDailyRecords(models.Model):
    _name = 'youtube.daily.records'
    _description = 'Youtube Daily Records'

    date = fields.Date(string='Date', required=True)
    subject = fields.Char(string='Subject')
    topic = fields.Char(string='Topic')
    net_hour = fields.Float(string='Net Hour', required=True)
    youtube_id = fields.Many2one('youtube.class.record', string='Youtube Id')
