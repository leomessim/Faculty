from odoo import models, fields, api, _


class FacultyReportClasses(models.TransientModel):
    _name = 'faculty.class.report'
    _description = 'Faculty Report'

    faculty_id = fields.Many2one('faculty.details', string='Faculty', required=1)
    record_ids = fields.Many2many('daily.class.record', string='Records')
    datas_ids = fields.Many2many('record.data', string='Datas')
    selection_field = fields.Selection([
        ('branch', 'Branch'),
        ('class', 'Class'),
        ('course', 'Course'),
        ('subject', 'Subject'),
        ('total', 'Total')
    ], string='Filter', default='branch')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.onchange('faculty_id', 'selection_field', 'from_date', 'to_date')
    def _onchange_faculty_id(self):
        domain = []
        sec_domain = []
        for rec in self:
            if rec.faculty_id:
                domain.append(('faculty_id', '=', rec.faculty_id.id))
                sec_domain.append(('record_id.faculty_id', '=', rec.faculty_id.id))
            if rec.from_date and rec.to_date:
                sec_domain.append(('date', '>=', rec.from_date))
                sec_domain.append(('date', '<=', rec.to_date))
                domain.append(('create_date', '>=', rec.from_date))
                domain.append(('create_date', '<=', rec.to_date))

        if domain:
            datas = self.env['record.data'].sudo().search(sec_domain)
            records = self.env['daily.class.record'].sudo().search(domain)
            self.record_ids = [(6, 0, records.ids)]
            self.datas_ids = [(6, 0, datas.ids)]
        else:
            self.record_ids = [(5,)]
            self.datas_ids = [(5,)]

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
                records = self.env['record.data'].sudo().search(
                    [('id', 'in', self.datas_ids.ids),
                     ('record_id.branch_id', '=', branch.id),
                     ('record_id.state', 'in', ['approve', 'register_payment', 'paid'])]
                )
                print(records, 'rec')
                for record in records:
                    total_hour += record.net_hour

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
                records = self.env['record.data'].sudo().search(
                    [('id', 'in', self.datas_ids.ids),
                     ('record_id.class_room', '=', cl.id),
                     ('record_id.state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.net_hour

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
                records = self.env['record.data'].sudo().search(
                    [('id', 'in', self.datas_ids.ids),
                     ('record_id.course_id', '=', course.id),
                     ('record_id.state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.net_hour

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
                records = self.env['record.data'].sudo().search(
                    [('id', 'in', self.datas_ids.ids),
                     ('record_id.subject_id', '=', subject.id),
                     ('record_id.state', 'in', ['approve', 'register_payment', 'paid'])]
                )

                for record in records:
                    total_hour += record.net_hour

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

            records = self.env['record.data'].sudo().search(
                [('id', 'in', self.datas_ids.ids),
                 ('record_id.state', 'in', ['approve', 'register_payment', 'paid'])]
            )

            for record in records:
                total_hour += record.net_hour

                if total_hour > 0:
                    line = {
                        # 'faculty_id': self.faculty_id.name.name,
                        'total_duration': total_hour,
                        'classes': record.record_id.class_room.name,
                        'branch': record.record_id.branch_id.branch_name,
                        'course': record.record_id.course_id.name,
                        'subject': record.record_id.subject_id.name,
                        'total_net': record.net_hour

                        # Include other fields as necessary
                    }
                    print(line, 'iii')
                    invoice_list.append(line)

        return invoice_list
