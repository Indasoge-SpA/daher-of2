from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

CURRENCY_SELECTION = [
    ('uf', 'UF'),
    ('clp', 'CLP')]

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    afp_id = fields.Many2one('hr.afp', 'AFP')
    anticipo_sueldo = fields.Float('Anticipo de Sueldo',help="Anticipo De Sueldo Realizado Contablemente")
    carga_familiar = fields.Integer('Carga Simple',help="Carga familiar para el cálculo de asignación familiar simple")
    carga_familiar_maternal = fields.Integer('Carga Maternal',help="Carga familiar para el cálculo de asignación familiar maternal")
    carga_familiar_invalida = fields.Integer('Carga Inválida',help="Carga familiar para el cálculo de asignación familiar inválida")
    colacion = fields.Float('Asig. Colación', help="Colación")
    isapre_id = fields.Many2one('hr.isapre', 'ISAPRE')
    isapre_cotizacion_uf = fields.Float('Cotización Pactada', digits=(6, 4),  help="Cotización Pactada")
    isapre_fun = fields.Char('Número de FUN',  help="Indicar N° Contrato de Salud a Isapre")
    isapre_cuenta_propia = fields.Boolean('Isapre Cuenta Propia')
    movilizacion = fields.Float('Asig. Movilización', help="Movilización")
    mutual_seguridad = fields.Boolean('Mutual Seguridad', default=True)
    otro_no_imp = fields.Float('Otros No Imponible', help="Otros Haberes No Imponibles")
    otros_imp = fields.Float('Otros Imponible', help="Otros Haberes Imponibles")
    pension = fields.Boolean('Pensionado')
    sin_afp = fields.Boolean('No Calcula AFP')
    sin_afp_sis = fields.Boolean('No Calcula AFP SIS')
    seguro_complementario_id = fields.Many2one('hr.seguro.complementario', 'Nombre')
    seguro_complementario = fields.Float('Seguro Complementario',  help="Seguro Complementario")
    viatico_santiago = fields.Float('Asig. Viático',  help="Asignación de Viático")
    complete_name = fields.Char(related='employee_id.firstname')
    last_name = fields.Char(related='employee_id.last_name')
    gratificacion_legal = fields.Boolean('Gratificación L. Manual')
    isapre_moneda= fields.Selection(CURRENCY_SELECTION, string="Tipo Moneda", default="uf", required=True)
    apv_id = fields.Many2one('hr.apv', 'APV')
    aporte_voluntario = fields.Float('Ahorro Previsional Voluntario (APV)', help="Ahorro Previsional Voluntario (APV)")
    aporte_voluntario_moneda= fields.Selection(CURRENCY_SELECTION, string="Tipo Moneda APV", default="uf", required=True)
    forma_pago_apv = fields.Selection([('1', 'Directa'), ('2', 'Indirecta')], 'Forma de Pago', default="1")
    seguro_complementario_moneda = fields.Selection([('uf', 'UF'),('clp', 'CLP')], string="Insurance Currency", default="uf")
    codigo_falp = fields.Char('Código Falp',  help="Indicar Código Falp")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category", required=True, default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    is_part_time = fields.Boolean('Part Time')
