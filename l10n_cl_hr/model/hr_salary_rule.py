from odoo import api, fields, models, tools, _


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = 'Salary Rule'

    date_start = fields.Date('Fecha Inicio',  help="Fecha de inicio de la regla salarial")
    date_end = fields.Date('Fecha Fin',  help="Fecha del fin de la regla salarial")

    @api.model
    def _company_domain(self):
        company_id = self._context.get('force_company') or self.env.user.company_id.id
        return [('company_id', '=', company_id)]

    @api.model
    def _account_domain(self):
        return [('deprecated', '=', False)] + self._company_domain()

    analytic_account_id = fields.Many2one(
        'account.analytic.account', company_dependent=True,
        domain=_company_domain)
    account_tax_id = fields.Many2one(
        'account.tax', company_dependent=True,
        domain=_company_domain)
    account_debit = fields.Many2one(
        'account.account', company_dependent=True,
        domain=_account_domain)
    account_credit = fields.Many2one(
        'account.account', company_dependent=True,
        domain=_account_domain)
