from odoo import api,models,fields,SUPERUSER_ID
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class HrAffidavit(models.Model):
    _name = 'hr.affidavit'
    _description = 'Certificado de sobre sueldos'

    year = fields.Date('Año comercial',required=True)
    tributary_year = fields.Date('Año tributario',required=True)
    company_id = fields.Many2one('res.company',string='Compañia',readonly=True,
        default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency','Moneda', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    bonus_cert_ids = fields.Many2many('hr.bonus.certificate', 'affidavit_certificate_rel', 'affidavit_id', string='Certificados de sobresueldos a informar')
    txt_filename = fields.Char('Nombre archivo')
    txt_binary = fields.Binary('Archivo txt')
    sii_folio = fields.Char('Folio SII',size=7)
    cod_presentacion = fields.Selection([
        ('F' , 'Formulario'),
        ('I' , 'Internet'),
        ('M', 'Excepción')
    ], 'Codigo presentacion', default='I')
    tipo_declaracion = fields.Selection([
        ('O' , 'Original'),
        ('R' , 'Rectificatoria')
    ], 'Tipo de Declaración', default='O')
    tot_pension_bruta = fields.Monetary('Total Pension Imponible', currency_field='currency_id')
    tot_cotizacion_prev = fields.Monetary('Total Cotizacion previsional', currency_field='currency_id')
    tot_renta_imponible = fields.Monetary('Total Renta Neta', currency_field='currency_id')
    tot_impuesto_retenido = fields.Monetary('Total Impuesto unico', currency_field='currency_id')
    tot_mayor_reten_imp_solicitado = fields.Monetary('Total Mayor retencion impuesto solicitado', currency_field='currency_id')
    tot_renta_exenta = fields.Monetary('Total Renta exenta', currency_field='currency_id')
    tot_renta_no_gravada = fields.Monetary('Total Renta no Gravada', currency_field='currency_id')
    tot_rebaja_zona_extrema = fields.Monetary('Total Rebaja zona extrema', currency_field='currency_id')
    tot_ma_renta_bruta = fields.Monetary('Total Montos ajustados renta imponible', currency_field='currency_id')
    tot_ma_renta_imponible = fields.Monetary('Total Montos ajustados renta neta', currency_field='currency_id')
    tot_ma_impuesto_unico = fields.Monetary('Total Montos ajustados impuesto unico', currency_field='currency_id')
    tot_ma_may_ret_imp_sol = fields.Monetary('Total Montos ajustados Mayor retencion impuesto solicitado', currency_field='currency_id')
    tot_ma_renta_exenta = fields.Monetary('Total Montos ajustados renta exenta', currency_field='currency_id')
    tot_ma_renta_no_gravada = fields.Monetary('Total Montos ajustados Renta no Gravada', currency_field='currency_id')
    tot_ma_rebaja_zona_extrema = fields.Monetary('Total Montos ajustados rebaja zona extrema', currency_field='currency_id')

    @api.onchange('bonus_cert_ids')
    def onchage_bonus_cert_ids(self):
        tot_pension_bruta = 0
        tot_cotizacion_prev = 0
        tot_renta_imponible = 0
        tot_impuesto_retenido = 0
        tot_mayor_reten_imp_solicitado = 0
        tot_renta_exenta = 0
        tot_renta_no_gravada = 0
        tot_rebaja_zona_extrema = 0
        tot_ma_renta_bruta = 0
        tot_ma_renta_imponible = 0
        tot_ma_impuesto_unico = 0
        tot_ma_may_ret_imp_sol = 0
        tot_ma_renta_exenta = 0
        tot_ma_renta_no_gravada = 0
        tot_ma_rebaja_zona_extrema = 0
        for item in self:
            for cert in item.bonus_cert_ids:
                tot_pension_bruta += cert.tot_pension_bruta
                tot_cotizacion_prev += cert.tot_cotizacion_prev
                tot_renta_imponible += cert.tot_renta_imponible
                tot_impuesto_retenido += cert.tot_impuesto_retenido
                tot_mayor_reten_imp_solicitado += cert.tot_mayor_reten_imp_solicitado
                tot_renta_exenta += cert.tot_renta_exenta
                tot_renta_no_gravada += cert.tot_renta_no_gravada
                tot_rebaja_zona_extrema += cert.tot_rebaja_zona_extrema
                tot_ma_renta_bruta += cert.tot_ma_renta_bruta
                tot_ma_renta_imponible += cert.tot_ma_renta_imponible
                tot_ma_impuesto_unico += cert.tot_ma_impuesto_unico
                tot_ma_may_ret_imp_sol += cert.tot_ma_may_ret_imp_sol
                tot_ma_renta_exenta += cert.tot_ma_renta_exenta
                tot_ma_renta_no_gravada += cert.tot_ma_renta_no_gravada
                tot_ma_rebaja_zona_extrema += cert.tot_ma_rebaja_zona_extrema
            item.tot_pension_bruta = tot_pension_bruta
            item.tot_cotizacion_prev = tot_cotizacion_prev
            item.tot_renta_imponible = tot_renta_imponible
            item.tot_impuesto_retenido = tot_impuesto_retenido
            item.tot_mayor_reten_imp_solicitado = tot_mayor_reten_imp_solicitado
            item.tot_renta_exenta = tot_renta_exenta
            item.tot_renta_no_gravada = tot_renta_no_gravada
            item.tot_rebaja_zona_extrema = tot_rebaja_zona_extrema
            item.tot_ma_renta_bruta = tot_ma_renta_bruta
            item.tot_ma_renta_imponible = tot_ma_renta_imponible
            item.tot_ma_impuesto_unico = tot_ma_impuesto_unico
            item.tot_ma_may_ret_imp_sol = tot_ma_may_ret_imp_sol
            item.tot_ma_renta_exenta = tot_ma_renta_exenta
            item.tot_ma_renta_no_gravada = tot_ma_renta_no_gravada
            item.tot_ma_rebaja_zona_extrema = tot_ma_rebaja_zona_extrema


    def run_cert_employee(self):
        cert_obj = self.env['hr.bonus.certificate']
        emplo_obj = self.env['hr.payslip']
        for item in self:
            commands = []
            payslips = emplo_obj.search([
                ('state','=','done'),
                ('date_from','>=',item.year),
                ('date_to','<=',item.tributary_year)
            ])
            employees = payslips.mapped('employee_id')
            for employee in employees:
                cert_find = cert_obj.search([('employee_id', '=', employee.id), ('year','=',item.year)], limit=1)
                if not cert_find:
                    cert_find = cert_obj.create({
                        'employee_id': employee.id,
                        'affidavit_id': item.id,
                        'year': item.year
                    })
                cert_find.run_line_detail()
                commands.append(cert_find.id)
            if commands:
                item.write({'bonus_cert_ids':[(6,False,commands)]})
            item.onchage_bonus_cert_ids()
