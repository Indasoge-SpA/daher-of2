from odoo import api,models,fields,SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_representative_id = fields.Many2one('res.partner',string='Representante Legal')
    giro = fields.Char('Giro')
    rut_declarante= fields.Char('Rut declarante')
