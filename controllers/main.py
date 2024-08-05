from odoo import http
from odoo.http import request
import io
import xlsxwriter
from odoo.addons.web.controllers.main import content_disposition

class FacultyReportController(http.Controller):

    @http.route([
        '/faculty/excel_report/<model("faculty.class.report"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, report_id=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Faculty Report' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': 'white',
            'bg_color': '#2C3E50',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        total_duration = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#b5fc5d',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })


        # get data for the report
        report_lines = report_id.get_report_lines()
        selection_field = report_id.selection_field
        faculty = report_id.faculty_id.name.name

        # prepare excel sheet styles and formats
        header_style = workbook.add_format({'bold': True})
        text_style = workbook.add_format()
        sheet = workbook.add_worksheet("invoices")
        # print(request.report_id.faculty_id.name.name)
        # Write the faculty name in the first row
            # Write the faculty name in the first row
        sheet.write(0, 0, 'Faculty', header_format)
        sheet.write(0, 1, faculty, text_style)

        # Write column headers based on the selection field
        col_start = 2
        if selection_field == 'branch':
            sheet.write(col_start, 0, 'No.', header_format)
            sheet.write(col_start, 1, 'Branch', header_format)
            sheet.write(col_start, 2, 'Total Duration (Hr)', header_format)
        elif selection_field == 'class':
            sheet.write(col_start, 0, 'No.', header_format)
            sheet.write(col_start, 1, 'Class', header_format)
            sheet.write(col_start, 2, 'Total Duration (Hr)', header_format)
        elif selection_field == 'course':
            sheet.write(col_start, 0, 'No.', header_format)
            sheet.write(col_start, 1, 'Course', header_format)
            sheet.write(col_start, 2, 'Total Duration (Hr)', header_format)
        elif selection_field == 'subject':
            sheet.write(col_start, 0, 'No.', header_format)
            sheet.write(col_start, 1, 'Subject', header_format)
            sheet.write(col_start, 2, 'Total Duration (Hr)', header_format)
        elif selection_field == 'total':
            sheet.write(col_start, 0, 'No.', header_format)
            sheet.write(col_start, 1, 'Branch', header_format)
            sheet.write(col_start, 2, 'Class', header_format)
            sheet.write(col_start, 3, 'Course', header_format)
            sheet.write(col_start, 4, 'Subject', header_format)
            sheet.write(col_start, 5, 'Total', header_format)

            sheet.write(col_start, 5, 'Total Duration (Hr)', header_format)

        # Write the report lines starting from the 5th row
        row = col_start + 1
        number = 1
        total_duration_sum = 0
        for line in report_lines:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, text_style)

            if selection_field == 'branch':
                sheet.write(row, 1, line.get('branch', ''), text_style)
            elif selection_field == 'class':
                sheet.write(row, 1, line.get('class', ''), text_style)
            elif selection_field == 'course':
                sheet.write(row, 1, line.get('course', ''), text_style)
            elif selection_field == 'subject':
                sheet.write(row, 1, line.get('subject', ''), text_style)
            elif selection_field == 'total':
                sheet.write(row, 1, line.get('branch', ''), text_style)
                sheet.write(row, 2, line.get('classes', ''), text_style)
                sheet.write(row, 3, line.get('course', ''), text_style)
                sheet.write(row, 4, line.get('subject', ''), text_style)
                sheet.write(row, 5, line.get('total_net', ''), text_style)

                total_duration_sum += line.get('total_net', 0)
            row += 1
            number += 1
        sheet.write(row, 4, 'Total Duration (Hr)', header_format)
        sheet.write(row, 5, total_duration_sum, total_duration)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

