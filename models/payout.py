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

    salary_per_hr = fields.Float(string='Salary per hour')
    course_id = fields.Many2one('courses.details', string='Course')
    subject_id = fields.Many2one('subject.details', domain="[('course_sub_id', '=', course_id)]", string='Subject')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    # name = fields.Char(string='hhhi')
    old_rate_ids = fields.One2many('rate.history', 'old_rate_id', string='Rate History', compute='old_salary_hr', store=True)

    @api.depends('salary_per_hr')
    def old_salary_hr(self):
        new = []
        datas = {
            'old_rate': self.salary_per_hr,
            'date_update': self.create_date,
            'name': self.env.user.name
        }
        new.append((0, 0, datas))
        self.old_rate_ids = new


class RateHistory(models.Model):
    _name = 'rate.history'
    _inherit = 'mail.thread'

    old_rate = fields.Float(string='Old Subject Rate')
    date_update = fields.Date(string='Update Date')
    name = fields.Char(string='Name')
    old_rate_id = fields.Many2one('faculty.subject.rate', string='old Rate')




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
    tds = fields.Float(string='TDS to be deducted')
    extra_charge = fields.Float('Extra hours')
    # create_date_custome = fields.Date('Custome date')


# class TotalPayment(models.Model):
#     _name = 'total.payment'


#
#     faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True)
#     from_date = fields.Date(string='From Date')
#     to_date = fields.Date(string='To Date')
#
#     currency_id = fields.Many2one('res.currency',
#                                   default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]).id,
#                                   readonly=True)
#     extra_charge = fields.Float('Extra hours')
#     advance_remaining = fields.Float(string='Advance pending', readonly=True)
#     advance_deduction = fields.Float(string='Advance deduction')
#     tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
#     amount_tax_id = fields.Monetary(string='Taxes', store=True, readonly=True, currency_field='currency_id',
#                                     compute='_compute_tax_id_amount')
#     current_status = fields.Selection([
#         ('active', 'Active'), ('inactive', 'Inactive')], string='Current status')
#     # inactive_date = fields.Date(string='Inactive date')
#     transaction_id = fields.Char(string='Transaction id')
#     state = fields.Selection([('draft', 'Draft'),
#                               ('pay', 'Pending Payment'),
#                               ('pay_list', 'Success')], string='Status', default='draft', track_visibility='onchange')
#
#     payment_ids = fields.One2many('payment.details.tree', 'payment_details_id', string='Payment')
#     month = fields.Selection([
#         ('january', 'January'), ('february', 'February'),
#         ('march', 'March'), ('april', 'April'),
#         ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
#         ('september', 'September'), ('october', 'October'), ('november', 'November'),
#         ('december', 'December')],
#         string='Month of record', copy=False,
#         tracking=True)
#     course_id = fields.Many2one('courses.details', string='Course')
#     subject_id = fields.Many2one('subject.details', string='Subject')
#     class_room = fields.Many2one('class.room', string='Class')
#     bank = fields.Char('Bank name')
#     ifsc = fields.Char('IFSC')
#     account_number = fields.Char('Account number')
#     account_holder = fields.Char('Account holder')
#     extra_reason = fields.Text('Reason')
#     charge = fields.Float()
#     check_gst = fields.Char('Tax available')
#     amount_to_be_paid = fields.Float(string='Total amount', readonly=True)
#     branch = fields.Selection(selection=[
#         ('corporate_office', 'Corporate office & City campus'),
#         ('cochin_campus', 'Cochin campus'),
#         ('calicut_campus', 'Calicut campus'),
#         ('kottayam_campus', 'Kottayam campus'),
#         ('malappuram_campus', 'Malappuram campus'),
#         ('trivandrum_campus', 'Trivandrum campus'),
#         ('palakkad_campus', 'Palakkad campus'),
#         ('dubai_campus', 'Dubai campus'),
#     ], string='Branch', copy=False,
#         tracking=True)
#
#     @api.depends('amount_pay_now', 'tax_id.amount')
#     def _compute_tax_id_amount(self):
#         for rec in self:
#             if rec.tax_id:
#                 for tax in rec.tax_id:
#                     rec.amount_tax_id = (rec.amount_pay_now * tax.amount) / 100
#
#             else:
#                 rec.amount_tax_id = 0
#         # print(self.amount_tax_id, 'tax')
#
#     @api.depends('extra_charge', 'extra_payment')
#     def _compute_extra_total_amount(self):
#         for record in self:
#             record.extra_total_accounts = record.extra_charge * record.extra_payment
#
#     extra_total_accounts = fields.Float('extra total', compute='_compute_extra_total_amount', store=True)
#
#     @api.depends('extra_charge')
#     def _compute_extra_amount(self):
#         sub_rate = self.env['faculty.subject.rate'].search([])
#         for rec in sub_rate:
#             if self.faculty_id == rec.name and self.course_id == rec.course_id and self.subject_id == rec.subject_id:
#                 self.extra_payment = self.extra_charge * rec.salary_per_hr
#             print(self.extra_payment, 'payment')
#
#     extra_payment = fields.Float('Extra payment', compute='_compute_extra_amount', store=True)
#
#     @api.depends('advance_deduction', 'amount_tax_id', 'amount_to_be_paid', 'extra_payment', 'tds_amount')
#     def _compute_total_payable_amount(self):
#         for rec in self:
#             aa = (rec.amount_to_be_paid - rec.tds_amount) + rec.amount_tax_id
#             bb = aa - rec.advance_deduction
#             rec.amount_pay_now = bb
#
#     amount_pay_now = fields.Float(string='Net payable', store=True, compute='_compute_total_payable_amount')
#     amount_tds_check = fields.Float(string='Total excluded tds')
#
#     @api.depends('amount_to_be_paid')
#     def _compute_tds(self):
#         for rec in self:
#             tds = (10 / 100) * rec.amount_to_be_paid
#         self.tds_amount = tds
#
#     tds_amount = fields.Float('TDS', compute='_compute_tds', store=True)
#
#     def confirm_payment(self):
#         rate = self.env['faculty.subject.rate'].search([])
#         advance = self.env['faculty.salary.advance'].search([])
#         for rec in advance:
#             if self.faculty_id.name.name == rec.employee_id.name.name:
#                 adv = rec.advance
#                 self.advance_remaining = adv
#                 # rec.advance = self.advance_remaining - self.advance_deduction
#
#         if self.faculty_id.gst_status == True:
#             self.check_gst = 'Yes'
#         else:
#             self.check_gst = 'No'
#         self.amount_to_be_paid = (self.charge * self.extra_charge) + self.amount_to_be_paid
#         # var = 0
#         # for rec in rate:
#         #     if rec.name.id == self.faculty_id.id:
#         #         if rec.course_id == self.course_id:
#         #             if rec.subject_id == self.subject_id:
#         #                 var = self.extra_charge * rec.salary_per_hr
#         # self.amount_pay_now = var + self.amount_to_be_paid
#         # self.amount_pay_now = (self.extra_payment + self.amount_to_be_paid) - self.tds_amount
#         self.state = 'pay'
#
#     # @api.depends('extra_charge','charge')
#     # def _compute_amount_total(self):
#     #     for rec in self:
#     #         rate = rec.charge * rec.extra_charge
#     #     self.amount_to_be_paid = rate + self.amount_pay_now
#
#     # def done_button(self):
#     #     payout_list = self.env['accountant.payout'].search([('state', '=', 'draft')])
#     #     advance = self.env['faculty.salary.advance'].search([])
#     #     print('payout_list.name')
#     #     totall = 0
#     #     sum = 0
#     #     for i in payout_list:
#     #         print(i.name, 'my name')
#     #         print(self.faculty_id.name.name, 'my')
#     #         if i.name == self.faculty_id.name.name:
#     #             between_dates = self.from_date <= i.create_date <= self.to_date
#     #             if between_dates:
#     #                 totall += i.total
#     #                 sum += i.extra_charge
#     #                 for rec in advance:
#     #                     if i.name == rec.employee_id.name.name:
#     #                         adv = rec.advance
#     #                         self.advance_remaining = adv
#     #                     # deduction = totall - adv
#     #                     self.amount_to_be_paid = totall
#     #                     self.amount_pay_now = totall
#     #                     self.current_status = self.faculty_id.current_status
#     #                     self.extra_charge = sum
#     #                     self.state = 'pay'
#     #                 else:
#     #                     self.amount_to_be_paid = totall
#     #                     self.amount_pay_now = totall
#     #                     self.extra_charge = sum
#     #                     self.current_status = self.faculty_id.current_status
#     #                     self.state = 'pay'
#
#     # else:
#     #     raise UserError('No records')
#
#     @api.depends('amount_to_be_paid', 'advance_remaining')
#     def _compute_advance_remaining(self):
#         for record in self:
#             record.total_class_remaining = record.amount_to_be_paid - record.advance_remaining
#
#     total_class_remaining = fields.Float(string='Total remaining amount', compute='_compute_advance_remaining',
#                                          store=True)
#
#     def submit_button(self):
#         aa = self.env['accountant.payout'].search([])
#         bb = self.env['faculty.salary.advance'].search([])
#         # for i in aa:
#         #     i.state = 'paid'
#         for j in bb:
#             # for k in aa:
#             if j.employee_id.name.name == self.faculty_id.name.name:
#                 j.advance = self.advance_remaining - self.advance_deduction
#
#         self.state = 'pay_list'
#

class PayoutWizard(models.TransientModel):
    _name = 'payout.wizard'
    _description = 'Wizard'

    journal = fields.Many2one('res.partner.bank', string='Journal', required=True)
    amount = fields.Float(string='Amount')
    payment_date = fields.Date(string='Payment Date', required=True)
    transaction_id = fields.Char(string='Transaction Id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def default_get(self, fields):
        res = super(PayoutWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        brws = self.env['payment.total'].browse(int(active_id))
        if active_id:
            res['amount'] = brws.amount_pay_now
        return res

    def done(self):
        ss = self.env['payment.total'].search([])

        for i in ss:
            i.state = 'pay_list'

    def cancel(self):
        ss = self.env['payment.total'].search([])
        for i in ss:
            i.state = 'pay'


class PaymentDetailsTree(models.Model):
    _name = 'payment.details.tree'

    start_date = fields.Float(string='Start time')
    end_date = fields.Float(string='End time')
    break_reason = fields.Char(string='Break reason')
    break_time = fields.Float(string='Break time')
    topic = fields.Char(string='Topic')
    date = fields.Date(string='Date')
    payment_details_id = fields.Many2one('payment.total', string='Payments record')
    net_hour = fields.Float(string='Net hour')
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
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    extra_charge = fields.Float('Extra hour eligible for payment')

    advance_deduction = fields.Float(string='Advance deduction')
    tax_id = fields.Many2many('account.tax', string='GST Slab', context={'active_test': False})

    current_status = fields.Selection([
        ('active', 'Active'), ('inactive', 'Inactive')], string='Current status')
    # inactive_date = fields.Date(string='Inactive date')
    transaction_id = fields.Integer(string='Transaction id')
    state = fields.Selection([('draft', 'Draft'),
                              ('pay', 'Register Payment'),
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
    referral_id = fields.Char('Referral id')
    date_of_payment = fields.Date('Date')

    check_gst = fields.Char('Tax available')

    remaining_hours = fields.Float()
    standard_hours = fields.Float('Standard hour allocated for subject')
    branch = fields.Many2one('logic.branches', 'Branch')
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

    @api.depends('course_id', 'subject_id', 'faculty_id', 'charge')
    def _sub_charge(self):
        sub_rate = self.env['faculty.subject.rate'].search([])
        for rec in sub_rate:
            if rec.name == self.faculty_id and self.course_id == rec.course_id and self.subject_id == rec.subject_id:
                self.charge = rec.salary_per_hr

    charge = fields.Float(compute='_sub_charge', store=True)

    # @api.depends('check_remain', 'standard_hours')
    # def _compute_real_remaining(self):
    #     for rec in self:
    #         rec.correct_remaining_hours = rec.standard_hours - rec.check_remain

    correct_remaining_hours = fields.Float('Balance standard hours')

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

    extra_payment = fields.Float('Extra hour payment', compute='_compute_extra_amount', store=True)

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

    total_duration_sum = fields.Float(string='Gross hours', compute='_amount_all', store=True)

    def confirm_payment(self):
        rate = self.env['faculty.subject.rate'].search([])
        advance = self.env['faculty.salary.advance'].search([])
        # self.amount_pay_now = self.amount_pay_now - self.advance_deduction
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

    @api.depends('total_duration_sum', 'extra_hr_testing')
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

    amount_to_be_paid = fields.Float(string='Subject rate (/hr)', readonly=True, compute='_compute_amount_to_be_paid',
                                     store=True)
    class_hours_till = fields.Float('Class hours till now')

    @api.depends('subject_id', 'course_id', 'faculty_id')
    def rate_subject(self):
        sub_rate = self.env['faculty.subject.rate'].search([])
        for rec in sub_rate:
            if rec.name == self.faculty_id and self.course_id == rec.course_id and self.subject_id == rec.subject_id:
                self.rate_of_sub = rec.salary_per_hr

    rate_of_sub = fields.Float(compute='rate_subject', store=True, string='Subject rate (/h)')

    @api.depends('amount_to_be_paid', 'extra_payment')
    def _compute_add_extra_hour_charge(self):
        for rec in self:
            rec.added_extra_charge = rec.amount_to_be_paid + rec.extra_payment

    added_extra_charge = fields.Float('added Extra', compute='_compute_add_extra_hour_charge', store=True)

    @api.depends('total_net_hour_amount')
    def _total_duration_rate(self):
        dd = self.env['faculty.subject.rate'].search([])
        for i in dd:
            if self.faculty_id == i.faculty_id and self.course_id == i.course_id and self.subject_id == i.subject_id:
                self.duration_amount = self.total_net_hour_amount * i.salary_pr_hy

    duration_amount = fields.Float('Total class payment', comput='_total_duration_rate', store=True)

    @api.depends('added_payment_extra')
    def _compute_tds(self):
        for rec in self:
            tds = (10 / 100) * rec.added_payment_extra
        self.tds_amount = tds

    tds_amount = fields.Float('TDS to be deducted', compute='_compute_tds', store=True)

    @api.depends('added_payment_extra', 'tds_amount')
    def _tds_extra_payment(self):
        for i in self:
            i.added_tds_payment = i.added_payment_extra - i.tds_amount

    added_tds_payment = fields.Float(compute='_tds_extra_payment', store=True,
                                     string='Gross payable after TDS deduction')

    @api.depends('added_tds_payment', 'tax_id.amount', 'added_payment_extra')
    def _compute_tax_id_amount(self):
        for rec in self:
            if rec.tax_id:
                for tax in rec.tax_id:
                    rec.amount_tax_id = (rec.added_payment_extra * tax.amount) / 100

            else:
                rec.amount_tax_id = 0

    amount_tax_id = fields.Monetary(string='GST Amount', store=True, readonly=True, currency_field='currency_id',
                                    compute='_compute_tax_id_amount')

    @api.depends('added_tds_payment', 'tax_id', 'amount_tax_id', 'added_payment_extra')
    def _tax_extra_payment(self):
        for i in self:
            i.added_tax_payment = i.added_payment_extra + i.amount_tax_id - i.tds_amount

    added_tax_payment = fields.Float(compute='_tax_extra_payment', store=True, string='Gross payable')



    @api.depends('amount_to_be_paid', 'advance_remaining')
    def _compute_advance_remaining(self):
        for record in self:
            record.total_class_remaining = record.amount_to_be_paid - record.advance_remaining

    total_class_remaining = fields.Float(string='Total remaining amount', compute='_compute_advance_remaining',
                                         store=True)

    @api.depends('amount_to_be_paid', 'extra_payment')
    def added_total_extra_payment(self):
        for i in self:
            if i.extra_payment != 0:
                if i.amount_to_be_paid != i.extra_payment:
                    i.added_payment_extra = i.amount_to_be_paid + i.extra_payment
                else:
                    i.added_payment_extra = i.amount_to_be_paid
            else:
                i.added_payment_extra = i.amount_to_be_paid

    added_payment_extra = fields.Float(compute='added_total_extra_payment', store=True,
                                       string='Gross payable before TDS')

    @api.depends('added_payment_extra', 'advance_deduction', 'added_tax_payment')
    def advance_deduction_total(self):
        for rec in self:
            rec.advance_ded_total = rec.added_tax_payment - rec.advance_deduction

    advance_ded_total = fields.Float('Net payable', compute='advance_deduction_total', store=True)

    @api.depends('amount_tax_id', 'added_payment_extra')
    def _gst_added_gross_before_tds(self):
        for i in self:
            i.added_gross_before_tds_custom = i.added_payment_extra + i.amount_tax_id

    added_gross_before_tds_custom = fields.Float(compute='_gst_added_gross_before_tds', store=True, string='Gross payable before TDS + GST')

    #     for i in self:
    #         i.added_gross_before_tds = i.added_payment_extra + i.amount_tax_id
    #
    # added_gross_before_tds = fields.Float(compute='_gst_added_gross_before_tds', store=True,
    #                                       string='Gross payable before TDS + GST')

    @api.depends('added_tds_payment', 'added_tax_payment', 'amount_to_be_paid', 'extra_payment', 'added_payment_extra',
                 'advance_ded_total')
    def _compute_total_payable_amount(self):
        for rec in self:
            # aa = (rec.amount_to_be_paid - rec.tds_amount) + rec.amount_tax_id
            # bb = aa - self.advance_deduction
            # rec.amount_pay_now = bb
            rec.amount_pay_now = rec.advance_ded_total

    amount_pay_now = fields.Float(string='Net payable', store=True, compute='_compute_total_payable_amount')

    # @api.depends('payment_ids.net_hour')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     total = 0
    #     for order in self.payment_ids:
    #         total += order.net_hour
    #     self.update({
    #         'total_net_hour_amount': total,
    #     })
    #
    # total_net_hour_amount = fields.Float(string='Total net hour', compute='_amount_all', store=True)

    def submit_button(self):
        print('kool')
        # sss = self.env['payout.wizard'].search([])
        # for i in sss:
        #     i.amount = self.amount_pay_now
        # aa = self.env['accountant.payout'].search([])
        # bb = self.env['faculty.salary.advance'].search([])
        # # for i in aa:
        # #     i.state = 'paid'
        # for j in bb:
        #     # for k in aa:
        #     if j.employee_id.name.name == self.faculty_id.name.name:
        #         j.advance = self.advance_remaining - self.advance_deduction

        self.state = 'pay_list'

    def refresh(self):
        sssss = self.env['faculty.subject.rate'].search([])
        adv = self.env['faculty.salary.advance'].search([])
        for i in self:
            for j in i.payment_ids:
                j.net_hour = j.net_hour
            for ii in sssss:
                if ii.name == self.faculty_id and ii.course_id == self.course_id and self.subject_id == ii.subject_id:
                    i.rate_of_sub = ii.salary_per_hr
            for advance in adv:
                if self.faculty_id == advance.employee_id:
                    self.advance_remaining = advance.advance
            self.subject_id = self.subject_id
