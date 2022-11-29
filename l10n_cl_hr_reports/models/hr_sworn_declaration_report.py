# -*- coding: utf-8 -*-
from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
import re,sys
import io
from odoo import api, fields, models
from xlwt import easyxf
import csv
import time
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)

class SwornDeclaration(models.TransientModel):
    _name = "hr.sworn.declaration.report"
    _description = "Sworn Declaration Report"


    date_to = fields.Date('Date To', required=True, default=lambda self: str(datetime.now()))
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))


    def export_xls(self):
        i = 1
        sheetName = 1
        workbook = xlwt.Workbook()

        n = 0
        c = 0
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour blue;''font: colour white, bold True;')
        filename = 'declJurada.csv'
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right',
        num_format_str='#,##0.00')
        formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
        worksheet = workbook.add_sheet("DJ"+str(self.date_to))
        sworn_declaration_recs = self.env['hr.affidavit'].search([('year','=',self.date_from)], limit=1)
        worksheet.col(0).width = 3000
        worksheet.col(1).width = 3000
        worksheet.col(2).width = 3000
        worksheet.col(3).width = 3000
        worksheet.col(4).width = 3000
        worksheet.col(5).width = 3000
        worksheet.col(6).width = 3000
        worksheet.col(7).width = 100
        worksheet.col(8).width = 100
        worksheet.col(9).width = 100
        worksheet.col(10).width = 100
        worksheet.col(11).width = 100
        worksheet.col(12).width = 100
        worksheet.col(13).width = 100
        worksheet.col(14).width = 100
        worksheet.col(15).width = 100
        worksheet.col(16).width = 100
        worksheet.col(17).width = 100
        worksheet.col(18).width = 100
        worksheet.col(19).width = 100
        worksheet.col(20).width = 800


        #Ejemplo Formato Simple
        #F1887 (Formulario 19 Columnas)
        for rec in sworn_declaration_recs:
            for cert in rec.bonus_cert_ids:
                worksheet.write(n, 0, cert.vat.replace('-','').replace('.','')[0:-1] or False, style)
                worksheet.write(n, 1, cert.vat.replace('-','').replace('.','')[-1:] or False, style)
                #Montos Anuales Actualizados
                worksheet.write(n, 2, str(int(round(cert.tot_ma_renta_imponible))), style)
                #Renta Total Neta Pagada (Art.42 N°1, Ley de la Renta)
                worksheet.write(n, 3, str(int(round(cert.tot_ma_impuesto_unico))), style)
                #Impuesto Único Retenido
                worksheet.write(n, 4, str(int(round(cert.tot_ma_may_ret_imp_sol))), style)
                #Mayor Retención Solicitada (Art.88 L.I.R)
                worksheet.write(n, 5, str(int(round(cert.tot_ma_renta_exenta))), style)
                #Renta Total Exenta y/o No Gravada
                worksheet.write(n, 6, str(int(round(cert.tot_ma_renta_no_gravada))), style)
                #Rebaja Por Zonas Extremas (Franquicia D.L. 889)
                worksheet.write(n, 7, str(int(round(cert.tot_ma_rebaja_zona_extrema))), style)
                worksheet.write(n, 8, cert.ene.upper(), style)
                worksheet.write(n, 9, cert.feb.upper(), style)
                worksheet.write(n, 10, cert.mar.upper(), style)
                worksheet.write(n, 11, cert.abr.upper(), style)
                worksheet.write(n, 12, cert.may.upper(), style)
                worksheet.write(n, 13, cert.jun.upper(), style)
                worksheet.write(n, 14, cert.jul.upper(), style)
                worksheet.write(n, 15, cert.ago.upper(), style)
                worksheet.write(n, 16, cert.sep.upper(), style)
                worksheet.write(n, 17, cert.oct.upper(), style)
                worksheet.write(n, 18, cert.nov.upper(), style)
                worksheet.write(n, 19, cert.dic.upper(), style)
                worksheet.write(n, 20, str(cert.name), style)

                n = n+1
        fp = io.BytesIO()
        workbook.save(fp)
        try:
            export_id = self.env['export.excel'].create({'excel_file':
        base64.encodestring(fp.getvalue()), 'file_name': filename})
        except:
            export_id = self.env['export.excel'].create({'excel_file':
        base64.b64encode(fp.getvalue()), 'file_name': filename})
            
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'export.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',

        }
        return True

class export_excel(models.TransientModel):
    _name= "export.excel"
    _description = "Export Excel"
    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File', size=64)
