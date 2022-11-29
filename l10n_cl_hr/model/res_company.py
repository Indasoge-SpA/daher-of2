# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"


    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', company_dependent=True)
    mutualidad_id = fields.Many2one('hr.mutual', 'Mutual', company_dependent=True)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, company_dependent=True)
    mutual_seguridad = fields.Float('Mutualidad', help="Mutual de Seguridad", default=0.95, company_dependent=True)



    def _create_resource_calendar(self):
        """
        Override to set the default calendar to
        45 hours/week for Chilean companies
        """
        cl_companies = self.filtered(lambda c: c.country_id.code == "CL" and not c.resource_calendar_id)
        for company in cl_companies:
            company.resource_calendar_id = self.env['resource.calendar'].create({
                'name': _('Standard 45 hours/week'),
                'company_id': company.id,
                'hours_per_day': 9.0,
                'full_time_required_hours': 45.0,
                'attendance_ids': [
                    (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 13, 'day_period': 'morning'}),
                    (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 14, 'hour_to': 18, 'day_period': 'afternoon'}),
                    (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 13, 'day_period': 'morning'}),
                    (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 14, 'hour_to': 18, 'day_period': 'afternoon'}),
                    (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 13, 'day_period': 'morning'}),
                    (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 14, 'hour_to': 18, 'day_period': 'afternoon'}),
                    (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 13, 'day_period': 'morning'}),
                    (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 14, 'hour_to': 18, 'day_period': 'afternoon'}),
                    (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 13, 'day_period': 'morning'}),
                    (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 14, 'hour_to': 18, 'day_period': 'afternoon'})
                ],
            }).id
        super(ResCompany, self - cl_companies)._create_resource_calendar()
