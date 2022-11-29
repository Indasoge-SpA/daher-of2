from odoo import fields, models, tools, _


class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Run'

    indicadores_id = fields.Many2one('hr.indicadores',
                                     'Indicadores',
                                     states={'draft': [('readonly', False)]},
                                     readonly=True, required=True)
    movimientos_personal = fields.Selection((
     ('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')
     ), 'Movimientos Personal', default="0")
    company_id = fields.Many2one('res.company', 'Company',
                                 copy=False, readonly=True,
                                 default=lambda self: self.env.company.id)
