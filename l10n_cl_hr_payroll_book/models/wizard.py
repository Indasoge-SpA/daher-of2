# -*- coding: utf-8 -*-
from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
import re,sys
import io
from odoo import api, fields, models, _
from xlwt import easyxf
import csv
import time
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class PayrollBoook(models.TransientModel):
    _name = "hr.payroll.book"
    _description = "Payroll Book"

    date_to = fields.Date('Date To', required=True, default=lambda self: str(datetime.now()))
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))

    @api.model
    def get_tramo_asignacion_familiar(self, payslip, valor):
        try:
            if payslip.contract_id.carga_familiar != 0 and payslip.indicadores_id.asignacion_familiar_tercer >= payslip.contract_id.wage and payslip.contract_id.pension is False:
                if payslip.indicadores_id.asignacion_familiar_primer >= valor:
                    return 'A'
                elif payslip.indicadores_id.asignacion_familiar_segundo  >= valor:
                    return 'B'
                elif payslip.indicadores_id.asignacion_familiar_tercer  >= valor:
                    return 'C'
            else:
                return 'S'
        except:
            return 'S'


    @api.model
    def get_dias_trabajados(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'WORK100':
                        worked_days = line.number_of_days
        return worked_days

    @api.model
    def get_dias_licencia(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'Licencia':
                        worked_days = line.number_of_days
        return worked_days

    @api.model
    def get_dias_vacaciones(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'Vacaciones':
                        worked_days = line.number_of_days
        return worked_days


    def get_payslip_lines_value(self, obj, rule):
        try:
            lineas = self.env['hr.payslip.line']
            detail = lineas.search([('slip_id','=',obj.id),('code','=',rule)])
            return detail.amount
        except:
            return '0'

        
    def get_cotizaciones(self, obj):
        #Corresponde a la sumatoria de los valores de los siguientes campos: cód 3141, cód 3143, cód
        #3144, cód 3146, cód 3151, cód 3154, cód 3155, cód 3156, cód 3157 y cód 3158.
        result = 0
        lineas = self.env['hr.payslip.line']
        result = lineas.search([('slip_id','=',obj.id),('code','=','PREV')]).amount or 0
        result = result + (lineas.search([('slip_id','=',obj.id),('code','=','SECE')]).amount or 0)
        result = result + (lineas.search([('slip_id','=',obj.id),('code','=','SALUD')]).amount or 0)
        result = result + (lineas.search([('slip_id','=',obj.id),('code','=','ADISA')]).amount or 0)
        return result

    def export_xls(self):
        i = 1
        sheetName = 1
        workbook = xlwt.Workbook()

        n = 1
        c = 0
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour blue;''font: colour white, bold True;')
        filename = 'LRE'+str(self.date_to)+'.csv'
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right',
        num_format_str='#,##0.00')
        formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
        worksheet = workbook.add_sheet("LRE"+str(self.date_to))

        payslip_recs = self.env['hr.payslip'].search([('date_from','>=',self.date_from),
        ('date_to', '<=', self.date_to),
        ('state','not in',['draft','cancel']),
        ('company_id' ,'=',self.env.user.company_id.id)])


        for column_index in range(0,144):
            worksheet.col(column_index).width = 5000
        worksheet.write(n-1, 0, 'Rut trabajador(1101)', style1)
        worksheet.write(n-1, 1, 'Fecha inicio contrato(1102)', style1)
        worksheet.write(n-1, 2, 'Fecha término de contrato(1103)', style1)
        worksheet.write(n-1, 3, 'Causal término de contrato(1104)', style1)
        worksheet.write(n-1, 4, 'Región prestación de servicios(1105)', style1)
        worksheet.write(n-1, 5, 'Comuna prestación de servicios(1106)', style1)
        worksheet.write(n-1, 6, 'Tipo impuesto a la renta(1170)', style1)
        worksheet.write(n-1, 7, 'Técnico extranjero exención cot. previsionales(1146)', style1)
        worksheet.write(n-1, 8, 'Código tipo de jornada(1107)', style1)
        worksheet.write(n-1, 9, 'Persona con Discapacidad - Pensionado por Invalidez(1108)', style1)
        worksheet.write(n-1, 10, 'Pensionado por vejez(1109)', style1)
        worksheet.write(n-1, 11, 'AFP(1141)', style1)
        worksheet.write(n-1, 12, 'IPS (ExINP)(1142)', style1)
        worksheet.write(n-1, 13, 'FONASA - ISAPRE(1143)', style1)
        worksheet.write(n-1, 14, 'AFC(1151)', style1)
        worksheet.write(n-1, 15, 'CCAF(1110)', style1)
        worksheet.write(n-1, 16, 'Org. administrador ley 16.744(1152)', style1)
        worksheet.write(n-1, 17, 'Nro cargas familiares legales autorizadas(1111)', style1)
        worksheet.write(n-1, 18, 'Nro de cargas familiares maternales(1112)', style1)
        worksheet.write(n-1, 19, 'Nro de cargas familiares invalidez(1113)', style1)
        worksheet.write(n-1, 20, 'Tramo asignación familiar(1114)', style1)
        worksheet.write(n-1, 21, 'Rut org sindical 1(1171)', style1)
        worksheet.write(n-1, 22, 'Rut org sindical 2(1172)', style1)
        worksheet.write(n-1, 23, 'Rut org sindical 3(1173)', style1)
        worksheet.write(n-1, 24, 'Rut org sindical 4(1174)', style1)
        worksheet.write(n-1, 25, 'Rut org sindical 5(1175)', style1)
        worksheet.write(n-1, 26, 'Rut org sindical 6(1176)', style1)
        worksheet.write(n-1, 27, 'Rut org sindical 7(1177)', style1)
        worksheet.write(n-1, 28, 'Rut org sindical 8(1178)', style1)
        worksheet.write(n-1, 29, 'Rut org sindical 9(1179)', style1)
        worksheet.write(n-1, 30, 'Rut org sindical 10(1180)', style1)
        worksheet.write(n-1, 31, 'Nro días trabajados en el mes(1115)', style1)
        worksheet.write(n-1, 32, 'Nro días de licencia médica en el mes(1116)', style1)
        worksheet.write(n-1, 33, 'Nro días de vacaciones en el mes(1117)', style1)
        worksheet.write(n-1, 34, 'Subsidio trabajador joven(1118)', style1)
        worksheet.write(n-1, 35, 'Puesto Trabajo Pesado(1154)', style1)
        worksheet.write(n-1, 36, 'APVI(1155)', style1)
        worksheet.write(n-1, 37, 'APVC(1157)', style1)
        worksheet.write(n-1, 38, 'Indemnización a todo evento(1131)', style1)
        worksheet.write(n-1, 39, 'Tasa indemnización a todo evento(1132)', style1)
        worksheet.write(n-1, 40, 'Sueldo(2101)', style1)
        worksheet.write(n-1, 41, 'Sobresueldo(2102)', style1)
        worksheet.write(n-1, 42, 'Comisiones(2103)', style1)
        worksheet.write(n-1, 43, 'Semana corrida(2104)', style1)
        worksheet.write(n-1, 44, 'Participación(2105)', style1)
        worksheet.write(n-1, 45, 'Gratificación(2106)', style1)
        worksheet.write(n-1, 46, 'Recargo 30% día domingo(2107)', style1)
        worksheet.write(n-1, 47, 'Remun. variable pagada en vacaciones(2108)', style1)
        worksheet.write(n-1, 48, 'Remun. variable pagada en clausura(2109)', style1)
        worksheet.write(n-1, 49, 'Aguinaldo(2110)', style1)
        worksheet.write(n-1, 50, 'Bonos u otras remun. fijas mensuales(2111)', style1)
        worksheet.write(n-1, 51, 'Tratos(2112)', style1)
        worksheet.write(n-1, 52, 'Bonos u otras remun. variables mensuales o superiores a un mes(2113)', style1)
        worksheet.write(n-1, 53, 'Ejercicio opción no pactada en contrato(2114)', style1)
        worksheet.write(n-1, 54, 'Beneficios en especie constitutivos de remun(2115)', style1)
        worksheet.write(n-1, 55, 'Remuneraciones bimestrales(2116)', style1)
        worksheet.write(n-1, 56, 'Remuneraciones trimestrales(2117)', style1)
        worksheet.write(n-1, 57, 'Remuneraciones cuatrimestral(2118)', style1)
        worksheet.write(n-1, 58, 'Remuneraciones semestrales(2119)', style1)
        worksheet.write(n-1, 59, 'Remuneraciones anuales(2120)', style1)
        worksheet.write(n-1, 60, 'Participación anual(2121)', style1)
        worksheet.write(n-1, 61, 'Gratificación anual(2122)', style1)
        worksheet.write(n-1, 62, 'Otras remuneraciones superiores a un mes(2123)', style1)
        worksheet.write(n-1, 63, 'Pago por horas de trabajo sindical(2124)', style1)
        worksheet.write(n-1, 64, 'Sueldo empresarial (2161)', style1)
        worksheet.write(n-1, 65, 'Subsidio por incapacidad laboral por licencia médica(2201)', style1)
        worksheet.write(n-1, 66, 'Beca de estudio(2202)', style1)
        worksheet.write(n-1, 67, 'Gratificaciones de zona(2203)', style1)
        worksheet.write(n-1, 68, 'Otros ingresos no constitutivos de renta(2204)', style1)
        worksheet.write(n-1, 69, 'Colación(2301)', style1)
        worksheet.write(n-1, 70, 'Movilización(2302)', style1)
        worksheet.write(n-1, 71, 'Viáticos(2303)', style1)
        worksheet.write(n-1, 72, 'Asignación de pérdida de caja(2304)', style1)
        worksheet.write(n-1, 73, 'Asignación de desgaste herramienta(2305)', style1)
        worksheet.write(n-1, 74, 'Asignación familiar legal(2311)', style1)
        worksheet.write(n-1, 75, 'Gastos por causa del trabajo(2306)', style1)
        worksheet.write(n-1, 76, 'Gastos por cambio de residencia(2307)', style1)
        worksheet.write(n-1, 77, 'Sala cuna(2308)', style1)
        worksheet.write(n-1, 78, 'Asignación trabajo a distancia o teletrabajo(2309)', style1)
        worksheet.write(n-1, 79, 'Depósito convenido hasta UF 900(2347)', style1)
        worksheet.write(n-1, 80, 'Alojamiento por razones de trabajo(2310)', style1)
        worksheet.write(n-1, 81, 'Asignación de traslación(2312)', style1)
        worksheet.write(n-1, 82, 'Indemnización por feriado legal(2313)', style1)
        worksheet.write(n-1, 83, 'Indemnización años de servicio(2314)', style1)
        worksheet.write(n-1, 84, 'Indemnización sustitutiva del aviso previo(2315)', style1)
        worksheet.write(n-1, 85, 'Indemnización fuero maternal(2316)', style1)
        worksheet.write(n-1, 86, 'Pago indemnización a todo evento(2331)', style1)
        worksheet.write(n-1, 87, 'Indemnizaciones voluntarias tributables(2417)', style1)
        worksheet.write(n-1, 88, 'Indemnizaciones contractuales tributables(2418)', style1)
        worksheet.write(n-1, 89, 'Cotización obligatoria previsional (AFP o IPS)(3141)', style1)
        worksheet.write(n-1, 90, 'Cotización obligatoria salud 7%(3143)', style1)
        worksheet.write(n-1, 91, 'Cotización voluntaria para salud(3144)', style1)
        worksheet.write(n-1, 92, 'Cotización AFC - trabajador(3151)', style1)
        worksheet.write(n-1, 93, 'Cotizaciones técnico extranjero para seguridad social fuera de Chile(3146)', style1)
        worksheet.write(n-1, 94, 'Descuento depósito convenido hasta UF 900 anual(3147)', style1)
        worksheet.write(n-1, 95, 'Cotización APVi Mod A(3155)', style1)
        worksheet.write(n-1, 96, 'Cotización APVi Mod B hasta UF50(3156)', style1)
        worksheet.write(n-1, 97, 'Cotización APVc Mod A(3157)', style1)
        worksheet.write(n-1, 98, 'Cotización APVc Mod B hasta UF50(3158)', style1)
        worksheet.write(n-1, 99, 'Impuesto retenido por remuneraciones(3161)', style1)
        worksheet.write(n-1, 100, 'Impuesto retenido por indemnizaciones(3162)', style1)
        worksheet.write(n-1, 101, 'Mayor retención de impuestos solicitada por el trabajador(3163)', style1)
        worksheet.write(n-1, 102, 'Impuesto retenido por reliquidación remun. devengadas otros períodos(3164)', style1)
        worksheet.write(n-1, 103, 'Diferencia impuesto reliquidación remun. devengadas en este período(3165)', style1)
        worksheet.write(n-1, 104, 'Retención préstamo clase media 2020 (Ley 21.252) (3166)', style1)
        worksheet.write(n-1, 105, 'Rebaja zona extrema DL 889 (3167)', style1)
        worksheet.write(n-1, 106, 'Cuota sindical 1(3171)', style1)
        worksheet.write(n-1, 107, 'Cuota sindical 2(3172)', style1)
        worksheet.write(n-1, 108, 'Cuota sindical 3(3173)', style1)
        worksheet.write(n-1, 109, 'Cuota sindical 4(3174)', style1)
        worksheet.write(n-1, 110, 'Cuota sindical 5(3175)', style1)
        worksheet.write(n-1, 111, 'Cuota sindical 6(3176)', style1)
        worksheet.write(n-1, 112, 'Cuota sindical 7(3177)', style1)
        worksheet.write(n-1, 113, 'Cuota sindical 8(3178)', style1)
        worksheet.write(n-1, 114, 'Cuota sindical 9(3179)', style1)
        worksheet.write(n-1, 115, 'Cuota sindical 10(3180)', style1)
        worksheet.write(n-1, 116, 'Crédito social CCAF(3110)', style1)
        worksheet.write(n-1, 117, 'Cuota vivienda o educación(3181)', style1)
        worksheet.write(n-1, 118, 'Crédito cooperativas de ahorro(3182)', style1)
        worksheet.write(n-1, 119, 'Otros descuentos autorizados y solicitados por el trabajador(3183)', style1)
        worksheet.write(n-1, 120, 'Cotización adicional trabajo pesado - trabajador(3154)', style1)
        worksheet.write(n-1, 121, 'Donaciones culturales y de reconstrucción(3184)', style1)
        worksheet.write(n-1, 122, 'Otros descuentos(3185)', style1)
        worksheet.write(n-1, 123, 'Pensiones de alimentos(3186)', style1)
        worksheet.write(n-1, 124, 'Descuento mujer casada(3187)', style1)
        worksheet.write(n-1, 125, 'Descuentos por anticipos y préstamos(3188)', style1)
        worksheet.write(n-1, 126, 'AFC - Aporte empleador(4151)', style1)
        worksheet.write(n-1, 127, 'Aporte empleador seguro accidentes del trabajo y Ley SANNA(4152)', style1)
        worksheet.write(n-1, 128, 'Aporte empleador indemnización a todo evento(4131)', style1)
        worksheet.write(n-1, 129, 'Aporte adicional trabajo pesado - empleador(4154)', style1)
        worksheet.write(n-1, 130, 'Aporte empleador seguro invalidez y sobrevivencia(4155)', style1)
        worksheet.write(n-1, 131, 'APVC - Aporte Empleador(4157)', style1)
        worksheet.write(n-1, 132, 'Total haberes(5201)', style1)
        worksheet.write(n-1, 133, 'Total haberes imponibles y tributables(5210)', style1)
        worksheet.write(n-1, 134, 'Total haberes imponibles no tributables(5220)', style1)
        worksheet.write(n-1, 135, 'Total haberes no imponibles y no tributables(5230)', style1)
        worksheet.write(n-1, 136, 'Total haberes no imponibles y tributables(5240)', style1)
        worksheet.write(n-1, 137, 'Total descuentos(5301)', style1)
        worksheet.write(n-1, 138, 'Total descuentos impuestos a las remuneraciones(5361)', style1)
        worksheet.write(n-1, 139, 'Total descuentos impuestos por indemnizaciones(5362)', style1)
        worksheet.write(n-1, 140, 'Total descuentos por cotizaciones del trabajador(5341)', style1)
        worksheet.write(n-1, 141, 'Total otros descuentos(5302)', style1)
        worksheet.write(n-1, 142, 'Total aportes empleador(5410)', style1)
        worksheet.write(n-1, 143, 'Total líquido(5501)', style1)
        worksheet.write(n-1, 144, 'Total indemnizaciones(5502)', style1)
        worksheet.write(n-1, 145, 'Total indemnizaciones tributables(5564)', style1)
        worksheet.write(n-1, 146, 'Total indemnizaciones no tributables(5565)', style1)
        for rec in payslip_recs:
            #Any Validation
            if rec.employee_id:
                if not rec.employee_id.address_id:
                    raise UserError(_("Please select company related to %s" % (rec.employee_id.name)))
                if not rec.employee_id.address_id.city_id:
                    raise UserError(_("Please select the commune for the company related to %s" % (rec.employee_id.name)))
                if not rec.employee_id.address_id.city_id.code:
                    raise UserError(_("Please select the commune code for the company related to %s" % (rec.employee_id.name)))
                if not rec.contract_id.afp_id and not rec.contract_id.afp_id.codigo:
                    raise UserError(_("Please check the AFP related to %s" % (rec.employee_id.name)))
                if not rec.contract_id.isapre_id and not rec.contract_id.isapre_id.codigo:
                    raise UserError(_("Please check the ISAPRE related to %s" % (rec.employee_id.name)))

                #Rut trabajador(1101) Obligatorio Formato 19745276-5
                worksheet.write(n, 0, rec.employee_id.identification_id.replace('.',''), style)
                #Fecha inicio contrato(1102) Obligatorio Formato 02-11-21
                worksheet.write(n, 1, rec.contract_id.date_start.strftime("%d/%m/%Y"), style)
                #Fecha término de contrato(1103)
                worksheet.write(n, 2, rec.contract_id.date_end or '', style)
                #Causal término de contrato(1104)
                worksheet.write(n, 3, '', style)
                #Región prestación de servicios(1105) Obligatorio TODO Not only Santiago
                worksheet.write(n, 4, int(rec.employee_id.address_id.state_id.code[2:4]), style)
                #Comuna prestación de servicios(1106) Obligatorio
                worksheet.write(n, 5, int(rec.employee_id.address_id.city_id.code.replace('CL','')) or 13114, style)
                #Tipo impuesto a la renta(1170) Obligatorio
                worksheet.write(n, 6, 1, style)
                #Técnico extranjero exención cot. previsionales(1146)
                worksheet.write(n, 7, 0, style)
                #Código tipo de jornada(1107) Obligatorio
                worksheet.write(n, 8, 101, style)
                #Persona con Discapacidad - Pensionado por Invalidez(1108)
                worksheet.write(n, 9, 0, style)
                #Pensionado por vejez(1109) Obligatorio 0 Falso 1 True
                worksheet.write(n, 10, 0, style)
                #AFP(1141) Obligatorio
                worksheet.write(n, 11, int(rec.contract_id.afp_id.codigo_afp_lre) or '', style)
                #IPS (ExINP)(1142)
                worksheet.write(n, 12, 0, style)
                #FONASA - ISAPRE(1143) Obligatorio
                worksheet.write(n, 13, int(rec.contract_id.isapre_id.codigo_isapre_lre) or '', style)
                #AFC(1151) Obligatorio
                worksheet.write(n, 14, 1, style)
                #CCAF(1110) Obligatorio Solo si tiene CCA
                worksheet.write(n, 15, 1 if self.get_payslip_lines_value(rec,'CAJACOMP')>0 else 0, style)
                #Org. administrador ley 16.744(1152) Obligatorio
                worksheet.write(n, 16, rec.indicadores_id.mutualidad_id.codigo if rec.indicadores_id.mutual_seguridad_bool else 0, style)
                #Nro cargas familiares legales autorizadas(1111) Obligatorio
                worksheet.write(n, 17, rec.contract_id.carga_familiar, style)
                #Nro de cargas familiares maternales(1112)
                worksheet.write(n, 18, rec.contract_id.carga_familiar_maternal, style)
                #Nro de cargas familiares invalidez(1113)
                worksheet.write(n, 19, rec.contract_id.carga_familiar_invalida, style)
                #Tramo asignación familiar(1114) Obligatorio
                worksheet.write(n, 20, self.get_tramo_asignacion_familiar(rec, self.get_payslip_lines_value(rec,'TOTIM')), style)
                #Rut org sindical 1(1171)
                worksheet.write(n, 21, '', style)
                #Rut org sindical 2(1172)
                worksheet.write(n, 22, '', style)
                #Rut org sindical 3(1173)
                worksheet.write(n, 23, '', style)
                #Rut org sindical 4(1174)
                worksheet.write(n, 24, '', style)
                #Rut org sindical 5(1175)
                worksheet.write(n, 25, '', style)
                #Rut org sindical 6(1176)
                worksheet.write(n, 26, '', style)
                #Rut org sindical 7(1177)
                worksheet.write(n, 27, '', style)
                #Rut org sindical 8(1178)
                worksheet.write(n, 28, '', style)
                #Rut org sindical 9(1179)
                worksheet.write(n, 29, '', style)
                #Rut org sindical 10(1180)
                worksheet.write(n, 30, '', style)
                #Nro días trabajados en el mes(1115) Obligatorio
                worksheet.write(n, 31, int(self.get_dias_trabajados(rec and rec[0] or False)), style)
                #Nro días de licencia médica en el mes(1116)
                worksheet.write(n, 32, int(self.get_dias_licencia(rec and rec[0] or False)), style)
                #Nro días de vacaciones en el mes(1117)
                worksheet.write(n, 33, int(self.get_dias_vacaciones(rec and rec[0] or False)), style)
                #Subsidio trabajador joven(1118) Obligatorio
                worksheet.write(n, 34, 0, style)
                #Puesto Trabajo Pesado(1154)
                worksheet.write(n, 35, '', style)
                #APVI(1155)
                worksheet.write(n, 36, 0, style)
                #APVC(1157)
                worksheet.write(n, 37, 0, style)
                #Indemnización a todo evento(1131)
                worksheet.write(n, 38, 0, style)
                #Tasa indemnización a todo evento(1132)
                worksheet.write(n, 39, '', style)
                #Sueldo(2101) Obligatorio
                worksheet.write(n, 40, self.get_payslip_lines_value(rec,'SUELDO'), style)
                #Sobresueldo(2102)
                worksheet.write(n, 41, 0, style)
                #Comisiones(2103) Obligatorio
                worksheet.write(n, 42, self.get_payslip_lines_value(rec,'COMI'), style)
                #Semana corrida(2104) Obligatorio TODO
                worksheet.write(n, 43, 0, style)
                #Participación(2105)
                worksheet.write(n, 44, '', style)
                #Gratificación(2106) Obligatorio
                worksheet.write(n, 45, self.get_payslip_lines_value(rec,'GRAT'), style)
                #Recargo 30% día domingo(2107)
                worksheet.write(n, 46, 0, style)
                #Remun. variable pagada en vacaciones(2108)
                worksheet.write(n, 47, '', style)
                #Remun. variable pagada en clausura(2109)
                worksheet.write(n, 48, '', style)
                #Aguinaldo(2110)
                worksheet.write(n, 49, self.get_payslip_lines_value(rec,'AGUI'), style)
                #Bonos u otras remun. fijas mensuales(2111)
                worksheet.write(n, 50, self.get_payslip_lines_value(rec,'BONO') or '', style)
                #Tratos(2112)
                worksheet.write(n, 51, '', style)
                #Bonos u otras remun. variables mensuales o superiores a un mes(2113) TODO
                worksheet.write(n, 52, 0, style)
                #Ejercicio opción no pactada en contrato(2114)
                worksheet.write(n, 53, '', style)
                #Beneficios en especie constitutivos de remun(2115)
                worksheet.write(n, 54, '', style)
                #Remuneraciones bimestrales(2116)
                worksheet.write(n, 55, '', style)
                #Remuneraciones trimestrales(2117)
                worksheet.write(n, 56, '', style)
                #Remuneraciones cuatrimestral(2118)
                worksheet.write(n, 57, '', style)
                #Remuneraciones semestrales(2119)
                worksheet.write(n, 58, '', style)
                #Remuneraciones anuales(2120)
                worksheet.write(n, 59, '', style)
                #Participación anual(2121)
                worksheet.write(n, 60, '', style)
                #Gratificación anual(2122)
                worksheet.write(n, 61, '', style)
                #Otras remuneraciones superiores a un mes(2123)
                worksheet.write(n, 62, '', style)
                #Pago por horas de trabajo sindical(2124)
                worksheet.write(n, 63, '', style)
                #2161: Sueldo empresarial (Haber Imponible y Tributable)
                worksheet.write(n, 64, self.get_payslip_lines_value(rec,'TOTIM') if rec.contract_id.type_id.name == 'Sueldo Empresarial' else 0, style)
                #Subsidio por incapacidad laboral por licencia médica(2201)
                worksheet.write(n, 65, '', style)
                #Beca de estudio(2202)
                worksheet.write(n, 66, '', style)
                #Gratificaciones de zona(2203)
                worksheet.write(n, 67, '', style)
                #Otros ingresos no constitutivos de renta(2204)
                worksheet.write(n, 68, '', style)
                #Colación(2301)
                worksheet.write(n, 69, self.get_payslip_lines_value(rec,'COL'), style)
                #Movilización(2302)
                worksheet.write(n, 70, self.get_payslip_lines_value(rec,'MOV'), style)
                #Viáticos(2303)
                worksheet.write(n, 71, self.get_payslip_lines_value(rec,'VIASAN'), style)
                #Asignación de pérdida de caja(2304)
                worksheet.write(n, 72, 0, style)
                #Asignación de desgaste herramienta(2305)
                worksheet.write(n, 73, 0, style)
                #Asignación familiar legal(2311) Obligatorio
                worksheet.write(n, 74, self.get_payslip_lines_value(rec,'ASIGFAM'), style)
                #Gastos por causa del trabajo(2306)
                worksheet.write(n, 75, '', style)
                #Gastos por cambio de residencia(2307)
                worksheet.write(n, 76, '', style)
                #Sala cuna(2308)
                worksheet.write(n, 77, '', style)
                #Asignación trabajo a distancia o teletrabajo(2309)
                worksheet.write(n, 78, '', style)
                #Depósito convenido hasta UF 900(2347)
                worksheet.write(n, 79, '', style)
                #Alojamiento por razones de trabajo(2310)
                worksheet.write(n, 80, '', style)
                #Asignación de traslación(2312)
                worksheet.write(n, 81, '', style)
                #Indemnización por feriado legal(2313)
                worksheet.write(n, 82, 0, style)
                #Indemnización años de servicio(2314)
                worksheet.write(n, 83, 0, style)
                #Indemnización sustitutiva del aviso previo(2315)
                worksheet.write(n, 84, 0, style)
                #Indemnización fuero maternal(2316)
                worksheet.write(n, 85, 0, style)
                #Pago indemnización a todo evento(2331)
                worksheet.write(n, 86, 0, style)
                #Indemnizaciones voluntarias tributables(2417)
                worksheet.write(n, 87, 0, style)
                #Indemnizaciones contractuales tributables(2418)
                worksheet.write(n, 88, 0, style)
                #Cotización obligatoria previsional (AFP o IPS)(3141) Obligatorio
                worksheet.write(n, 89, self.get_payslip_lines_value(rec,'PREV'), style)
                #Cotización obligatoria salud 7%(3143) Obligatorio
                worksheet.write(n, 90, self.get_payslip_lines_value(rec,'SALUD'), style)
                #Cotización voluntaria para salud(3144)
                worksheet.write(n, 91, self.get_payslip_lines_value(rec,'ADISA'), style)
                #Cotización AFC - trabajador(3151) Obligatorio
                worksheet.write(n, 92, int(self.get_payslip_lines_value(rec,'SECE')) + int(self.get_payslip_lines_value(rec,'SECEMP')) , style)
                #Cotizaciones técnico extranjero para seguridad social fuera de Chile(3146)
                worksheet.write(n, 93, '', style)
                #Descuento depósito convenido hasta UF 900 anual(3147)
                worksheet.write(n, 94, 0, style)
                #Cotización APVi Mod A(3155)
                worksheet.write(n, 95, 0, style)
                #Cotización APVi Mod B hasta UF50(3156)
                worksheet.write(n, 96, 0, style)
                #Cotización APVc Mod A(3157)
                worksheet.write(n, 97, '', style)
                #Cotización APVc Mod B hasta UF50(3158)
                worksheet.write(n, 98, '', style)
                #Impuesto retenido por remuneraciones(3161)
                worksheet.write(n, 99, round(self.get_payslip_lines_value(rec,'IMPUNI')), style)
                #Impuesto retenido por indemnizaciones(3162)
                worksheet.write(n, 100, '', style)
                #Mayor retención de impuestos solicitada por el trabajador(3163)
                worksheet.write(n, 101, 0, style)
                #Impuesto retenido por reliquidación remun. devengadas otros períodos(3164)
                worksheet.write(n, 102, '', style)
                #Diferencia impuesto reliquidación remun. devengadas en este período(3165)
                worksheet.write(n, 103, '', style)
                #3166: Retención préstamo clase media 2020 (Ley 21.252)(Descuento)
                worksheet.write(n, 104, self.get_payslip_lines_value(rec,'RPCM'), style)
                #3167: Rebaja zona extrema DL 889 (Descuento)
                worksheet.write(n, 105, self.get_payslip_lines_value(rec,'RZE'), style)
                #Cuota sindical 1(3171)
                worksheet.write(n, 106, '', style)
                #Cuota sindical 2(3172)
                worksheet.write(n, 107, '', style)
                #Cuota sindical 3(3173)
                worksheet.write(n, 108, '', style)
                #Cuota sindical 4(3174)
                worksheet.write(n, 109, '', style)
                #Cuota sindical 5(3175)
                worksheet.write(n, 110, '', style)
                #Cuota sindical 6(3176)
                worksheet.write(n, 111, '', style)
                #Cuota sindical 7(3177)
                worksheet.write(n, 112, '', style)
                #Cuota sindical 8(3178)
                worksheet.write(n, 113, '', style)
                #Cuota sindical 9(3179)
                worksheet.write(n, 114, '', style)
                #Cuota sindical 10(3180)
                worksheet.write(n, 115, '', style)
                #Crédito social CCAF(3110) TODO CHECK
                worksheet.write(n, 116, self.get_payslip_lines_value(rec,'PCCAF'), style)
                #Cuota vivienda o educación(3181)
                worksheet.write(n, 117, '', style)
                #Crédito cooperativas de ahorro(3182)
                worksheet.write(n, 118, '', style)
                #Otros descuentos autorizados y solicitados por el trabajador(3183)
                worksheet.write(n, 119, 0, style)
                #Cotización adicional trabajo pesado - trabajador(3154)
                worksheet.write(n, 120, '', style)
                #Donaciones culturales y de reconstrucción(3184)
                worksheet.write(n, 121, '', style)
                #Otros descuentos(3185)
                worksheet.write(n, 122, self.get_payslip_lines_value(rec,'TOD'), style)
                #Pensiones de alimentos(3186)
                worksheet.write(n, 123, '', style)
                #Descuento mujer casada(3187)
                worksheet.write(n, 124, '', style)
                #Descuentos por anticipos y préstamos(3188)
                worksheet.write(n, 125, int(self.get_payslip_lines_value(rec,'ASUE')) + int(self.get_payslip_lines_value(rec,'PRES')) , style)
                #AFC - Aporte empleador(4151) Obligatorio
                worksheet.write(n, 126, self.get_payslip_lines_value(rec,'SECEEMP'), style)
                #Aporte empleador seguro accidentes del trabajo y Ley SANNA(4152) Obligatorio
                worksheet.write(n, 127, round(self.get_payslip_lines_value(rec,'ISL')), style)
                #Aporte empleador indemnización a todo evento(4131)
                worksheet.write(n, 128, '', style)
                #Aporte adicional trabajo pesado - empleador(4154)
                worksheet.write(n, 129, '', style)
                #Aporte empleador seguro invalidez y sobrevivencia(4155) Obligatorio
                worksheet.write(n, 130, self.get_payslip_lines_value(rec,'SIS'), style)
                #APVC - Aporte Empleador(4157)
                worksheet.write(n, 131, '', style)
                #Total haberes(5201) Obligatorio
                worksheet.write(n, 132, self.get_payslip_lines_value(rec,'HAB'), style)
                #Total haberes imponibles y tributables(5210) Obligatorio
                worksheet.write(n, 133, self.get_payslip_lines_value(rec,'TOTIM'), style)
                #Total haberes imponibles no tributables(5220)
                worksheet.write(n, 134, 0, style)
                #Total haberes no imponibles y no tributables(5230) Obligatorio
                worksheet.write(n, 135, self.get_payslip_lines_value(rec,'TOTNOI'), style)
                #Total haberes no imponibles y tributables(5240)
                worksheet.write(n, 136, 0, style)
                #Total descuentos(5301) Obligatorio
                worksheet.write(n, 137, self.get_payslip_lines_value(rec,'TDE'), style)
                #Total descuentos impuestos a las remuneraciones(5361)
                worksheet.write(n, 138, round(self.get_payslip_lines_value(rec,'IMPUNI')), style)
                #Total descuentos impuestos por indemnizaciones(5362)
                worksheet.write(n, 139, '', style)
                #Total descuentos por cotizaciones del trabajador(5341) Obligatorio
                worksheet.write(n, 140, self.get_cotizaciones(rec), style)
                #Total otros descuentos(5302) TODO
                worksheet.write(n, 141, self.get_payslip_lines_value(rec,'TOD'), style)
                #Total aportes empleador(5410) Obligatorio
                worksheet.write(n, 142, self.get_payslip_lines_value(rec,'APORTE'), style)
                #Total líquido(5501) Obligatorio
                worksheet.write(n, 143, self.get_payslip_lines_value(rec,'LIQ'), style)
                #Total indemnizaciones(5502)
                worksheet.write(n, 144, 0, style)
                #Total indemnizaciones tributables(5564)
                worksheet.write(n, 145, 0, style)
                #Total indemnizaciones no tributables(5565)
                worksheet.write(n, 146, 0, style)
                n = n+1
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['export.book.excel'].create({'excel_file':
        base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'export.book.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',

        }
        return True

class export_excel(models.TransientModel):
    _name= "export.book.excel"
    _description = "Export Excel"
    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File', size=64)
