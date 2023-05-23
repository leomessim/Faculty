from odoo import fields, models, _


class Department(models.Model):
    _name = 'faculty.department'
    _rec_name = 'deprt_prime'

    deprt_prime = fields.Many2one('primary.department', string='Primary Department', required=True)
    adm_fee = fields.Float(string='Admission fee', required=True, related='deprt_prime.fee')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')

    # def confirm_department(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'admission.details',
    #         'view_type': 'tree',
    #         'view_mode': 'tree,form',
    #     }
    #     print('hi')


class PrimaryDepartment(models.Model):
    _name = 'primary.department'
    _rec_name = 'dpt'

    dpt = fields.Char(string='Department')
    fee = fields.Float(string='Admission fee')

class AdmissionDepartment(models.Model):
    _name = 'admission.details'

    course_ids = fields.Many2many('courses.details', string='Courses')
    batches_ids = fields.Many2many('res.batch', string='Batches')
    class_room_id = fields.Many2one('res.class', string='Classroom')
    student_id = fields.Char(string='Students')
