from odoo import fields, models, _, api
from datetime import datetime
from odoo.exceptions import UserError


class DailyClassRecord(models.Model):
    _name = 'daily.class.record'
    _inherit = 'mail.thread'
    _rec_name = 'faculty_id'

    faculty_id = fields.Many2one('faculty.details', 'Name', index=True, required=True)
    class_room = fields.Many2one('class.room', string='Class', required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('fac_approve', 'Faculty Approve'),
        ('approve', 'Approved'),
        ('rejected', 'Rejected')

    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    branch_name = fields.Many2one('logic.branches', string='Branch')
    month_of_record = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of record', copy=False,
        tracking=True)

    course_id = fields.Many2one('courses.details', string='Course', required=True)
    subject_id = fields.Many2one('subject.details', string='Subject', required=True)
    extra_hour_active = fields.Boolean('Add extra hour', required=True)
    extra_hour_reason = fields.Text('Extra hour reason')
    record_ids = fields.One2many('record.data', 'record_id', string='Records')

    subject_rate = fields.Float(string='Subject rate', compute='onchange_standard_hour', store=True)
    extra_hour = fields.Integer(string='Extra hour eligible for payment', required=True)

    @api.depends('subject_id')
    def _compute_standard_hour_taken(self):
        standard = self.env['subject.details'].search([])
        for j in standard:
            print(self.subject_id.name,'kl')
            print(j.name, 'kl')
            if self.subject_id.name == j.name and self.course_id == j.course_sub_id:
                print(j.stnd_hr, 'yes')
                self.standard_hour = j.stnd_hr
                break
            else:
                self.standard_hour = 0
                print('no')

    standard_hour = fields.Float(string='Standard hour', compute='_compute_standard_hour_taken', store=True)

    @api.depends('subject_id')
    def onchange_standard_hour(self):
        print(self.subject_id, 'facul')
        rate = self.env['faculty.subject.rate'].search([])
        for j in rate:
            print(j.subject_id, 'co')
            if self.faculty_id == j.name and self.course_id == j.course_id and self.subject_id == j.subject_id:

                self.subject_rate = j.salary_per_hr
                print(self.subject_rate,'rate')
            else:
                print('no')

    @api.depends('record_ids.net_hour')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.record_ids:
            total += order.net_hour
        self.update({
            'total_duration_sum': total,
        })

    total_duration_sum = fields.Float(string='Total duration', compute='_amount_all', store=True)

    @api.depends('standard_hour', 'total_duration_sum')
    def remaining_hour(self):
        total = 0
        net_hour = self.env['daily.class.record'].search([])

        for jj in net_hour:
            if self.faculty_id == jj.faculty_id and self.class_room == jj.class_room and self.course_id == jj.course_id and self.subject_id == jj.subject_id:
                total += jj.total_duration_sum
            aa = self.standard_hour - total
            for i in jj.record_ids:
                self.total_remaining_hour = aa
        print(total, 'kklk')
                # self.total_remaining_hour = self.total_duration_sum - total

    total_remaining_hour = fields.Float(string='Balance standard hours', compute='remaining_hour', store=True)

    @api.depends('record_ids.net_hour', 'subject_rate')
    def _compute_subtotal_amount(self):
        for record in self.record_ids:
            cc = record.net_hour * self.subject_rate

    @api.depends('total_amount')
    def _compute_tds(self):
        for rec in self:
            tds = (10 / 100) * rec.amount_to_be_paid
            self.tds = tds

    @api.depends('record_ids.balance')
    def _amount_total(self):
        for record in self:
            if record.total_remaining_hour >= 0:

                total = 0
                for order in record.record_ids:
                    total += order.balance
                record.update({
                    'total_amount': total,
                })
            else:
                record.total_amount = record.standard_hour * record.subject_rate
    total_amount = fields.Float('Total', compute='_amount_total', store=True)
    check_coordinator_id = fields.Integer()
    actual_dur = fields.Float()
    extra_hour_testing = fields.Float()
    total_extra_hour = fields.Float()

    @api.depends('subject_id', 'course_id')
    def _total_taken_classes(self):
        total = 0
        duration = self.env['daily.class.record'].search([])
        for i in duration:
            if self.faculty_id == i.faculty_id and self.class_room == i.class_room and self.subject_id == i.subject_id and self.course_id == i.course_id:
                total += i.total_duration_sum
                self.class_hour_till_now = total
            else:

                self.class_hour_till_now = 0
    class_hour_till_now = fields.Float('Class hours till now', compute='_total_taken_classes', store=True)

    def confirm_record(self):
        total = 0
        var = []
        net_hour = self.env['daily.class.record'].search([])
        for j in net_hour:
            if j.faculty_id == self.faculty_id and self.subject_id == j.subject_id and self.course_id == j.course_id:
                total += j.total_duration_sum
        var.append(total)
        aa = self.standard_hour - total
        self.actual_dur = aa
        if self.actual_dur <0:
            self.extra_hour_testing = abs(self.actual_dur)
            aaaa = self.total_duration_sum - self.extra_hour_testing
            if aaaa == 0:
                if self.total_remaining_hour <0:
                    self.total_extra_hour = self.total_remaining_hour
            else:
                self.total_extra_hour = aaaa

            print(self.extra_hour_testing, 'total extra')
            print(self.total_duration_sum, 'total dur')
            print(aaaa,'tes')
        else:
            print('cherdh')
        for record in self:
            # print(self.record_ids.balance)
            record.state = 'to_approve'
        self.check_coordinator_id = self.env.user.employee_parent_id.user_id
        # print(self.check_coordinator_id, 'cooo')

    def head_approve(self):
        print(self.check_coordinator_id, 'employee')
        print(self.env.user.id,'user')
        if not self.check_coordinator_id == self.env.user.id:
            raise UserError('Coordinator manager approve button')
        #
        else:
            self.state = 'fac_approve'

    def faculty_approve(self):
        abc = []
        for rec in self.record_ids:
            res_list = {
                'date': rec.date,
                # 'classroom_id': self.class_room.name,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'balance': rec.balance,
                'net_hour': rec.net_hour,
            }
            abc.append((0, 0, res_list))
        record = self.env['payment.total'].create({
            'faculty_id': self.faculty_id.id,
            'month': self.month_of_record,
            'extra_reason': self.extra_hour_reason,
            'extra_charge': self.extra_hour,
            'payment_ids': abc,
            # 'amount_to_be_paid': self.total_amount,
            'class_room': self.class_room.id,
            'course_id': self.course_id.id,
            'subject_id': self.subject_id.id,
            'current_status': self.faculty_id.current_status,
            'branch': self.branch_name.id,
            # 'charge': self.subject_rate,
            'ifsc': self.faculty_id.ifsc,
            'bank': self.faculty_id.bank_name,
            'account_number': self.faculty_id.bank_account_no,
            'account_holder': self.faculty_id.account_holder,
            'remaining_hours': self.total_remaining_hour,
            'standard_hours': self.standard_hour,
            'extra_hr_testing': self.total_extra_hour,
            'extra_hour_reason': self.extra_hour_reason,
            'correct_remaining_hours': self.total_remaining_hour,
            'class_hours_till': self.class_hour_till_now,
        }
        )

        self.state = 'approve'

    def rejected(self):
        self.state = 'rejected'

    make_visible = fields.Boolean(string="User", default=True, compute='get_user')

    @api.depends('make_visible')
    def get_user(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('faculty.group_faculty_user'):
            self.make_visible = False

        else:
            self.make_visible = True

    make_visible_coord = fields.Boolean(string="User", default=True, compute='get_coord')

    @api.depends('make_visible_coord')
    def get_coord(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('faculty.coordinator_user'):
            self.make_visible_coord = False

        else:
            self.make_visible_coord = True


class RecordData(models.Model):
    _name = 'record.data'

    start_date = fields.Datetime(string='Start time', widget='time', required=True)
    end_date = fields.Datetime(string='End time', widget='time', required=True)

    record_id = fields.Many2one('daily.class.record')
    break_reason = fields.Char(string='Break reason')
    break_time = fields.Integer(string='Break time')
    topic = fields.Char(string='Topic')
    date = fields.Date(string='Date', default=fields.Date.today)
    remaining_hours = fields.Float('Remaining hours')

    @api.depends('start_date', 'end_date')
    def _compute_net_time(self):
        for record in self:
            if record.start_date and record.end_date:
                datetime_diff = datetime.strptime(str(record.end_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                    str(record.start_date), '%Y-%m-%d %H:%M:%S')
                seconds_diff = datetime_diff.total_seconds()
                record.net_duration = seconds_diff / 3600.0
            else:
                record.net_duration = 0.0

    net_duration = fields.Float(string='Net', compute='_compute_net_time', readonly=True, store=True)

    @api.depends('break_time', 'net_duration')
    def _compute_net_total_duration(self):
        for record in self:
            record.net_hour = record.net_duration - record.break_time

    net_hour = fields.Integer(string='Net hours', compute='_compute_net_total_duration', store=True)

    @api.depends('net_hour', 'record_id.subject_rate')
    def _compute_balance(self):
        for record in self:
            record.balance = record.net_hour * record.record_id.subject_rate

    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)

    # @api.depends('net_hour')
    # def _compute_total_remaining_hour(self):
    #     for rec in self:
    #
    #         rec.remaining_hours = rec.record_id.total_remaining_hour
