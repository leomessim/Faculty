from odoo import fields, models, _, api


class AdvanceWizard(models.TransientModel):
    _name = 'advance.wizard'
    _description = 'Advance Wizard'

    faculty_id = fields.Many2one('faculty.salary.advance', string='Amount to be paid')
    advance = fields.Float(string='Advance', related='faculty_id.advance')
    advance_deduction = fields.Float(string='Advance Deduction')
    current_payment = fields.Float('Current Payment')
    amount_pay_now = fields.Float()

    @api.depends('faculty_id')
    def _default_field_b(self):
        ss = self.env['faculty.salary.advance'].search([])

    def advance_button(self):
        abs = self.env['accountant.payout'].search([])
        for i in abs:
            i.state = 'paid'
        print('advance')


class FacultySalaryAdvance(models.Model):
    _name = 'faculty.salary.advance'
    _rec_name = 'employee_id'

    # name = fields.Char(string='Name', readonly=True, default=lambda self: 'Adv/')
    employee_id = fields.Many2one('faculty.details', string='Faculty', required=True)
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(), help="Submit date")
    reason = fields.Text(string='Reason', help="Reason")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Advance', required=True)
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string='Department')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted')], string='Status', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contract')

    def submit_to_manager(self):
        self.state = 'submit'
