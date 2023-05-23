from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import datetime
import json


class MainFormDepartment(models.Model):
    _name = 'form.department'
    _inherit = 'mail.thread'

    name = fields.Char(string='ENTREES', readonly=True)
    class_details_ids = fields.One2many('daily.class', 'samp_many_one_id')
    test_bool = fields.Boolean()
    current_user = fields.Many2one('res.users', 'Coordinator', default=lambda self: self.env.user)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approve'),
        ('approve', 'Approved'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    manager_approve = fields.Many2one('hr.employee')

    def approve_button(self):
        print("hi")
        self.state = 'approve'
        self.test_bool = True

    def add_entry(self):
        # print("hi", self.current_user.name)

        bal = self.env['hr.employee'].search(
            [('name', '=', self.current_user.name)])
        # print(bal.parent_id.name, 'employees')
        self.state = 'confirm'
        self.manager_approve = bal.parent_id
        print("manager", self.manager_approve.name)

    def check_approval(self):
        if self.manager_approve == self.env.user.name:
            self.test_bool = True
            print("currect")
            # records = self.search([('state', '=', 'done')])
        else:
            self.test_bool = False
            print("no")

            self.state = 'done'
            print("ok")
        # def write(self, vals):

    #     if any(state != 'done' for state in set(self.mapped('done'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super().write(vals)


class DailyClass(models.Model):
    _name = 'daily.class'
    _inherit = 'mail.thread'
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=True,
                                 domain=[('current_status', '=', 'active')])
    manager_approve = fields.Char(string='Manager', compute='approve_employee_manager', store=True)

    current_user = fields.Many2one('res.users', 'Coordinator', default=lambda self: self.env.user)
    coordinator_manager = fields.Char()
    subject_daily_id = fields.Many2one('subject.details', string='Subject',
                                       domain="[('course_sub_id', '=', course_id)]", required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('fac_approve', 'Faculty Approve'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),

    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    approve_status = fields.Selection(selection=[
        ('approved_status', 'Approved'),
    ], string='Faculty status', readonly=True, copy=False,
        tracking=True)
    class_room = fields.Many2one('class.room', string='Class room', required=True)
    normal_class_time = fields.Float('Checking time')
    course_id = fields.Many2one('courses.details', string='Course', required=True)
    topic = fields.Char(string='Topic')

    strt_time = fields.Datetime(string='Start time', required=True)
    end_time = fields.Datetime(string='End time', required=True)
    samp_many_one_id = fields.Many2one('form.department')
    test_bool = fields.Boolean()
    total_remain_test = fields.Float('Total working hr')
    reason_ids = fields.One2many('break.reason', 'reason_id')
    total_amount = fields.Float(string='Total break time', compute='_compute_total_amount', store=True)
    group_check = fields.Boolean(compute='compute_your_method')
    extra_class_bool = fields.Boolean('Extra class')
    extra_hour = fields.Float('Extra Hours')
    payment_status = fields.Selection(selection=[
        ('paid', 'Paid'),
        ('not_paid', 'Not Paid'),

    ], string='Payment Status', required=True, readonly=True, copy=False,
        tracking=True, default='not_paid')
    total_rate = fields.Float(string='Payable Amount', compute='_compute_duration_total_time', store=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]).id,
                                  readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, currency_field='currency_id',
                                 compute='_compute_tax_amount')
    tds_id = fields.Many2one('account.tax', store=True, readonly=True, currency_field='currency_id',
                             default=lambda self: self.env['account.tax'].search([('name', '=', 'Tds')]))
    tds_amount = fields.Float(string='TDS', computea='_compute_payable_amount_total')
    extra_hour_reason = fields.Text(string='Extra hour reason')
    extra_amount = fields.Float('Extra amount', compute='_compute_extra_amount', store=True)
    extra_hour_total = fields.Float('Extra total hour', compute='_compute_total_extra_hour', store=True)
    testing_extra_hour = fields.Float()

    @api.depends('total_rate', 'tax_ids.amount')
    def _compute_tax_amount(self):
        for rec in self:
            if rec.tax_ids:
                for tax in rec.tax_ids:
                    rec.amount_tax = (rec.total_rate * tax.amount) / 100

            else:
                rec.amount_tax = 0

    @api.depends('total_rate', 'tds_id.amount')
    def _compute_tds_amount(self):
        for rec in self:
            if rec.tds_id:
                for tds in rec.tds_id:
                    rec.tds_amount += (rec.total_rate * tds.amount) / 100

            else:
                rec.tds_amount = 0

    @api.depends('reason_ids.duration')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.reason_ids.mapped('duration'))

    @api.depends('extra_hour_total', 'extra_hour')
    def _compute_total_extra_hour(self):
        hours = self.env['daily.class'].search([])
        total_hour_extra = 0
        for record in hours:
            print(record.extra_hour, '+ve')
            total_hour_extra -= record.extra_hour
        print(total_hour_extra, '-ve hour')

    def approve_user_button(self):

        record = self.env['accountant.payout'].create({
            'name': self.faculty_id.name.name,
            'course': self.course_id.name,
            'create_date': self.create_date,
            'duration': self.actual_amount,
            'per_hr_rate': self.total_rate,
            'total': self.total_payable_amount,
            'tds': self.tds_amount,
            'extra_charge': self.extra_hour

        }
        )
        faculty_check = self.env['faculty.details'].search([])
        order_line_list = []
        for i in faculty_check:
            # print(i.name.name, 'messi')
            # print(self.faculty_id.name.name, 'ronaldo')
            check_name = i.name.name == self.faculty_id.name.name
            if check_name:
                print(self.faculty_id.name.name, 'rooney')
                res_list = {
                    'subject_id': self.subject_daily_id.name,
                    # 'classroom_id': self.class_room.name,
                    'courses_id': self.course_id.name,
                    'topic': self.topic,
                    'start_time': self.strt_time,
                    'end_time': self.end_time
                }
                order_line_list.append((0, 0, res_list))
                i.payout_ids = order_line_list
        self.state = 'approve'

        # aa = self.env['total.payment'].search([])
        # aa.extra_charge = self.extra_hour

    def approve_button(self):
        user_id = self.env.user.name
        print('Current user ID:', user_id)

        print("hi", self.manager_approve)
        self.state = 'approve'
        self.test_bool = True
        my_records = self.env['daily.class'].search([('manager_approve', '=', self.env.user.name)])
        my_data = my_records.read(['faculty_id', 'topic'])

        if self.manager_approve == self.env.user.name:
            print("currect")

            # records = self.search([('state', '=', 'done')])
        else:
            print("no")


    @api.depends('strt_time', 'end_time')
    def _compute_duration_time(self):
        for record in self:
            if record.strt_time and record.end_time:
                datetime_diff = datetime.strptime(str(record.end_time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                    str(record.strt_time), '%Y-%m-%d %H:%M:%S')
                seconds_diff = datetime_diff.total_seconds()
                record.duration_time = seconds_diff / 3600.0
            else:
                record.duration_time = 0.0


    duration_time = fields.Float(string='Duration', compute='_compute_duration_time', readonly=True, store=True)


    @api.depends('total_amount', 'duration_time')
    def _compute_actual_duration_total(self):
        for record in self:
            record.actual_amount = record.duration_time - record.total_amount

    actual_amount = fields.Float(string='Actual class duration', compute='_compute_actual_duration_total', store=True)

    @api.depends('subject_daily_id.stnd_hr', 'total_remain_test')
    def _compute_class_total_duration(self):
        for record in self:
            if record.subject_daily_id.stnd_hr - record.total_remain_test <= 0:
                # record.total_class_remaining = 0
                print('hoooi')
            record.total_class_remaining = record.subject_daily_id.stnd_hr - record.total_remain_test
            # else:
            #     record.total_class_remaining = record.subject_daily_id.stnd_hr - record.total_remain_test
            #     print('kkko')

    total_class_remaining = fields.Float(string='Total remaining class', compute='_compute_class_total_duration',
                                         store=True)


    @api.depends('subject_daily_id.stnd_hr', 'actual_amount')
    def _compute_remaining_total(self):
        asd = self.env['daily.class'].search([])
        # if asd.faculty_id == self.faculty_id:
        #
        #     print(asd, 'filter record')
        total = 0
        for sample in asd:
            new = []
            aaa = sample.faculty_id == self.faculty_id
            if aaa and sample.subject_daily_id == self.subject_daily_id and sample.class_room == self.class_room:
                total += sample.actual_amount
            else:
                print("no")
        print("currect", total)
        self.total_remain_test = total
        # ssss = sum(sample.actual_amount)
        # float_sum = sum(sample.mapped('actual_amount'))
        # new.append(sum[sample.actual_amount])

        # total = sum(new)

        # print(total)
        for record in self:
            record.total_remaining = record.subject_daily_id.stnd_hr - record.actual_amount


    total_remaining = fields.Float(string='Total Remaining Time', compute='_compute_remaining_total', store=True)


    # @api.onchange('strt_time')
    # def _onchangestrttime(self):
    #     rate = self.env['faculty.subject.rate'].search([])
    #     for rec in rate:
    #         print('faculty record', rec)
    #         if rec.name == self.faculty_id:
    #             if rec.subject_id == self.subject_daily_id:
    #                 aa = rec.salary_per_hr * self.actual_amount
    #                 self.total_rate = aa
    #                 print("same", aa)
    #         else:
    #             print("no match")

    @api.depends('total_class_remaining')
    def _compute_extra_hours(self):
        if self.total_class_remaining <= 0:
            print('yes')
            sssdd = self.total_class_remaining
            self.extra_hour = abs(sssdd)

        else:
            print('no')
            self.extra_hour = 0


    @api.depends('extra_hour', 'extra_amount')
    def _compute_extra_amount(self):
        sss = self.env['faculty.subject.rate'].search([])
        for i in sss:
            if i.name == self.faculty_id and i.subject_id == self.subject_daily_id:
                if self.total_class_remaining <= 0:
                    positive = self.extra_hour * i.salary_per_hr
                    self.extra_amount = abs(positive)
                    # print(abs(self.extra_amount))
                else:
                    self.extra_amount = 0

    def add_entry(self):
       self.normal_class_time = self.duration_time
       self.state = 'to_approve'
       ab = self.env['daily.class'].search([])

       num = 0
       for rec in ab:
           num += rec.normal_class_time
           if rec.total_class_remaining < 0:
               self.duration_time - rec.total_class_remaining
       print(num)


       # for rec in self:
        #     if rec.total_class_remaining < 0:
        #         var = self.total_class_remaining
        #         # var.append(rec.total_class_remaining)
        #         time = self.duration_time
        #         self.total_class_remaining = 0
        # # aa = abs(var)
        # # bb = abs(time)
        # # total = bb - aa
        # print(var, 'meeeeeeeeeeee')
        # print(self.total_class_remaining)
        # print(time, 'totaal')
        # # print("hi", self.current_user.name)
        # bal = self.env['hr.employee'].search([('name', '=', self.current_user.name)])



    @api.depends('duration_time', 'actual_amount')
    def _compute_duration_total_time(self):
        rate = self.env['faculty.subject.rate'].search([])
        tax = self.env['faculty.details'].search([])
        for rec in rate:
            print('faculty record', rec)
            if rec.name == self.faculty_id:
                if rec.subject_id == self.subject_daily_id:
                    aa = rec.salary_per_hr * self.actual_amount
                    self.total_rate = aa
                    print("same", aa)
            else:
                print("no match")


    @api.depends('strt_time')
    def approve_employee_manager(self):
        print(self.env.user.employee_parent_id.name, 'he he heee')
        self.manager_approve = self.env.user.employee_parent_id.name

        # msg = _(
        #     "The entry added by %(carrier_name)s date by %(ref)",
        #     carrier_name=self.faculty_id.name,
        #     ref=self.create_date,
        # )
        # self.message_post(body=_('The entry added'))

    def check_approval(self):
        if not self.manager_approve == self.env.user.name:
            raise UserError('Coordinator manager approve button')
        else:

            if self.total_class_remaining < 0:
                raise UserError('This faculty class is over please adjust class duration')
            else:
                self.state = 'fac_approve'

    @api.depends('total_rate', 'amount_tax', 'extra_amount')
    def _compute_payable_amount_total(self):
        sum = 0
        ss = self.env['subject.details'].search([])
        dd = self.env['daily.class'].search([])
        # for jh in ss:
        #     if self.subject_daily_id.name == jh.name:
        #         print(jh.stnd_hr, 'hjjkk')
        #         for k in dd:
        #             sum += k.duration_time
        #             for gh in range(100):
        #                 if gh == jh.stnd_hr:
        #                     break
        print(sum,'hooi')
        for record in self:

            tds = (10 / 100) * record.total_rate
            record.total_payable_amount = (record.total_rate - tds) + record.amount_tax
            record.tds_amount = tds

    total_payable_amount = fields.Float(string='Total', compute='_compute_payable_amount_total', store=True)

class Approvals(models.Model):
    _name = 'approvals'
    _inherit = 'mail.thread'

    faculty_appr_id = fields.Many2one('faculty.details', string='Faculty', required=True)
    manager_appr_approve = fields.Char()
    current_appr_user = fields.Many2one('res.users', 'Coordinator', default=lambda self: self.env.user)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('done', 'Approve'),
        ('approve', 'Approved'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    class_room_appr = fields.Many2one('res.class', string='Class room')
    topic_appr = fields.Char(string='Topic')
    strt_time_appr = fields.Datetime(string='Start time')
    end_time_appr = fields.Datetime(string='End time')
    samp_many_appr_one_id = fields.Many2one('form.department')
    test_bool_appr = fields.Boolean()

    # def datas_approvals(self):
    #     self.env['daily.class'].search([])
    #     # print(aa)
    #     for rec in self:
    #         records = self.env['approvals'].create({
    #             'faculty_appr_id': self.partner_id.name,
    #             'machine_order': rec.machine_id.name,
    #             'material_order': rec.materials,
    #             'delivery_date': rec.delivery,
    #             'sale_order': self.name
    #         })

    # manager_coord_appr = fields.Many2one('hr.employee', default=lambda self: self.env.user)

    # def check_approvals(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'form.department',
    #         'view_type': 'tree',
    #         'view_mode': 'tree',
    #     }
    #     print("dd")


class BreakReasons(models.Model):
    _name = 'break.reason'

    reason = fields.Char(string='Reason')
    reason_id = fields.Many2one('daily.class')

    from_date = fields.Datetime(string='From')
    to_date = fields.Datetime(string='To')

    # date_start_str = from_date.strftime('%Y-%m-%d %H:%M:%S')
    # date_end_str = to_date.strftime('%Y-%m-%d %H:%M:%S')

    @api.depends('from_date', 'to_date')
    def _compute_duration(self):
        for record in self:
            if record.from_date and record.to_date:
                datetime_diff = datetime.strptime(str(record.to_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                    str(record.from_date), '%Y-%m-%d %H:%M:%S')
                seconds_diff = datetime_diff.total_seconds()
                record.duration = seconds_diff / 3600.0
            else:
                record.duration = 0.0

    duration = fields.Float(string='Duration', compute='_compute_duration', store=True)
