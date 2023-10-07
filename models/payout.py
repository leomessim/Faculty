from odoo import fields, models, _, api
from odoo.exceptions import UserError
import requests
import base64
from pdf2docx import parse
from datetime import date, datetime


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
    _description = 'Rates'

    name = fields.Many2one('faculty.details', string='Faculty', required=True)
    salary_per_hr = fields.Float(string='Salary per hour', required=True)
    course_id = fields.Many2one('courses.details', string='Course',required=True)
    subject_id = fields.Many2one('subject.details', domain="[('course_sub_id', '=', course_id)]", string='Subject', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    # name = fields.Char(string='hhhi')
    old_rate_ids = fields.One2many('rate.history', 'old_rate_id', string='Rate History', compute='old_salary_hr',
                                   store=True)

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


class PayoutWizard(models.TransientModel):
    _name = 'payout.wizard'
    _description = 'Wizard'

    journal = fields.Many2one('res.partner.bank', string='Journal', required=True)
    amount = fields.Float(string='Amount')
    payment_date = fields.Date(string='Payment Date', required=True)
    transaction_id = fields.Char(string='Transaction Id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    current_id = fields.Integer(string='Current Id')
    file_ids = fields.Many2many('ir.attachment', string='Attachments')

    current_record_id = fields.Integer(string='Current Record Id')
    report_file = fields.Binary(string='Report File')

    @api.model
    def default_get(self, fields):
        res = super(PayoutWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        brws = self.env['payment.total'].browse(int(active_id))
        if active_id:
            res['amount'] = brws.amount_pay_now
            res['current_id'] = brws.id
            res['current_record_id'] = brws.current_id
            res['transaction_id'] = brws.transaction_id

        return res

    # date_field = fields.Date(string='Date Field')
    #
    # @api.model
    # def update_date(self):
    #     for record in self:
    #         # Set the date field to the current date
    #         record.date_field = fields.Date.today()

    @api.onchange('payment_date')
    def onchange_payment_date(self):
        print('wwwwww')
        active_wizard_id = self.env.context.get('active_id')
        record = self.env['payment.total'].sudo().search([('id', '=', active_wizard_id)])
        for rec in record:
            print(rec.faculty_id.email_address, 'email')
        print("Active Wizard ID:", active_wizard_id)

    def done(self):
        purchase_ids = self.env.context.get('active_ids', [])
        purchase_rec = self.env['payment.total'].browse(purchase_ids)
        print(purchase_ids, 'wiz')
        print(purchase_rec, 'pur')
        purchase_rec.date_of_payment = self.payment_date
        purchase_rec.transaction_id = self.transaction_id
        purchase_rec.state = 'pay_list'
        current_date = datetime.now().strftime('%Y-%m-%d')
        # data = {
        #     'docs': purchase_rec,  # Your report data
        #     'context': {'current_date': current_date},
        #
        # }

        email = []
        active_wizard_id = self.env.context.get('active_id')
        record = self.env['payment.total'].sudo().search([('id', '=', active_wizard_id)])
        pdf_content = \
            self.env.ref('faculty.report_faculty_payout')._render_qweb_pdf(record.id,
                                                                           )[
                0]
        outfile = open('/tmp/temp.pdf', 'wb')
        outfile.write(pdf_content)
        outfile.close()
        open('/tmp/temp.docx', 'w')
        parse('/tmp/temp.pdf', '/tmp/temp.docx')
        self.report_file = base64.b64encode(open('/tmp/temp.pdf', 'rb').read())
        for rec in record:
            email_temp = rec.faculty_id.email_address
            email.append(email_temp)
        partner = self.env['res.partner'].browse(self._context.get('active_id'))

        # Create the email message
        for rec in record:
            if rec.faculty_id.email_address:
                email_values = {
                    'subject': 'Faculty Payment',
                    'email_to': rec.faculty_id.email_address,  # Use the client's email address
                    'body_html': 'Payment successfully processed.',
                    # 'attachment_ids': [(6, 0, self.file_ids.ids)]
                }
                email = self.env['mail.mail'].sudo().create(email_values)
                # print(email_values['attachment_ids'])
                attachment_values = {
                    'name': 'payment_slip.pdf',
                    'datas': self.report_file,
                    'res_model': 'mail.mail',
                    'res_id': self.id,
                }

                attachment = self.env['ir.attachment'].sudo().create(attachment_values)

                # Send the email
                email.attachment_ids = [(4, attachment.id)]
                email.send()

                # Send the email
                # email = self.env['mail.mail'].sudo().create(email_values)
                # email.send()
                record = self.env['daily.class.record'].sudo().search([])
                for rec in record:
                    if self.current_record_id == rec.id:
                        rec.state = 'paid'
                return {'type': 'ir.actions.act_window_close'}

        # ss = self.env['payment.total'].sudo().search([])
        #
        # for i in ss:
        #     if self.current_id == i.id:
        #         i.state = 'pay_list'

    def cancel(self):
        ss = self.env['payment.total'].search([])
        for i in ss:
            if self.current_id == i.id:
                i.state = 'pay'


class PaymentDetailsTree(models.Model):
    _name = 'payment.details.tree'

    start_date = fields.Float(string='Start time')
    end_date = fields.Float(string='End time')
    break_reason = fields.Char(string='Break reason')
    break_time = fields.Float(string='Break time')
    topic = fields.Char(string='Topic')
    date = fields.Date(string='Date')
    payment_details_id = fields.Many2one('payment.total', string='Payments record', ondelete='cascade')
    net_hour = fields.Float(string='Net hour')
    balance = fields.Float(string='Amount')


class PaymentTotal(models.Model):
    _name = 'payment.total'
    _rec_name = 'faculty_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payment'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True, ondelete='restrict')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    current_id = fields.Integer(string='Current Id')
    attach_file = fields.Binary(string='Attach File')

    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]).id,
                                  readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    extra_charge = fields.Float('Extra hour eligible for payment')
    advance_deduction = fields.Float(string='Advance deduction')
    tax_id = fields.Many2many('account.tax', string='GST Slab', context={'active_test': False}, ondelete='restrict')

    current_status = fields.Selection([
        ('active', 'Active'), ('inactive', 'Inactive')], string='Current status')
    # inactive_date = fields.Date(string='Inactive date')
    transaction_id = fields.Char(string='Transaction id')
    state = fields.Selection([('draft', 'Draft'),
                              ('pay', 'Register Payment'),
                              ('pay_list', 'Success'), ('rejected', 'Rejected')], string='Status', default='draft',
                             track_visibility='onchange')

    payment_ids = fields.One2many('payment.details.tree', 'payment_details_id', string='Payment')
    month = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of record', copy=False,
        tracking=True)
    course_id = fields.Many2one('courses.details', string='Course', ondelete='restrict')
    subject_id = fields.Many2one('subject.details', string='Subject', ondelete='restrict')
    class_room = fields.Many2one('class.room', string='Class', ondelete='restrict')
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
    report_file = fields.Binary()
    current_date = fields.Date()

    @api.depends('remaining_hours', 'total_duration_sum')
    def _compute_set_remaining(self):
        total = 0
        remaining = self.env['payment.total'].search([])
        for rec in remaining:
            if rec.faculty_id == self.faculty_id:
                if rec.class_room == self.class_room and self.branch == rec.branch and rec.course_id == self.course_id and rec.subject_id == self.subject_id:
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

    correct_remaining_hours = fields.Float('Balance standard hours')

    def compute_count(self):
        for record in self:
            record.form_count = self.env['daily.class.record'].search_count(
                [('id', '=', self.current_id)])

    form_count = fields.Integer(compute='compute_count')

    def get_payments_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Class Record',
            'view_mode': 'tree,form',
            'res_model': 'daily.class.record',
            'domain': [('id', '=', self.current_id)],
            'context': "{'create': False}"
        }

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
        fac_record = self.env['daily.class.record'].sudo().search([('id', '=', self.current_id)])
        fac_record.write({'state': 'register_payment'})
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
                    self.amount_to_be_paid = self.extra_hr_testing * self.rate_of_sub
                elif self.extra_hr_testing == 0:
                    self.amount_to_be_paid = self.total_duration_sum * self.rate_of_sub
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

    @api.depends('added_payment_extra', 'advance_deduction', 'added_tax_payment')
    def advance_deduction_total(self):
        for rec in self:
            rec.advance_ded_total = rec.added_tax_payment - rec.advance_deduction

    advance_ded_total = fields.Float('Net payable', compute='advance_deduction_total', store=True)

    @api.depends('amount_tax_id', 'added_payment_extra')
    def _gst_added_gross_before_tds(self):
        for i in self:
            i.added_gross_before_tds_custom = i.added_payment_extra + i.amount_tax_id

    added_gross_before_tds_custom = fields.Float(compute='_gst_added_gross_before_tds', store=True,
                                                 string='Gross payable before TDS + GST')

    @api.depends('added_tds_payment', 'added_tax_payment', 'amount_to_be_paid', 'extra_payment', 'added_payment_extra',
                 'advance_ded_total')
    def _compute_total_payable_amount(self):
        for rec in self:
            rec.amount_pay_now = rec.advance_ded_total

    amount_pay_now = fields.Float(string='Net payable', store=True, compute='_compute_total_payable_amount')

    def submit_button(self):
        print('kool')

        self.state = 'pay_list'

    def refresh(self):
        sssss = self.env['faculty.subject.rate'].search([])
        adv = self.env['faculty.salary.advance'].search([])
        daily_record = self.env['daily.class.record'].search([('id', '=', self.current_id)])
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
            i.added_total_extra_payment()

    def reject_button(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject.reason.payment',
            'view_mode': 'form',
            'target': 'new',

        }

    def action_selected_records_state_paid(self):
        records = self.env.context.get('active_ids', [])
        paid = self.env['payment.total'].search([('id', 'in', records)])
        # email = []
        for record in paid:
            print(record.faculty_id.name, 'faculty')
            pdf_content = \
                self.env.ref('faculty.report_faculty_payout')._render_qweb_pdf(record.id,
                                                                               )[
                    0]
            outfile = open('/tmp/temp.pdf', 'wb')
            outfile.write(pdf_content)
            outfile.close()
            open('/tmp/temp.docx', 'w')
            parse('/tmp/temp.pdf', '/tmp/temp.docx')
            self.report_file = base64.b64encode(open('/tmp/temp.pdf', 'rb').read())
            # for rec in record:
            #     email_temp = rec.faculty_id.email_address
            #     email.append(email_temp)
            # partner = self.env['res.partner'].browse(self._context.get('active_id'))

            # Create the email message
            for rec in record:
                if rec.faculty_id.email_address:
                    email_values = {
                        'subject': 'Faculty Payment',
                        'email_to': rec.faculty_id.email_address,  # Use the client's email address
                        'body_html': 'Payment successfully processed.',
                        # 'attachment_ids': [(6, 0, self.file_ids.ids)]
                    }
                    email = self.env['mail.mail'].sudo().create(email_values)
                    # print(email_values['attachment_ids'])
                    attachment_values = {
                        'name': 'payment_slip.pdf',
                        'datas': self.report_file,
                        'res_model': 'mail.mail',
                        'res_id': self.id,
                    }

                    attachment = self.env['ir.attachment'].sudo().create(attachment_values)

                    # Send the email
                    email.attachment_ids = [(4, attachment.id)]
                    email.send()

            class_rec = self.env['daily.class.record'].search([])

            for rec in class_rec:
                if rec.id == record.current_id:
                    rec.state = 'paid'
            #     rec.state = 'paid'
        print(records, 'records')


class RejectReason(models.TransientModel):
    _name = 'reject.reason.payment'

    reason = fields.Char('Reason')

    def action_done(self):
        payment = self.env['payment.total'].search([('id', '=', self._context['active_id'])])
        if payment:
            daily_record = self.env['daily.class.record'].search([('id', '=', payment.current_id)])
            daily_record.state = 'rejected'
            payment.state = 'rejected'
            daily_record.activity_schedule('faculty.mail_activity_for_coordinator_rejected_record',
                                           user_id=daily_record.create_uid.id,
                                           note=f'This record is rejected due to: {self.reason}')

        return
