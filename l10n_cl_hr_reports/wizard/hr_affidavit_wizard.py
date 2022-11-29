from odoo import api,models,fields,SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class hr_affidavit_wizard(models.TransientModel):
    _name = 'hr.affidavit.wizard'
    _description = 'Informe de declaraciones juradas'

    year = fields.Date('Año', required=True, default=lambda self: fields.Date.context_today(self))

    def action_print_report(self):
        return
