
import math
from odoo import api, fields, models, tools, _
from datetime import datetime, date, timedelta, time
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class HRHolidaysStatus(models.Model):
    _inherit = 'hr.leave.type'
    is_continued = fields.Boolean('Discount Weekends')
    movimientos_personal = fields.Selection(
     [('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')],
     default='0', string= "Código Movimiento")



class HrLeave(models.Model):
    _inherit = 'hr.leave'

    company_id = fields.Many2one('res.company', 'User Company',
                                 copy=False,
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)

    def _get_number_of_days(self, date_from, date_to, employee_id):
        days = super(HrLeave, self)._get_number_of_days(date_from,
                                                        date_to,
                                                        employee_id)
        # Health Leave are counted all days between two dates no matter what
        if (employee_id and self.holiday_status_id.is_continued):
            time_delta = date_to - date_from
            days = (time_delta.days)+1
            return {'days': days, 'hours': days*9}
        elif self.holiday_status_id.exclude_public_holidays:
            return days
        today_hours = self.env.company.resource_calendar_id.\
            get_work_hours_count(
                datetime.combine(date_from.date(), time.min),
                datetime.combine(date_from.date(), time.max),
                False)
        hours = self.env.company.resource_calendar_id.\
            get_work_hours_count(date_from, date_to)
        return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
