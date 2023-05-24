from odoo import fields, models, _, api
from odoo.exceptions import UserError


class Payout(models.Model):
    _name = 'payout'

    subject_id = fields.Char(string='Subject')

    # classroom_id = fields.Many2one(string='Class room')
    courses_id = fields.Char(string='Course')
    topic = fields.Char(string='Topic')

    start_time = fields.Datetime(string='Start time')
    end_time = fields.Datetime(string='End time')
    payout_id = fields.Many2one('faculty.details')


class FacultySalary(models.Model):
    _name = 'faculty.subject.rate'
    _inherit = 'mail.thread'

    name = fields.Many2one('faculty.details', string='Faculty')
    subject_id = fields.Many2one('subject.details', string='Subject')
    salary_per_hr = fields.Float(string='Salary per hour')
    course_id = fields.Many2one('courses.details', string='Course')
    # name = fields.Char(string='hhhi')


class AccountantPayout(models.Model):
    _name = 'accountant.payout'
    _inherit = 'mail.thread'

    name = fields.Char(string='Faculty')
    course = fields.Char(string='Course')
    create_date = fields.Date('Entry date')
    tax = fields.Float(string='Tax')
    total = fields.Float(string='Total')
    state = fields.Selection(selection=[
        ('draft', 'Not Paid'),
        ('paid', 'Paid'),

    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    duration = fields.Float(string='Duration')
    per_hr_rate = fields.Float(string='Rate Per Hour')
    total_rate = fields.Float(string='Total')
    tds = fields.Float(string='TDS')
    extra_charge = fields.Float('Extra hours')
    # create_date_custome = fields.Date('Custome date')


class TotalPayment(models.Model):
    _name = 'total.payment'
    _inherit = 'mail.thread'
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True)
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]).id,
                                  readonly=True)
    extra_charge = fields.Float('Extra hours')
    advance_remaining = fields.Float(string='Advance pending', readonly=True)
    advance_deduction = fields.Float(string='Advance deduction')
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    amount_tax_id = fields.Monetary(string='Taxes', store=True, readonly=True, currency_field='currency_id',
                                    compute='_compute_tax_id_amount')
    current_status = fields.Selection([
        ('active', 'Active'), ('inactive', 'Inactive')], string='Current status')
    # inactive_date = fields.Date(string='Inactive date')
    transaction_id = fields.Char(string='Transaction id')
    state = fields.Selection([('draft', 'Draft'),
                              ('pay', 'Pending Payment'),
                              ('pay_list', 'Success')], string='Status', default='draft', track_visibility='onchange')

    payment_ids = fields.One2many('payment.details.tree', 'payment_details_id', string='Payment')
    month = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of record', copy=False,
        tracking=True)
    course_id = fields.Many2one('courses.details', string='Course')
    subject_id = fields.Many2one('subject.details', string='Subject')
    class_room = fields.Many2one('class.room', string='Class')
    bank = fields.Char('Bank name')
    ifsc = fields.Char('IFSC')
    account_number = fields.Char('Account number')
    account_holder = fields.Char('Account holder')
    extra_reason = fields.Text('Reason')
    charge = fields.Float()
    check_gst = fields.Char('Tax available')
    amount_to_be_paid = fields.Float(string='Total amount', readonly=True)
    branch = fields.Selection(selection=[
        ('corporate_office', 'Corporate office & City campus'),
        ('cochin_campus', 'Cochin campus'),
        ('calicut_campus', 'Calicut campus'),
        ('kottayam_campus', 'Kottayam campus'),
        ('malappuram_campus', 'Malappuram campus'),
        ('trivandrum_campus', 'Trivandrum campus'),
        ('palakkad_campus', 'Palakkad campus'),
        ('dubai_campus', 'Dubai campus'),
    ], string='Branch', copy=False,
        tracking=True)

    @api.depends('amount_pay_now', 'tax_id.amount')
    def _compute_tax_id_amount(self):
        for rec in self:
            if rec.tax_id:
                for tax in rec.tax_id:
                    rec.amount_tax_id = (rec.amount_pay_now * tax.amount) / 100

            else:
                rec.amount_tax_id = 0
        # print(self.amount_tax_id, 'tax')

    @api.depends('extra_charge', 'extra_payment')
    def _compute_extra_total_amount(self):
        for record in self:
            record.extra_total_accounts = record.extra_charge * record.extra_payment

    extra_total_accounts = fields.Float('extra total', compute='_compute_extra_total_amount', store=True)

    @api.depends('extra_charge')
    def _compute_extra_amount(self):
        sub_rate = self.env['faculty.subject.rate'].search([])
        for rec in sub_rate:
            if self.faculty_id == rec.name and self.course_id == rec.course_id and self.subject_id == rec.subject_id:
                self.extra_payment = self.extra_charge * rec.salary_per_hr
            print(self.extra_payment, 'payment')

    extra_payment = fields.Float('Extra payment', compute='_compute_extra_amount', store=True)

    @api.depends('advance_deduction', 'amount_tax_id', 'amount_to_be_paid', 'extra_payment', 'tds_amount')
    def _compute_total_payable_amount(self):
        for rec in self:
            aa = (rec.amount_to_be_paid - rec.tds_amount) + rec.amount_tax_id
            bb = aa - rec.advance_deduction
            rec.amount_pay_now = bb

    amount_pay_now = fields.Float(string='Amount paying now', store=True, compute='_compute_total_payable_amount')
    amount_tds_check = fields.Float(string='Total excluded tds')

    @api.depends('amount_to_be_paid')
    def _compute_tds(self):
        for rec in self:
            tds = (10 / 100) * rec.amount_to_be_paid
        self.tds_amount = tds

    tds_amount = fields.Float('TDS', compute='_compute_tds', store=True)

    def confirm_payment(self):
        rate = self.env['faculty.subject.rate'].search([])
        advance = self.env['faculty.salary.advance'].search([])
        for rec in advance:
            if self.faculty_id.name.name == rec.employee_id.name.name:
                adv = rec.advance
                self.advance_remaining = adv
                # rec.advance = self.advance_remaining - self.advance_deduction

        if self.faculty_id.gst_status == True:
            self.check_gst = 'Yes'
        else:
            self.check_gst = 'No'
        self.amount_to_be_paid = (self.charge * self.extra_charge) + self.amount_to_be_paid
        # var = 0
        # for rec in rate:
        #     if rec.name.id == self.faculty_id.id:
        #         if rec.course_id == self.course_id:
        #             if rec.subject_id == self.subject_id:
        #                 var = self.extra_charge * rec.salary_per_hr
        # self.amount_pay_now = var + self.amount_to_be_paid
        # self.amount_pay_now = (self.extra_payment + self.amount_to_be_paid) - self.tds_amount
        self.state = 'pay'

    # @api.depends('extra_charge','charge')
    # def _compute_amount_total(self):
    #     for rec in self:
    #         rate = rec.charge * rec.extra_charge
    #     self.amount_to_be_paid = rate + self.amount_pay_now

    # def done_button(self):
    #     payout_list = self.env['accountant.payout'].search([('state', '=', 'draft')])
    #     advance = self.env['faculty.salary.advance'].search([])
    #     print('payout_list.name')
    #     totall = 0
    #     sum = 0
    #     for i in payout_list:
    #         print(i.name, 'my name')
    #         print(self.faculty_id.name.name, 'my')
    #         if i.name == self.faculty_id.name.name:
    #             between_dates = self.from_date <= i.create_date <= self.to_date
    #             if between_dates:
    #                 totall += i.total
    #                 sum += i.extra_charge
    #                 for rec in advance:
    #                     if i.name == rec.employee_id.name.name:
    #                         adv = rec.advance
    #                         self.advance_remaining = adv
    #                     # deduction = totall - adv
    #                     self.amount_to_be_paid = totall
    #                     self.amount_pay_now = totall
    #                     self.current_status = self.faculty_id.current_status
    #                     self.extra_charge = sum
    #                     self.state = 'pay'
    #                 else:
    #                     self.amount_to_be_paid = totall
    #                     self.amount_pay_now = totall
    #                     self.extra_charge = sum
    #                     self.current_status = self.faculty_id.current_status
    #                     self.state = 'pay'

    # else:
    #     raise UserError('No records')

    @api.depends('amount_to_be_paid', 'advance_remaining')
    def _compute_advance_remaining(self):
        for record in self:
            record.total_class_remaining = record.amount_to_be_paid - record.advance_remaining

    total_class_remaining = fields.Float(string='Total remaining amount', compute='_compute_advance_remaining',
                                         store=True)

    def submit_button(self):
        aa = self.env['accountant.payout'].search([])
        bb = self.env['faculty.salary.advance'].search([])
        # for i in aa:
        #     i.state = 'paid'
        for j in bb:
            # for k in aa:
            if j.employee_id.name.name == self.faculty_id.name.name:
                j.advance = self.advance_remaining - self.advance_deduction

        self.state = 'pay_list'


class PayoutWizard(models.TransientModel):
    _name = 'payout.wizard'
    _description = 'Wizard'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    def done(self):
        pay = self.env['accountant.payout'].search([])
        for i in pay:
            if i.name == self.faculty_id.name.name:
                between_dates = self.from_date <= i.create_date <= self.to_date
                if between_dates:
                    # print(any_name.create_date, 'dates')

                    return {
                        'name': 'Payout',
                        'type': 'ir.actions.act_window',
                        'res_model': 'accountant.payout',
                        'view_mode': 'tree,form',
                        'domain': [('name', '=', self.faculty_id.name.name), ('create_date', '>=', self.from_date),
                                   ('create_date', '<=', self.to_date)],
                    }
        else:
            raise UserError('No records')


class PaymentDetailsTree(models.Model):
    _name = 'payment.details.tree'

    start_date = fields.Datetime(string='Start time')
    end_date = fields.Datetime(string='End time')
    break_reason = fields.Char(string='Break reason')
    break_time = fields.Integer(string='Break time')
    topic = fields.Char(string='Topic')
    date = fields.Date(string='Date')
    payment_details_id = fields.Many2one('payment.total', string='Payments record')
    net_hour = fields.Integer(string='Net hour')
    balance = fields.Float(string='Amount')


class PaymentTotal(models.Model):
    _name = 'payment.total'
    _rec_name = 'faculty_id'
    _inherit = 'mail.thread'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True)
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]).id,
                                  readonly=True)
    extra_charge = fields.Float('Extra hours')

    advance_deduction = fields.Float(string='Advance deduction')
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    amount_tax_id = fields.Monetary(string='Taxes', store=True, readonly=True, currency_field='currency_id',
                                    compute='_compute_tax_id_amount')
    current_status = fields.Selection([
        ('active', 'Active'), ('inactive', 'Inactive')], string='Current status')
    # inactive_date = fields.Date(string='Inactive date')
    transaction_id = fields.Integer(string='Transaction id')
    state = fields.Selection([('draft', 'Draft'),
                              ('pay', 'Pending Payment'),
                              ('pay_list', 'Success')], string='Status', default='draft', track_visibility='onchange')

    payment_ids = fields.One2many('payment.details.tree', 'payment_details_id', string='Payment')
    month = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of record', copy=False,
        tracking=True)
    course_id = fields.Many2one('courses.details', string='Course')
    subject_id = fields.Many2one('subject.details', string='Subject')
    class_room = fields.Many2one('class.room', string='Class')
    bank = fields.Char('Bank name')
    ifsc = fields.Char('IFSC')
    account_number = fields.Char('Account number')
    account_holder = fields.Char('Account holder')
    extra_reason = fields.Text('Reason')
    charge = fields.Float()
    check_gst = fields.Char('Tax available')

    remaining_hours = fields.Float()
    standard_hours = fields.Float()
    branch = fields.Selection(selection=[
        ('corporate_office', 'Corporate office & City campus'),
        ('cochin_campus', 'Cochin campus'),
        ('calicut_campus', 'Calicut campus'),
        ('kottayam_campus', 'Kottayam campus'),
        ('malappuram_campus', 'Malappuram campus'),
        ('trivandrum_campus', 'Trivandrum campus'),
        ('palakkad_campus', 'Palakkad campus'),
        ('dubai_campus', 'Dubai campus'),
    ], string='Branch', copy=False,
        tracking=True)
    extra_hr_testing = fields.Float()
    extra_hour_reason = fields.Text()

    @api.depends('remaining_hours', 'total_duration_sum')
    def _compute_set_remaining(self):
        total = 0
        remaining = self.env['payment.total'].search([])
        for rec in remaining:
            if rec.faculty_id == self.faculty_id:
                if rec.class_room == self.class_room and rec.course_id == self.course_id and rec.subject_id == self.subject_id:
                    total += rec.total_duration_sum
                    self.check_remain = total
                else:
                    self.check_remain = self.standard_hours - self.total_duration_sum


    check_remain = fields.Float(string='Total remaining hour', readonly=True, compute='_compute_set_remaining',
                                store=True)

    # @api.depends('check_remain', 'standard_hours')
    # def _compute_real_remaining(self):
    #     for rec in self:
    #         rec.correct_remaining_hours = rec.standard_hours - rec.check_remain

    correct_remaining_hours = fields.Float('Balance standard hours')

    @api.depends('amount_pay_now', 'tax_id.amount')
    def _compute_tax_id_amount(self):
        for rec in self:
            if rec.tax_id:
                for tax in rec.tax_id:
                    rec.amount_tax_id = (rec.amount_pay_now * tax.amount) / 100

            else:
                rec.amount_tax_id = 0
        # print(self.amount_tax_id, 'tax')

    @api.depends('extra_charge', 'extra_payment')
    def _compute_extra_total_amount(self):
        for record in self:
            record.extra_total_accounts = record.extra_charge * record.extra_payment

    extra_total_accounts = fields.Float('extra total', compute='_compute_extra_total_amount', store=True)

    @api.depends('charge', 'extra_charge')
    def _compute_extra_amount(self):
        for rec in self:
            rec.extra_payment = rec.charge * rec.extra_charge

    extra_payment = fields.Float('Extra payment', compute='_compute_extra_amount', store=True)

    amount_tds_check = fields.Float(string='Total excluded tds')

    @api.depends('payment_ids.net_hour')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.payment_ids:
            total += order.net_hour
        self.update({
            'total_duration_sum': total,
        })

    total_duration_sum = fields.Float(string='Total Sum', compute='_amount_all', store=True)

    def confirm_payment(self):
        rate = self.env['faculty.subject.rate'].search([])
        advance = self.env['faculty.salary.advance'].search([])
        self.amount_pay_now = self.amount_pay_now - self.advance_deduction
        for rec in advance:
            if self.faculty_id == rec.employee_id:
                rec.advance = self.advance_remaining - self.advance_deduction
        if self.faculty_id.gst_status == True:
            self.check_gst = 'Yes'
        else:
            self.check_gst = 'No'
        self.state = 'pay'

    @api.depends('course_id')
    def _compute_advanced_remaining(self):
        advance = self.env['faculty.salary.advance'].search([])
        for record in advance:
            if self.faculty_id == record.employee_id:
                adv = record.advance
                self.advance_remaining = adv

                # print('jkk')
                # self.advance_remaining = 11

    advance_remaining = fields.Float(string='Advance pending', compute='_compute_advanced_remaining', store=True)


    #     for rec in self:
    #         rate = rec.charge * rec.extra_charge
    #     self.amount_to_be_paid = rate + self.amount_pay_now

    @api.depends('total_duration_sum')
    def _compute_amount_to_be_paid(self):
        total = 0
        sub_rate = self.env['faculty.subject.rate'].search([])
        for rec in sub_rate:
            if self.faculty_id == rec.name and self.course_id == rec.course_id and self.subject_id == rec.subject_id:
                if self.extra_hr_testing < 0:
                    self.amount_to_be_paid = 0
                elif self.extra_hr_testing > 0:
                    self.amount_to_be_paid = self.extra_hr_testing * rec.salary_per_hr
                elif self.extra_hr_testing == 0:
                    self.amount_to_be_paid = self.total_duration_sum * rec.salary_per_hr
                else:
                    print('ok')
        print(total, 'gg')

    amount_to_be_paid = fields.Float(string='Total amount', readonly=True, compute='_compute_amount_to_be_paid',
                                     store=True)

    @api.depends('advance_deduction', 'amount_tax_id', 'amount_to_be_paid', 'extra_payment', 'tds_amount')
    def _compute_total_payable_amount(self):
        for rec in self:
            aa = (rec.amount_to_be_paid - rec.tds_amount) + rec.amount_tax_id
            bb = aa - self.advance_deduction
            rec.amount_pay_now = bb
            print(aa,'dedu')

    amount_pay_now = fields.Float(string='Amount paying now', store=True, compute='_compute_total_payable_amount')

    @api.depends('amount_to_be_paid', 'extra_payment')
    def _compute_add_extra_hour_charge(self):
        for rec in self:
            rec.added_extra_charge = rec.amount_to_be_paid + rec.extra_payment

    added_extra_charge = fields.Float('added Extra', compute='_compute_add_extra_hour_charge', store=True)

    @api.depends('added_extra_charge')
    def _compute_tds(self):
        for rec in self:
            tds = (10 / 100) * rec.added_extra_charge
        self.tds_amount = tds

    tds_amount = fields.Float('TDS', compute='_compute_tds', store=True)

    @api.depends('amount_to_be_paid', 'advance_remaining')
    def _compute_advance_remaining(self):
        for record in self:
            record.total_class_remaining = record.amount_to_be_paid - record.advance_remaining

    total_class_remaining = fields.Float(string='Total remaining amount', compute='_compute_advance_remaining',
                                         store=True)
    def submit_button(self):
        aa = self.env['accountant.payout'].search([])
        bb = self.env['faculty.salary.advance'].search([])
        # for i in aa:
        #     i.state = 'paid'
        for j in bb:
            # for k in aa:
            if j.employee_id.name.name == self.faculty_id.name.name:
                j.advance = self.advance_remaining - self.advance_deduction

        self.state = 'pay_list'

    def refresh(self):
        # sssss = self.env['payment.total'].search([])
        for i in self:
            for j in i.payment_ids:
                j.net_hour = j.net_hour

