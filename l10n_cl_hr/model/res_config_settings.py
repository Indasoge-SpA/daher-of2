
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    caja_compensacion = fields.Char(
        string="Tasa", default=0.60, help="Caja de Compensacion",
        config_parameter='l10n_cl_hr.caja_compensacion')
    fonasa = fields.Char(
        string="Fonasa", default=6.40, help="Fonasa",
        config_parameter='l10n_cl_hr.fonasa')
    pensiones_ips = fields.Char(
        string="Pensiones IPS", default=18.84, help="Pensiones IPS",
        config_parameter='l10n_cl_hr.pensiones_ips')
    tope_imponible_salud = fields.Char(
        string="Tope Imponible Salud", default=7.00, help="Pensiones IPS",
        config_parameter='l10n_cl_hr.tope_imponible_salud')
    isl = fields.Char(
        string="ISL", default=7.00, help="Instituto de Seguridad Laboral",
        config_parameter='l10n_cl_hr.isl')
