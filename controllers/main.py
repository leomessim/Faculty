from odoo import http
from odoo.http import request
import io
import xlsxwriter
from odoo.addons.web.controllers.main import content_disposition

class FacultyReportController(http.Controller):

    @http.route('/faculty/excel_report/<int:report_id>', type='http', auth='user')
    def get_faculty_excel_report(self, report_id=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Faculty_report' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        report = request.env['faculty.class.report'].sudo().browse(report_id)
        report_lines = report.get_report_lines() if report else []

        # Check if any report line has data for the optional columns
        has_branch = any(line.get('branch') for line in report_lines)
        has_class = any(line.get('class') for line in report_lines)
        has_course = any(line.get('course') for line in report_lines)
        has_subject = any(line.get('subject') for line in report_lines)
        has_month = any(line.get('month') for line in report_lines)

        # Prepare excel sheet styles and formats
        header_style = workbook.add_format({'bold': True})
        text_style = workbook.add_format()
        sheet = workbook.add_worksheet("invoices")
        sheet.write(0, 0, 'No.', header_style)
        sheet.write(0, 1, 'Faculty', header_style)
        col = 2
        if has_branch:
            sheet.write(0, col, 'Branch', header_style)
            col += 1
        if has_month:
            sheet.write(0, col, 'Month', header_style)
            col += 1
        if has_class:
            sheet.write(0, col, 'Class', header_style)
            col += 1
        if has_course:
            sheet.write(0, col, 'Course', header_style)
            col += 1
        if has_subject:
            sheet.write(0, col, 'Subject', header_style)
            col += 1
        sheet.write(0, col, 'Total Duration (Hr)', header_style)

        # Write the report lines to the excel document
        row = 1
        number = 1
        for line in report_lines:
            sheet.set_row(row, 20)
            col = 0
            sheet.write(row, col, number, text_style)
            col += 1
            sheet.write(row, col, line.get('faculty_id', ''), text_style)
            col += 1
            if has_branch:
                sheet.write(row, col, line.get('branch', ''), text_style)
                col += 1
            if has_month:
                sheet.write(row, col, line.get('month', ''), text_style)
                col += 1
            if has_class:
                sheet.write(row, col, line.get('class', ''), text_style)
                col += 1
            if has_course:
                sheet.write(row, col, line.get('course', ''), text_style)
                col += 1
            if has_subject:
                sheet.write(row, col, line.get('subject', ''), text_style)
                col += 1
            sheet.write(row, col, line.get('total_duration', ''), text_style)
            row += 1
            number += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

