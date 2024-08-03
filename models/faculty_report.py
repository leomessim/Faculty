from odoo import models, fields, api, _


class FacultyReportClasses(models.TransientModel):
    _name = 'faculty.class.report'
    _description = 'Faculty Report'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=1)
    record_ids = fields.Many2many('daily.class.record', string='Records')
    selection_field = fields.Selection([
        ('branch', 'Branch'),
        ('class', 'Class'),
        ('course', 'Course'),
        ('subject', 'Subject'),
        ('total', 'Total')
    ], string='Filter', default='branch')

    @api.onchange('faculty_id', 'selection_field')
    def _onchange_faculty_id(self):
        domain = []
        for rec in self:
            if rec.faculty_id:
                domain.append(('faculty_id', '=', rec.faculty_id.id))

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
        if self.selection_field == 'branch':
            branches = self.env['logic.base.branches'].sudo().search([])

            for branch in branches:
                total_hour = 0
                rec = self.record_ids.ids
                print(rec , 'rrr')
                records = self.env['daily.class.record'].sudo().search(
                    [('id', 'in', self.record_ids.ids),
                     ('branch_id', '=', branch.id),
                     ('state', 'in', ['approve', 'register_payment', 'paid'])]
                )
                print(records, 'rec')
                for record in records:
                    total_hour += record.total_duration_sum

                if total_hour > 0:
                    line = {
                        'faculty_id': self.faculty_id.name.name,
                        'branch': branch.branch_name,
                        'total_duration': total_hour,
                        # Include other fields as necessary
                    }
                    invoice_list.append(line)
                    print(f"Branch: {branch.branch_name}, Total Duration: {total_hour}")

        elif self.selection_field == 'class':
            classes = self.env['class.room'].sudo().search([])

            for cl in classes:
                total_hour = 0
                records = self.env['daily.class.record'].sudo().search(
                    [('id', 'in', self.record_ids.ids),
                     ('class_room', '=', cl.id),
                     ('state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.total_duration_sum

                if total_hour > 0:
                    line = {
                        'faculty_id': self.faculty_id.name.name,
                        'class': cl.name,
                        'total_duration': total_hour,
                        # Include other fields as necessary
                    }
                    invoice_list.append(line)

        elif self.selection_field == 'course':
            courses = self.env['courses.details'].sudo().search([])

            for course in courses:
                total_hour = 0
                records = self.env['daily.class.record'].sudo().search(
                    [('id', 'in', self.record_ids.ids),
                     ('course_id', '=', course.id),
                     ('state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.total_duration_sum

                if total_hour > 0:
                    line = {
                        'faculty_id': self.faculty_id.name.name,
                        'course': course.name,
                        'total_duration': total_hour,
                        # Include other fields as necessary
                    }
                    invoice_list.append(line)

        elif self.selection_field == 'subject':
            subjects = self.env['subject.details'].sudo().search([])

            for subject in subjects:
                total_hour = 0
                records = self.env['daily.class.record'].sudo().search(
                    [('id', 'in', self.record_ids.ids),
                     ('subject_id', '=', subject.id),
                     ('state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.total_duration_sum

                if total_hour > 0:
                    line = {
                        'faculty_id': self.faculty_id.name.name,
                        'subject': subject.name,
                        'total_duration': total_hour,
                        # Include other fields as necessary
                    }
                    invoice_list.append(line)

        else:
            total_hour = 0
            records = self.env['daily.class.record'].sudo().search(
                [('id', 'in', self.record_ids.ids),
                 ('state', 'in', ['approve', 'register_payment', 'paid'])]
            )

            for record in records:
                total_hour += record.total_duration_sum

            if total_hour > 0:
                line = {
                    'faculty_id': self.faculty_id.name.name,
                    'total_duration': total_hour,
                    # Include other fields as necessary
                }
                invoice_list.append(line)

        return invoice_list


