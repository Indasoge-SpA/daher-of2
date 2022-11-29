from odoo import api, models, fields, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class hr_bonus_certificate(models.Model):
    _name = 'hr.bonus.certificate'
    _description = 'Certificado de sobre sueldos'

    name = fields.Char('Certificado N', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    vat = fields.Char('Rut', related='employee_id.identification_id')
    company_id = fields.Many2one('res.company', string='Compañia',
        default=lambda self: self.env.user.company_id)
    year = fields.Date('Año', required=True)
    bonus_cert_ids = fields.One2many('hr.bonus.certificate.line', 'bonus_cert_id', "Tabla calculada", readonly=True)
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)
    affidavit_id = fields.Many2one('hr.affidavit', 'Declaracion jurada en la que se informa')
    tot_pension_bruta = fields.Monetary('Total Pension Imponible', currency_field='currency_id')
    tot_cotizacion_prev = fields.Monetary('Total Cotizacion previsional', currency_field='currency_id')
    tot_renta_imponible = fields.Monetary('Total Renta Neta', currency_field='currency_id')
    tot_impuesto_retenido = fields.Monetary('Total Impuesto unico', currency_field='currency_id')
    tot_mayor_reten_imp_solicitado = fields.Monetary('Total Mayor retencion impuesto solicitado', currency_field='currency_id')
    tot_renta_exenta = fields.Monetary('Total Renta exenta', currency_field='currency_id')
    tot_renta_no_gravada = fields.Monetary('Total Renta no Gravada', currency_field='currency_id')
    tot_rebaja_zona_extrema = fields.Monetary('Total Rebaja zona extrema', currency_field='currency_id')
    tot_ma_renta_bruta = fields.Monetary('Total Montos ajustados renta bruta', currency_field='currency_id')
    tot_ma_renta_imponible = fields.Monetary('Total Montos ajustados renta neta', currency_field='currency_id')
    tot_ma_impuesto_unico = fields.Monetary('Total Montos ajustados impuesto unico', currency_field='currency_id')
    tot_ma_may_ret_imp_sol = fields.Monetary('Total Montos ajustados Mayor retencion impuesto solicitado',
        currency_field='currency_id')
    tot_ma_renta_exenta = fields.Monetary('Total Montos ajustados renta exenta', currency_field='currency_id')
    tot_ma_renta_no_gravada = fields.Monetary('Total Montos ajustados renta no gravada', currency_field='currency_id')
    tot_ma_rebaja_zona_extrema = fields.Monetary('Total Montos ajustados rebaja zona extrema', currency_field='currency_id')
    ene = fields.Char('E')
    feb = fields.Char('F')
    mar = fields.Char('M')
    abr = fields.Char('A')
    may = fields.Char('M')
    jun = fields.Char('J')
    jul = fields.Char('J')
    ago = fields.Char('A')
    sep = fields.Char('S')
    oct = fields.Char('O')
    nov = fields.Char('N')
    dic = fields.Char('D')


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.bonus.certificate') or '/'
        return super(hr_bonus_certificate, self).create(vals)


    def run_line_detail(self):
        meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        mesesdict = {}
        for mes in meses:
            mesesdict[mes[:3].lower()] = ''
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
            commands = [(2, line_id.id, False) for line_id in item.bonus_cert_ids]
            for month in range(12):
                from_day = item.year + relativedelta(months=month)
                to_day = item.year + relativedelta(months=month + 1, days=-1)
                payslips = self.env['hr.payslip'].search([
                    ('employee_id', '=', item.employee_id.id), ('state', '=', 'done'),
                    ('date_from', '>=', from_day),
                    ('date_to', '<=', to_day)
                ])
                if month == 1:
                    payslips = self.env['hr.payslip'].search([
                        ('employee_id', '=', item.employee_id.id), ('state', '=', 'done'),
                        ('date_from', '=', from_day),
                    ])
                detalle = {
                    'mes': meses[month],
                    'pension_bruta': 0,
                    'cotizacion_prev': 0,
                    'renta_imponible': 0,
                    'impuesto_retenido': 0,
                    'mayor_reten_imp_solicitado': 0,
                    'renta_exenta': 0,
                    'renta_no_gravada': 0,
                    'rebaja_zona_extrema': 0,
                    'fact_actualizacion': 0,
                    'ma_renta_bruta':0,
                    'ma_renta_imponible': 0,
                    'ma_impuesto_unico': 0,
                    'ma__may_ret_imp_sol': 0,
                    'ma_renta_exenta': 0,
                    'ma_renta_no_gravada': 0,
                    'ma_rebaja_zona_extrema': 0,
                    'contract_hours':''
                }
                if payslips:
                    lips_lines = payslips.mapped('line_ids')
                    detalle['pension_bruta'] = sum([x.total for x in lips_lines if x.salary_rule_id.code == 'SUELDO'])
                    detalle['cotizacion_prev'] = sum(
                        [x.total for x in lips_lines if x.salary_rule_id.category_id.code in ('PREV', 'SALUD')])
                    detalle['renta_imponible'] = sum(
                        [x.total for x in lips_lines if x.salary_rule_id.code == 'TRIBU'])
                    detalle['renta_exenta'] = sum(
                        [x.total for x in lips_lines if x.salary_rule_id.category_id.code == 'NOIMPO'])
                    detalle['renta_no_gravada'] = sum(
                        [x.total for x in lips_lines if x.salary_rule_id.code in ('COL', 'MOV', 'ASIGFAM')])
                    detalle['impuesto_retenido'] = sum(
                        [x.total for x in lips_lines if x.salary_rule_id.code == 'IMPUNI'])

                    #Buscaremos cada correccion. Aqui estamos tomando cualquier valor. Debemos pasar por cada mes del ano
                    factor = self.env['hr.indicadores'].search([('month', '=',month+1),('year','=',self.year.strftime('%Y'))], limit=1)
                    _logger.warning(factor.name)
                    if factor.ipc==0:
                        raise ValidationError("No existe factor de correccion monetaria para el mes de %s" % (meses[month]))
                    detalle['fact_actualizacion'] = factor.ipc
                    detalle['ma_renta_bruta'] = detalle['pension_bruta'] * factor.ipc
                    detalle['ma_renta_imponible'] = detalle['renta_imponible'] * factor.ipc
                    detalle['ma_impuesto_unico'] = detalle['impuesto_retenido'] * factor.ipc
                    detalle['ma_renta_exenta'] = detalle['renta_exenta'] * factor.ipc
                    detalle['ma_renta_no_gravada'] = detalle['renta_no_gravada'] * factor.ipc
                    detalle['contract_hours'] = 'c'
                    mesesdict[meses[month][:3].lower()] = detalle['contract_hours']
                    tot_pension_bruta += detalle['pension_bruta']
                    tot_cotizacion_prev += detalle['cotizacion_prev']
                    tot_renta_imponible += detalle['renta_imponible']
                    tot_impuesto_retenido += detalle['impuesto_retenido']
                    tot_mayor_reten_imp_solicitado += detalle['mayor_reten_imp_solicitado']
                    tot_renta_no_gravada += detalle['renta_no_gravada']
                    tot_renta_exenta += detalle['renta_exenta']
                    tot_rebaja_zona_extrema += detalle['rebaja_zona_extrema']
                    tot_ma_renta_bruta += detalle['ma_renta_bruta']
                    tot_ma_renta_imponible += detalle['ma_renta_imponible']
                    tot_ma_impuesto_unico += detalle['ma_impuesto_unico']
                    tot_ma_may_ret_imp_sol += detalle['ma__may_ret_imp_sol']
                    tot_ma_renta_exenta += detalle['ma_renta_exenta']
                    tot_ma_renta_no_gravada += detalle['ma_renta_no_gravada']
                    tot_ma_rebaja_zona_extrema += detalle['ma_rebaja_zona_extrema']
                commands.append((0, False, detalle))
            data = {
                'bonus_cert_ids': commands,
                'tot_pension_bruta': tot_pension_bruta,
                'tot_cotizacion_prev' : tot_cotizacion_prev,
                'tot_renta_imponible' : tot_renta_imponible,
                'tot_impuesto_retenido' : tot_impuesto_retenido,
                'tot_mayor_reten_imp_solicitado' : tot_mayor_reten_imp_solicitado,
                'tot_renta_exenta' : tot_renta_exenta,
                'tot_renta_no_gravada': tot_renta_no_gravada,
                'tot_rebaja_zona_extrema' : tot_rebaja_zona_extrema,
                'tot_ma_renta_bruta': tot_ma_renta_bruta,
                'tot_ma_renta_imponible' : tot_ma_renta_imponible,
                'tot_ma_impuesto_unico' : tot_ma_impuesto_unico,
                'tot_ma_may_ret_imp_sol' : tot_ma_may_ret_imp_sol,
                'tot_ma_renta_exenta' : tot_ma_renta_exenta,
                'tot_ma_renta_no_gravada': tot_ma_renta_no_gravada,
                'tot_ma_rebaja_zona_extrema' : tot_ma_rebaja_zona_extrema,
            }
            data.update(mesesdict)
            item.write(data)


class HrBonusCertificateLine(models.Model):
    _name = 'hr.bonus.certificate.line'
    _description = 'Detale certificado de sobre sueldos'

    mes = fields.Char('Mes')
    pension_bruta = fields.Monetary('Pension bruta', currency_field='currency_id')
    cotizacion_prev = fields.Monetary('Cotizacion previsional', currency_field='currency_id')
    renta_imponible = fields.Monetary('Renta neta', currency_field='currency_id')
    impuesto_retenido = fields.Monetary('Impuesto unico', currency_field='currency_id')
    mayor_reten_imp_solicitado = fields.Monetary('Mayor retencion impuesto solicitado', currency_field='currency_id')
    renta_exenta = fields.Monetary('Renta exenta', currency_field='currency_id')
    renta_no_gravada = fields.Monetary('Renta no gravada', currency_field='currency_id')
    rebaja_zona_extrema = fields.Monetary('Rebaja zona extrema', currency_field='currency_id')
    fact_actualizacion = fields.Float('Factor de actualizacion', digits=(16, 3))
    ma_renta_bruta = fields.Monetary('Montos ajustados renta bruta', currency_field='currency_id')
    ma_renta_imponible = fields.Monetary('Montos ajustados renta imponible', currency_field='currency_id')
    ma_impuesto_unico = fields.Monetary('Montos ajustados impuesto unico', currency_field='currency_id')
    ma__may_ret_imp_sol = fields.Monetary('Montos ajustados Mayor retencion impuesto solicitado', currency_field='currency_id')
    ma_renta_exenta = fields.Monetary('Montos ajustados renta exenta', currency_field='currency_id')
    ma_renta_no_gravada = fields.Monetary('Montos ajustados renta no gravada', currency_field='currency_id')
    ma_rebaja_zona_extrema = fields.Monetary('Montos ajustados rebaja zona extrema', currency_field='currency_id')
    bonus_cert_id = fields.Many2one('hr.bonus.certificate', 'Encabezado')
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)
    contract_hours = fields.Selection([('c', 'Completo'), ('p', 'Parcial')], 'Jornada contractual')
