from odoo import fields, models, _, api
from datetime import datetime
from odoo.exceptions import UserError


class DailyClassRecord(models.Model):
    _name = 'daily.class.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'faculty_id'
    _description = 'Class Record'

    faculty_id = fields.Many2one('faculty.details', 'Faculty', index=True, required=True, ondelete='restrict')
    class_room = fields.Many2one('class.room', string='Class', required=True, ondelete='restrict')
    coordinator = fields.Many2one('res.users', 'user', default=lambda self: self.env.user.id, ondelete='restrict')

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('sent_approve', 'Sent to Approve'),
        ('to_approve', 'To Approve'),
        # ('fac_approve', 'Faculty Approve'),
        ('approve', 'Approved'),
        ('register_payment', 'Register Payment'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),

    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    branch_name = fields.Many2one('logic.branches', string='Branch', required=True, ondelete='restrict')
    month_of_record = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of Record', copy=False,
        required=True)

    course_id = fields.Many2one('courses.details', string='Course', required=True, ondelete='restrict')
    subject_id = fields.Many2one('subject.details', string='Subject', required=True, ondelete='restrict',
                                 domain="[('course_sub_id', '=', course_id)]")
    extra_hour_active = fields.Boolean('Add extra hour', required=True)
    extra_hour_reason = fields.Text('Extra hour reason')

    record_ids = fields.One2many('record.data', 'record_id', string='Records')
    skip_ids = fields.One2many('skipped.classes', 'skip_id', string='Skipped classes')
    subject_rate = fields.Float(string='Subject rate', compute='onchange_standard_hour', store=True)
    extra_hour = fields.Float(string='Extra hour eligible for payment', required=True)
    create_date = fields.Datetime(default=datetime.now(), tracking=True)
    is_this_record_locked = fields.Boolean('Is this record locked?')
    groups_id = fields.Many2one('res.groups', string='Groups',
                                default=lambda self: self.env.ref('faculty.group_faculty_administrator').id)
    record_year = fields.Char(string='Year', compute='year_only', store=True)

    @api.depends('create_date')
    def year_only(self):
        for i in self:
            if i.create_date:
                i.record_year = i.create_date.year

    def action_bulk_record_add_year(self):
        rec = self.env['daily.class.record'].sudo().search([])
        for i in rec:
            if i.create_date:
                i.record_year = i.create_date.year

    is_this_current_month_record = fields.Boolean('Is this current month record')

    @api.onchange('month_of_record')
    def _onchange_lock_record(self):
        current_date = fields.Date.context_today(self)
        print(current_date.month, 'month')
        if self.month_of_record:
            if self.month_of_record == 'january':
                if current_date.month == 1:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'february':
                if current_date.month == 2:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'march':
                if current_date.month == 3:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'april':
                if current_date.month == 4:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False

            if self.month_of_record == 'may':
                if current_date.month == 5:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'june':
                if current_date.month == 6:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'july':
                if current_date.month == 7:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'august':
                if current_date.month == 8:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'september':
                if current_date.month == 9:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'october':
                if current_date.month == 10:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'november':
                if current_date.month == 11:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
            if self.month_of_record == 'december':
                if current_date.month == 12:
                    self.is_this_current_month_record = True
                else:
                    self.is_this_current_month_record = False
                print()
        current_date = fields.Date.context_today(self)
        print(current_date.month, 'month')
        lock_day = self.env['faculty.daily.record.lock.date'].sudo().search([], limit=1)
        current_day = current_date.day
        print(current_day, 'current day')
        print(lock_day.lock_day, 'lock day')
        if self.month_of_record:
            if self.is_this_current_month_record == False:
                self.is_this_record_locked = True
            else:

                if current_day > lock_day.lock_day:
                    self.is_this_record_locked = True
                else:
                    self.is_this_record_locked = False
        else:
            self.is_this_record_locked = False

    def action_cron_locking_record(self):
        print('action')
        current_date = fields.Date.context_today(self)
        # print(current_date.month, 'month')
        #
        # print(current_date.month, 'month')
        lock_day = self.env['faculty.daily.record.lock.date'].sudo().search([], limit=1)
        current_day = current_date.day
        # print(current_day, 'current day')
        # print(lock_day.lock_day, 'lock day')
        rec = self.env['daily.class.record'].sudo().search([])
        for record in rec:
            # print(record.month_of_record, 'rec month')
            if record.month_of_record:
                if record.month_of_record == 'january':
                    if current_date.month == 1:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'february':
                    if current_date.month == 2:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'march':
                    if current_date.month == 3:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'april':
                    if current_date.month == 4:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False

                if record.month_of_record == 'may':
                    if current_date.month == 5:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'june':
                    if current_date.month == 6:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'july':
                    if current_date.month == 7:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'august':
                    if current_date.month == 8:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'september':
                    if current_date.month == 9:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'october':
                    if current_date.month == 10:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'november':
                    if current_date.month == 11:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                if record.month_of_record == 'december':
                    if current_date.month == 12:
                        record.is_this_current_month_record = True
                    else:
                        record.is_this_current_month_record = False
                    print()

            if record.is_this_current_month_record == False:
                if current_day > lock_day.lock_day:
                    record.is_this_record_locked = True
                else:
                    record.is_this_record_locked = False
            else:
                record.is_this_record_locked = False

    def action_unlock_daily_record(self):
        self.is_this_record_locked = False

    def action_all_record_unlocking(self):
        rec = self.env['daily.class.record'].sudo().search([])
        for record in rec:
            record.is_this_record_locked = False

    coordinator_head = fields.Many2one('res.users', domain="[('groups_id', 'in', [groups_id])]",
                                       default=lambda self: self.env.user.employee_id.branch_id.branch_head.id,
                                       ondelete='restrict', required=True)
    branch_id = fields.Many2one('logic.base.branches', string='Branch', required=1)

    def server_action_for_change_branch_student_to_base(self):
        rec = self.env['daily.class.record'].sudo().search([])
        for recs in rec:
            if recs.branch_name:
                if recs.branch_name == 'Kottayam Campus':
                    recs.branch_id = 3
                if recs.branch_name == 'Corporate Office & City Campus':
                    recs.branch_id = 1
                if recs.branch_name == 'Cochin Campus':
                    recs.branch_id = 2
                if recs.branch_name == 'Trivandrum Campus':
                    recs.branch_id = 6
                if recs.branch_name == 'Calicut Campus':
                    recs.branch_id = 4
                if recs.branch_name == 'Malappuram Campus':
                    recs.branch_id = 9
                if recs.branch_name == 'Palakkad Campus':
                    recs.branch_id = 7

                if recs.branch_name == 'Online Campus':
                    recs.branch_id = 10
                if recs.branch_name == 'Bengaluru':
                    recs.branch_id = 16

    def add_empty_coordinator_head_fields(self):
        records = self.env['daily.class.record'].sudo().search([])
        for record in records:
            if not record.coordinator_head:
                print(record.coordinator_head, 'empty')
                print(record.create_uid.employee_id.parent_id.user_id.name, 'coord')
                record.coordinator_head = record.create_uid.employee_id.parent_id.user_id.id

    @api.onchange('course_id')
    def _compute_subject_based_on_course(self):
        for record in self:
            record.subject_id = False

    @api.depends('subject_id', 'faculty_id', 'record_ids.date', 'course_id')
    def compute_standard_hour_taken(self):
        standard = self.env['subject.details'].search([])
        change = self.env['changed.standard.hours'].search([])
        if self.is_it_changed == True:
            print('changed')
            for hour in change:
                if self.faculty_id == hour.faculty_id and self.subject_id == hour.subject_id and self.course_id == hour.course_id:
                    print('same_sub')
                    self.standard_hour = hour.standard_hour

                else:
                    for j in standard:
                        print(self.subject_id.name, 'kl')
                        if self.subject_id.name == j.name and self.course_id == j.course_sub_id:
                            print(j.stnd_hr, 'yes')
                            self.standard_hour = j.stnd_hr
                        # else:
                        #     self.standard_hour = 0
                        #     print('no')
            if self.standard_hour == 0:
                print('this is zero')
                for ref in standard:
                    # print(self.subject_id.name, 'subject')
                    # print(j.name, 'hour sub')
                    if self.subject_id.name == ref.name and self.course_id == ref.course_sub_id:
                        # print(j.stnd_hr, 'hour')
                        self.standard_hour = ref.stnd_hr
            else:
                print('this is not zero')
        else:
            print('no same')
            for j in standard:
                print(self.subject_id.name, 'subject')
                print(j.name, 'hour sub')
                if self.subject_id.name == j.name and self.course_id == j.course_sub_id:
                    print(j.stnd_hr, 'hour')
                    self.standard_hour = j.stnd_hr

                # else:
                #     self.standard_hour = 0
                #     print('no')

    standard_hour = fields.Float(string='Standard Hour', compute='compute_standard_hour_taken', store=True)

    def sent_to_approval(self):
        # duration = self.env['daily.class.record'].sudo().search([])
        # total = 0
        # for i in duration:
        #     if self.faculty_id == i.faculty_id and self.branch_name == i.branch_name and self.class_room == i.class_room and self.subject_id == i.subject_id and self.course_id == i.course_id:
        #         if i.state in 'to_approve' or i.state in 'approve' or i.state in 'sent_approve' or i.state in 'paid' or i.state in 'register_payment':
        #             total += i.total_duration_sum
        self.class_hour_till_now = self.class_till_view
            # else:
            #     self.class_hour_till_now = 0
        self.state = 'to_approve'
        # net_hour = self.env['daily.class.record'].sudo().search([])
        # total_rem = 0
        # for jj in net_hour:
        #     if self.faculty_id == jj.faculty_id and self.branch_name == jj.branch_name and self.class_room == jj.class_room and self.course_id == jj.course_id and self.subject_id == jj.subject_id:
        #         if jj.state in 'to_approve' or jj.state in 'approve' or jj.state in 'sent_approve' or jj.state in 'paid' or jj.state in 'register_payment':
        #             total_rem += jj.total_duration_sum
        #     aa = self.standard_hour - total_rem

        self.total_remaining_hour = self.remaining_hour_view

        # fac = self.env['faculty.details'].search([])
        # for faculty in fac:
        #     if self.faculty_id.id == faculty.id:
        #         faculty.sudo().write({'is_it_changed_faculty': False})

        # self.total_remaining_hour = self.total_duration_sum - total

    total_remaining_hour = fields.Float(string='Balance Standard Hours', readonly=True)
    class_hour_till_now = fields.Float('Class hours till now', readonly=True)
    activity_done_coordinator = fields.Boolean('Activity done')

    def action_activity_cancel(self):

        faculty_activity = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('faculty.mail_activity_for_coordinator_rejected_record').id)])
        faculty_activity.unlink()
        self.activity_done_coordinator = True
        # if activity_faculty:
        #     activity_faculty.unlink()

    @api.depends('subject_id')
    def onchange_standard_hour(self):
        print(self.subject_id, 'facul')
        rate = self.env['faculty.subject.rate'].sudo().search([])

        for j in rate:
            print(j.subject_id, 'co')
            if self.faculty_id == j.name and self.course_id == j.course_id and self.subject_id == j.subject_id:

                self.subject_rate = j.salary_per_hr
                print(self.subject_rate, 'rate')
            else:
                print('no')

    @api.depends('record_ids.net_hour')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.record_ids:
            if order.upaya_class == False:
                total += order.net_hour
        self.update({
            'total_duration_sum': total,
        })

    total_duration_sum = fields.Float(string='Total duration', compute='_amount_all', store=True)

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

    # @api.depends('subject_id', 'course_id', 'record_ids.net_hour')
    # def _total_taken_classes(self):
    # total = 0
    # duration = self.env['daily.class.record'].search([])
    # for i in duration:
    #     if self.branch_name == i.branch_name and self.class_room == i.class_room and self.subject_id == i.subject_id and self.course_id == i.course_id:
    #         if i.state in 'to_approve' or i.state in 'approve' or i.state in 'sent_approve' or i.state in 'paid':
    #             total += i.total_duration_sum
    #             self.class_hour_till_now = total
    #     else:
    #         self.class_hour_till_now = 0

    over_time_check = fields.Boolean()
    over_time = fields.Float()

    def confirm_record(self):
        ss = self.env['daily.class.record'].sudo().search([])
        net_hour = self.env['daily.class.record'].sudo().search([])
        total_rem = 0
        std_hr = []
        for jj in net_hour:
            if self.faculty_id == jj.faculty_id and self.branch_name == jj.branch_name and self.class_room == jj.class_room and self.course_id == jj.course_id and self.subject_id == jj.subject_id:
                if jj.state != 'rejected':
                    total_rem += jj.total_duration_sum
            aa = self.standard_hour - total_rem
        std_hr.append(aa)
        self.over_time = aa
        print(self.standard_hour, 'total hr ddddddddddddd')
        print(std_hr, 'class hour till sssssss')
        print(total_rem, 'class hour till remmmm')
        for hh in ss:
            print(hh.id, 'rec id')
        if self.over_time < 0:
            self.over_time_check = True
        else:
            self.over_time_check = False
        # total = 0
        # var = []
        # net_hour = self.env['daily.class.record'].search([])
        # for j in net_hour:
        #     if self.class_room == j.class_room and self.subject_id == j.subject_id and self.course_id == j.course_id:
        #         if j.state != 'rejected':
        #             total += j.total_duration_sum
        # var.append(total)
        # aa = self.standard_hour - total
        # self.actual_dur = aa
        # if self.actual_dur < 0:
        #     self.extra_hour_testing = abs(self.actual_dur)
        #     aaaa = self.total_duration_sum - self.extra_hour_testing
        #     if aaaa == 0:
        #         if self.total_remaining_hour < 0:
        #             self.total_extra_hour = self.total_remaining_hour
        #     else:
        #         self.total_extra_hour = aaaa
        #
        #     print(self.extra_hour_testing, 'total extra')
        #     print(self.total_duration_sum, 'total dur')
        #     print(aaaa, 'tes')
        # else:
        #     print('cherdh')
        for record in self:
            # print(self.record_ids.balance)
            record.state = 'sent_approve'
        # self.check_coordinator_id = self.env.user.employee_parent_id.user_id
        # print(self.check_coordinator_id, 'cooo')

    def refresh_record(self):
        ff = self.env['daily.class.record'].sudo().search([])
        print('refresh')
        total = 0

        for ii in ff:
            if self.faculty_id == ii.faculty_id and self.branch_name == ii.branch_name and self.class_room == ii.class_room and self.subject_id == ii.subject_id and self.course_id == ii.course_id:
                if ii.state != 'rejected':
                    total += ii.total_duration_sum
                    self.class_hour_till_now = total
                    self.extra_hour = 0
                    self.total_remaining_hour = self.standard_hour - total
                # else:
                #     self._total_taken_classes()

    def head_approve(self):
        print(self.coordinator.employee_id.parent_id.user_id.id, 'employee')
        print(self.env.user, 'user')
        if self.coordinator.employee_id.parent_id.user_id.id == self.env.user.id or self.env.user.id == self.coordinator_head.id:
            if self.over_time_check == True:
                total = 0
                var = []
                net_hour = self.env['daily.class.record'].sudo().search([])
                for j in net_hour:
                    if self.faculty_id == j.faculty_id and self.branch_name == j.branch_name and self.class_room == j.class_room and self.subject_id == j.subject_id and self.course_id == j.course_id:
                        if j.state in 'to_approve' or j.state in 'approve' or j.state in 'sent_approve' or j.state in 'register_payment' or j.state in 'paid':
                            total += j.total_duration_sum
                var.append(total)
                aa = self.standard_hour - total
                self.actual_dur = aa
                if self.actual_dur < 0:
                    print('hhhhhhhhhhhhhhhh')
                    self.extra_hour_testing = abs(self.actual_dur)
                    aaaa = self.total_duration_sum - self.extra_hour_testing
                    if aaaa == 0:
                        if self.total_remaining_hour < 0:
                            self.total_extra_hour = self.total_remaining_hour
                    else:
                        self.total_extra_hour = aaaa

                self.write({'state': 'approve'})
                # self.state = 'approve'
                abc = []
                for rec in self.record_ids:
                    res_list = {
                        'date': rec.date,
                        # 'classroom_id': self.class_room.name,
                        'start_date': rec.start_date,
                        'end_date': rec.end_date,
                        'balance': rec.balance,
                        'net_hour': rec.net_hour,
                        'topic': rec.topic,
                        'upaya_class': rec.upaya_class
                    }
                    abc.append((0, 0, res_list))
                record = self.env['payment.total'].create({
                    'faculty_id': self.faculty_id.id,
                    'current_id': self.id,
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
            else:
                total = 0
                var = []
                net_hour = self.env['daily.class.record'].sudo().search([])
                for j in net_hour:
                    if self.faculty_id == j.faculty_id and self.class_room == j.class_room and self.subject_id == j.subject_id and self.course_id == j.course_id:
                        if j.state in 'to_approve' or j.state in 'approve' or j.state in 'sent_approve' or j.state in 'paid':
                            total += j.total_duration_sum
                var.append(total)
                aa = self.standard_hour - total
                self.actual_dur = aa
                # if self.actual_dur < 0:
                #     self.extra_hour_testing = abs(self.actual_dur)
                #     aaaa = self.total_duration_sum - self.extra_hour_testing
                #     if aaaa == 0:
                #         if self.total_remaining_hour < 0:
                #             self.total_extra_hour = self.total_remaining_hour
                #     else:
                #         self.total_extra_hour = aaaa
                #
                #     print(self.extra_hour_testing, 'total extra')
                #     print(self.total_duration_sum, 'total dur')
                #     print(aaaa, 'tes')
                # else:
                #     print('cherdh')
                # self.state = 'approve'
                self.write({'state': 'approve'})

                abc = []
                for rec in self.record_ids:
                    res_list = {
                        'date': rec.date,
                        # 'classroom_id': self.class_room.name,
                        'start_date': rec.start_date,
                        'end_date': rec.end_date,
                        'balance': rec.balance,
                        'net_hour': rec.net_hour,
                        'topic': rec.topic,
                        'upaya_class': rec.upaya_class
                    }
                    abc.append((0, 0, res_list))
                record = self.env['payment.total'].create({
                    'faculty_id': self.faculty_id.id,
                    'current_id': self.id,
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

            # self.state = 'approve'
        #
        else:
            raise UserError('Coordinator manager approve button')

    def compute_count(self):
        for record in self:
            record.payment_count = self.env['payment.total'].search_count(
                [('current_id', '=', self.id)])

    payment_count = fields.Integer(compute='compute_count')

    def reset_to_draft(self):
        self.write({'state': 'draft'})

    def get_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'tree,form',
            'res_model': 'payment.total',
            'domain': [('current_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def faculty_approve(self):
        # abc = []
        # for rec in self.record_ids:
        #     res_list = {
        #         'date': rec.date,
        #         # 'classroom_id': self.class_room.name,
        #         'start_date': rec.start_date,
        #         'end_date': rec.end_date,
        #         'balance': rec.balance,
        #         'net_hour': rec.net_hour,
        #     }
        #     abc.append((0, 0, res_list))
        # record = self.env['payment.total'].create({
        #     'faculty_id': self.faculty_id.id,
        #     'month': self.month_of_record,
        #     'extra_reason': self.extra_hour_reason,
        #     'extra_charge': self.extra_hour,
        #     'payment_ids': abc,
        #     # 'amount_to_be_paid': self.total_amount,
        #     'class_room': self.class_room.id,
        #     'course_id': self.course_id.id,
        #     'subject_id': self.subject_id.id,
        #     'current_status': self.faculty_id.current_status,
        #     'branch': self.branch_name.id,
        #     # 'charge': self.subject_rate,
        #     'ifsc': self.faculty_id.ifsc,
        #     'bank': self.faculty_id.bank_name,
        #     'account_number': self.faculty_id.bank_account_no,
        #     'account_holder': self.faculty_id.account_holder,
        #     'remaining_hours': self.total_remaining_hour,
        #     'standard_hours': self.standard_hour,
        #     'extra_hr_testing': self.total_extra_hour,
        #     'extra_hour_reason': self.extra_hour_reason,
        #     'correct_remaining_hours': self.total_remaining_hour,
        #     'class_hours_till': self.class_hour_till_now,
        # }
        # )

        self.state = 'approve'

    def rejected(self):
        self.state = 'rejected'

    @api.depends('make_visible')
    def get_user(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('faculty.group_faculty_user'):
            self.make_visible = False

        else:
            self.make_visible = True

    make_visible = fields.Boolean(string="User", default=True, compute='get_user')

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

    def head_academic(self):
        print('head_check')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('faculty.group_faculty_administrator'):
            self.make_academic_head = False

        else:
            self.make_academic_head = True

    make_academic_head = fields.Boolean(string="Academic Head", default=True, compute='head_academic')
    change_faculty_boolean = fields.Boolean(string='Change Faculty', default=False)
    old_faculty = fields.Many2one('faculty.details', string='Old Faculty')
    new_faculty = fields.Many2one('faculty.details', string='New Faculty')
    old_faculty_class_time = fields.Float(string='Old Faculty Class Time')
    cng_course_id = fields.Many2one('changed.standard.hours', string='Course')
    cng_subject_id = fields.Many2one('changed.standard.hours', string='Subject')

    def change_faculty(self):
        self.old_faculty = self.faculty_id
        net_hour = self.env['daily.class.record'].sudo().search([])
        total_rem = 0
        for jj in net_hour:
            if self.faculty_id == jj.faculty_id and self.branch_name == jj.branch_name and self.class_room == jj.class_room and self.course_id == jj.course_id and self.subject_id == jj.subject_id:
                if jj.state in 'to_approve' or jj.state in 'approve' or jj.state in 'sent_approve' or jj.state in 'paid' or jj.state in 'register_payment':
                    total_rem += jj.total_duration_sum
            aa = self.standard_hour - total_rem
        # print(aa, 'class hour till')
        stand = self.env['subject.details'].sudo().search([])
        # for rec in stand:
        #     if self.
        self.change_faculty_boolean = True

    @api.onchange('faculty_id', 'record_ids.date', 'is_it_changed')
    def _onchange_is_it_changed(self):
        print('working')
        if self.faculty_id.is_it_changed_faculty == True:
            print('true')
            self.is_it_changed = True
        else:
            print('false')
            self.is_it_changed = False

    is_it_changed = fields.Boolean(string='Is It Changed')

    def faculty_change_done(self):
        if not self.new_faculty:
            raise UserError('Please Select New Faculty')
        else:
            partner = self.env['faculty.details'].browse(self.new_faculty.id)
            partner.sudo().write({
                'is_it_changed_faculty': True})
            self.faculty_id = self.new_faculty
            net_hour = self.env['daily.class.record'].sudo().search([])
            total_rem = 0
            std_hr = []
            for jj in net_hour:
                if self.old_faculty == jj.faculty_id and self.branch_name == jj.branch_name and self.class_room == jj.class_room and self.course_id == jj.course_id and self.subject_id == jj.subject_id:
                    if jj.state in 'to_approve' or jj.state in 'approve' or jj.state in 'sent_approve' or jj.state in 'paid' or jj.state in 'register_payment':
                        total_rem += jj.total_duration_sum
                aa = self.standard_hour - total_rem
                std_hr.append(aa)
            print(std_hr, 'class hour till')
            # self.new_faculty.faculty_current_id = self.faculty_id.id
            self.change_faculty_boolean = False
            new_fac = self.env['changed.standard.hours'].sudo().search([])

            new_fac.sudo().create({'faculty_id': self.new_faculty.id,
                                   'course_id': self.course_id.id,
                                   'subject_id': self.subject_id.id,
                                   'standard_hour': aa,
                                   'old_standard_hour': self.standard_hour,
                                   'coordinator_id': self.create_uid.id,
                                   'date_update': self.create_date
                                   })
            self.is_it_changed = True

    def faculty_change_cancel(self):
        self.new_faculty = False
        self.change_faculty_boolean = False

    @api.onchange('faculty_id')
    def onchange_faculty_changed(self):
        print('changedddd')
        if self.faculty_id.is_it_changed_faculty == True:
            self.is_it_changed = True
        else:
            self.is_it_changed = False

    @api.depends('faculty_id', 'subject_id', 'course_id', 'record_ids.net_hour', 'class_room', 'branch_name')
    def _class_till_now_view(self):
        hour = self.env['daily.class.record'].sudo().search([])
        total = 0
        for i in hour:
            if self.faculty_id == i.faculty_id and self.branch_name == i.branch_name and self.class_room == i.class_room and self.course_id == i.course_id and self.subject_id == i.subject_id:
                if i.state in 'to_approve' or i.state in 'approve' or i.state in 'sent_approve' or i.state in 'paid' or i.state in 'draft' or i.state in 'register_payment':
                    print(i.total_duration_sum, 'total duration')
                    total += i.total_duration_sum
                    self.class_till_view = total
            # else:
            #     self.class_till_view = 0

    class_till_view = fields.Float(string='Class Hours Till Now', compute='_class_till_now_view', store=True)

    @api.depends('class_till_view', 'standard_hour')
    def _compute_remaining_hours(self):
        for rec in self:
            if rec.standard_hour != 0:
                rec.remaining_hour_view = rec.standard_hour - rec.class_till_view
            else:
                rec.remaining_hour_view = 0

    remaining_hour_view = fields.Float(string='Remaining Hours', compute='_compute_remaining_hours', store=True)

    def action_print_daily_class(self):
        rep = self.env['daily.class.record'].search([])
        # print(self.env.context.get('active_ids'), 'ids')
        # print(rep, 'rep')

        all_zero_records = self.env['daily.class.record'].sudo().search(
            [('class_hour_till_now', '=', 0), ('month_of_record', '=', 'august')])
        already_done = []
        for j in all_zero_records:
            recs = self.env['daily.class.record'].sudo().search(
                [('id', 'not in', already_done), ('faculty_id', '=', j.faculty_id.id),
                 ('class_room', '=', j.class_room.id), ('branch_name', '=', j.branch_name.id),
                 ('course_id', '=', j.course_id.id), ('state', 'not in', ['rejected', 'draft']),
                 ('subject_id', '=', j.subject_id.id)])
            total = 0
            print(recs, 'recs')
            for rec in recs:
                total += rec.total_duration_sum
            j.class_hour_till_now = total
            already_done.append(j.id)
        all_rec_for_payment = self.env['daily.class.record'].sudo().search([])
        for pay_rec in all_rec_for_payment:
            payment = self.env['payment.total'].search([('class_hours_till', '=', 0)])

            for payments in payment:
                if payments.current_id == pay_rec.id:
                    payments.class_hours_till = pay_rec.class_hour_till_now

    def get_old_reports(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Records',
            'view_mode': 'tree,form',
            'res_model': 'daily.class.record',
            'domain': [('branch_name', '=', self.branch_name.id), ('faculty_id', '=', self.faculty_id.id),
                       ('class_room', '=', self.class_room.id), ('course_id', '=', self.course_id.id),
                       ('subject_id', '=', self.subject_id.id), ('id', '!=', self.id)],
            'context': "{'create': False}"
        }


class RecordData(models.Model):
    _name = 'record.data'

    start_date = fields.Float(string='Start time', required=True, help='Enter rail way time')
    end_date = fields.Float(string='End time', required=True, help='Enter rail way time')

    record_id = fields.Many2one('daily.class.record', ondelete='cascade')
    break_reason = fields.Char(string='Break reason')
    break_time = fields.Float(string='Break Time', widget='time')
    topic = fields.Char(string='Topic')
    upaya_class = fields.Boolean(string='Upaya Class', help="When selecting the 'Upaya' class, the hour will be excluded from standard hour calculations, extra hour calculations, and similar computations.")
    date = fields.Date(string='Date', default=fields.Date.today)
    remaining_hours = fields.Float('Remaining hours')

    @api.depends('start_date', 'end_date')
    def _compute_net_time(self):
        for record in self:
            if record.start_date and record.end_date:
                record.net_duration = record.end_date - record.start_date
            else:
                record.net_duration = 0.0

    net_duration = fields.Float(string='Net', compute='_compute_net_time', readonly=True, store=True)

    @api.depends('break_time', 'net_duration')
    def _compute_net_total_duration(self):
        for record in self:
            record.net_hour = record.net_duration - record.break_time

    net_hour = fields.Float(string='Net Hour', digits=(16, 2), widget='timepicker', help='Enter time in hours',
                            compute='_compute_net_total_duration', store=True)

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


class SkippedClasses(models.Model):
    _name = 'skipped.classes'

    date_skip = fields.Date(string='Date')
    reason_skip = fields.Char(string='Reason')
    skip_id = fields.Many2one('daily.class.record')
