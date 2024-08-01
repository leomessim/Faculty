from odoo import http
from odoo.http import request
import io
import xlsxwriter
from odoo.addons.web.controllers.main import content_disposition

class FacultyReportController(http.Controller):

    @http.route([
        '/faculty/excel_report/<model("faculty.class.report"):report_id>',
    ], type='http', auth="user", csrf=False)
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
        # get data for the report.
        report_lines = report_id.get_report_lines() if report_id else []
        # prepare excel sheet styles and formats
        header_style = workbook.add_format({'bold': True})
        text_style = workbook.add_format()
        sheet = workbook.add_worksheet("invoices")
        sheet.write(0, 0, 'No.', header_style)
        sheet.write(0, 1, 'Faculty', header_style)
        # sheet.write(0, 2, 'Standard Hour', header_style)
        sheet.write(0, 2, 'Total Duration', header_style)

        row = 1
        number = 1
        # write the report lines to the excel document
        for line in report_lines:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, text_style)
            sheet.write(row, 1, line.get('faculty_id', ''), text_style)
            # sheet.write(row, 2, line.get('standard_hour', ''), text_style)
            sheet.write(row, 2, line.get('total_duration', ''), text_style)
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
