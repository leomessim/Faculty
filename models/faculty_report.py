from odoo import models, fields, api, _


class FacultyReportClasses(models.TransientModel):
    _name = 'faculty.class.report'
    _description = 'Faculty Report'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=1)
    record_ids = fields.Many2many('daily.class.record', string='Records')
    branch_id = fields.Many2one('logic.base.branches', string='Branch')
    class_id = fields.Many2one('class.room', string='Class')
    course_id = fields.Many2one('courses.details', string='Course')
    subject_id = fields.Many2one('subject.details', string='Subject')
    month_of_record = fields.Selection([
        ('january', 'January'), ('february', 'February'),
        ('march', 'March'), ('april', 'April'),
        ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
        ('september', 'September'), ('october', 'October'), ('november', 'November'),
        ('december', 'December')],
        string='Month')
    standard_hour = fields.Float(string='Standard Hour')

    @api.onchange('faculty_id', 'branch_id', 'class_id', 'subject_id', 'course_id', 'month_of_record')
    def _onchange_faculty_id(self):
        domain = []
        for rec in self:
            if rec.faculty_id:
                domain.append(('faculty_id', '=', rec.faculty_id.id))
                if rec.branch_id:
                    domain.append(('branch_id', '=', rec.branch_id.id))
                if rec.class_id:
                    domain.append(('class_room', '=', rec.class_id.id))
                if rec.course_id:
                    domain.append(('course_id', '=', rec.course_id.id))
                if not rec.course_id:
                    rec.standard_hour = 0
                if rec.month_of_record:
                    domain.append(('month_of_record', '=', rec.month_of_record))
                if rec.subject_id:
                    domain.append(('subject_id', '=', rec.subject_id.id))

        if domain:
            records = self.env['daily.class.record'].sudo().search(domain)
            self.record_ids = [(6, 0, records.ids)]
        else:
            self.record_ids = [(5,)]

    def print_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/faculty/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_report_lines(self):
        invoice_list = []
        total_hour = 0
        for move in self.record_ids:
            print(move, 'moves')
            if move.state in ['approve','register_payment','paid']:
                total_hour += move.total_duration_sum

        line = {'month': self.month_of_record,
                'faculty_id': self.faculty_id.name.name,
                'total_duration': total_hour,
                'standard_hour': self.standard_hour,
                'branch': self.branch_id.branch_name,
                'class': self.class_id.name,
                'course': self.course_id.name,
                'subject': self.subject_id.name
                }
        print(total_hour, 'total_hour')
        invoice_list.append(line)
        return invoice_list
