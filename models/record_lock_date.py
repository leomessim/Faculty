from odoo import models, fields, api, _


class FacultyDailyRecordLockDate(models.Model):
    _name = 'faculty.daily.record.lock.date'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lock_day'
    _description = 'Faculty Daily Record Lock Date'

    lock_day = fields.Integer(string='Lock Day')

    def action_cron_locking_record_manual(self):
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

