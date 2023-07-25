from odoo import models, fields, api, _


class FacultyDetails(models.Model):
    _name = "faculty.details"
    _inherit = 'mail.thread'

    name = fields.Many2one('res.users', domain=[('faculty_check', '=', True)], string="Name")
    qualification = fields.Char(string="Qualification")
    exp = fields.Char(string="Experience")
    course = fields.Many2many('courses.details', string="Courses")
    # bank_acc = fields.Integer(string="Bank account")
    test = fields.Many2one('res.class', string='Class Room')
    pay_test = fields.Char(string="Pay")
    tds = fields.Char(string="Tds")
    salary_hr = fields.Integer(string="Salary per Hour")
    bank_acc = fields.Many2one('res.partner.bank',
                               string="Bank Account",
                               ondelete='restrict', copy=False, required=True)
    date_birth = fields.Date(string='Date of Birth')
    pan_number = fields.Char(string='Pan Number')
    payout_ids = fields.One2many('payout', 'payout_id')
    gst_number = fields.Char(string='Gst Number')
    bank_name = fields.Char('Bank name', required=True)
    account_holder = fields.Char('Account holder name')
    bank_account_no = fields.Char('Bank account number', required=True)
    ifsc = fields.Char('IFSC', required=True)
    user_id = fields.Many2one('res.users', string="Approved By", default=lambda self: self.env.user.id, readonly="1",
                              tracking=True)
    scheduled_ids = fields.One2many('scheduled.classes', 'schedule_id')
    date_month = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month of Birth', copy=False,
        tracking=True)
    current_status = fields.Selection([
        ('active', 'Active'), ('inactive', 'Inactive')], string='Current status', default='active')
    inactive_date = fields.Date(string='Inactive date')
    gst_status = fields.Boolean('Gst status')

    @api.onchange('date_birth')
    def _onchange_date_birth(self):
        print(self.name.name, "this user")
        if self.date_birth != False:
            if self.date_birth.month == 1:
                self.date_month = 'january'
            elif self.date_birth.month == 2:
                self.date_month = 'february'
            elif self.date_birth.month == 3:
                self.date_month = 'march'
            elif self.date_birth.month == 4:
                self.date_month = 'april'
            elif self.date_birth.month == 5:
                self.date_month = 'may'
            elif self.date_birth.month == 6:
                self.date_month = 'june'
            elif self.date_birth.month == 7:
                self.date_month = 'july'
            elif self.date_birth.month == 8:
                self.date_month = 'august'
            elif self.date_birth.month == 9:
                self.date_month = 'september'
            elif self.date_birth.month == 10:
                self.date_month = 'october'
            elif self.date_birth.month == 11:
                self.date_month = 'november'
            elif self.date_birth.month == 12:
                self.date_month = 'december'
            else:
                print("not match")
        else:
            print("ok")


class Courses(models.Model):
    _name = 'courses.details'
    _inherit = 'mail.thread'

    name = fields.Char(string='Course name', required=True)
    subject_ids = fields.Many2many('subject.details', string='Subject')
    # department = fields.Many2one('primary.department', string='Primary department', required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    current_id = fields.Integer()

    def add_subject(self):
        # self.state = 'confirm'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'subject.details',
            'view_type': 'form',
            'view_mode': 'form,tree',
        }
        # self.current_id = self.id
        # print("current id", self.id)


class SubjectDetails(models.Model):
    _name = 'subject.details'
    _inherit = 'mail.thread'

    name = fields.Char(string='Subject Name')
    stnd_hr = fields.Float(string='Standard Hours')
    rec_id = fields.Integer()
    course_sub_id = fields.Many2one('courses.details', string='course')
    old_ids = fields.One2many('old.standard.hours', 'old_id', compute='old_standard_hr', store=True)

    # @api.model
    # def create(self, vals):
    #     new = []
    #     datas = {
    #         'name': self.name,
    #     }
    #     new.append((0, 0, datas))
    #     self.env['subject.details'].create({
    #         'old_ids': new,
    #     }
    #     )
    #     return super(SubjectDetails, self).create(vals)

    @api.depends('stnd_hr')
    def old_standard_hr(self):
        new = []
        datas = {
            'old_hr': self.stnd_hr,
            'date_update': self.create_date,
            'name': self.env.user.name
        }
        new.append((0, 0, datas))
        self.old_ids = new

    # @api.onchange('name')
    # def _onchange_name(self):
    #     self.env['courses.details'].search([])
    #     self.rec_id = self.id
    #     print(self.rec_id, 'record')


class OldStandardHours(models.Model):
    _name = 'old.standard.hours'
    _inherit = 'mail.thread'

    old_hr = fields.Float(string='Old Standard Hours')
    date_update = fields.Date(string='Update Date')
    name = fields.Char(string='Name')
    old_id = fields.Many2one('subject.details', string='old standard hours')


class ScheduledClasses(models.Model):
    _name = 'scheduled.classes'
    _description = 'Scheduled classes'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='Date', required=True)
    day = fields.Char(string='Day')
    time_from = fields.Float(string='Time From', widget='time')
    time_to = fields.Float(string='Time To', widget='time')
    faculty_id = fields.Many2one('res.users', string='Faculty', domain=[('faculty_check', '=', True)])
    subject_id = fields.Many2one('subject.details', string='Subject')
    record_id = fields.Integer()

    schedule_id = fields.Many2one('faculty.details', string='Scheduled Classes')
