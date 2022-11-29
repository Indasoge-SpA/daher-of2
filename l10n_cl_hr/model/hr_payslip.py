from pytz import timezone
from datetime import date, datetime, time

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    indicadores_id = fields.Many2one('hr.indicadores', string='Indicadores',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Defines Previred Forecast Indicators')
    movimientos_personal = fields.Selection(
     [('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')],
     default='0', string= "Código Movimiento")

    date_start_mp = fields.Date('Fecha Inicio MP',  help="Fecha de inicio del movimiento de personal")
    date_end_mp = fields.Date('Fecha Fin MP',  help="Fecha del fin del movimiento de personal")
    isapre_cotizacion_uf = fields.Float('Cotización', digits=(6, 4),  help="Cotización Pactada")
    licencias = fields.Integer(
        'Licencias', compute='_compute_ausentismo')
    vacaciones = fields.Integer(
        'Vacaciones', compute='_compute_ausentismo')
    ausencias = fields.Integer(
        'Ausencias', compute='_compute_ausentismo')


    @api.model
    def create(self, vals):
        if 'indicadores_id' in self.env.context:
            vals['indicadores_id'] = self.env.context.get('indicadores_id')
        if 'movimientos_personal' in self.env.context:
            vals['movimientos_personal'] = self.env.context.get('movimientos_personal')
        return super(HrPayslip, self).create(vals)



    #Se pide recáldulo de días cuando se establece fechas de movimientos de personal y hay retiro o contratación
    @api.onchange('date_start_mp', 'date_end_mp')
    def _onchange_movimiento(self):
        if self.date_end_mp and self.date_end_mp:
            if self.movimientos_personal in ['1', '2', '7']:
                self.onchange_employee()


    #Se pide cotizacion del periodo para que quede guardada
    @api.onchange('contract_id','employee_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.isapre_cotizacion_uf = self.contract_id.isapre_cotizacion_uf


    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        attendance = 30
        not_attendance = 0

        #First For We look for not attendance
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            not_attendance_ids = self.env['hr.leave'].search([
                    ('employee_id', '=', self.employee_id.id),
                    ('date_to', '<=', self.date_to),
                    ('date_from', '>=', self.date_from),
                    ('state', '=', 'validate')])
            not_days = 0
            out_of_contract = 0
            for not_attendance in not_attendance_ids:
                not_days = not_days + not_attendance.number_of_days
            if not_days == 31:
                not_days = 30
            not_attendance = not_days
            if self.date_from < self.contract_id.date_start:
                out_of_contract = (self.contract_id.date_start - self.date_from).days



        #Second For We take 30 - not attendance

        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            if work_entry_type.code == 'WORK100':
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': attendance - not_attendance - out_of_contract,
                    'number_of_hours': 180,
                }
                res.append(attendance_line)
            if work_entry_type.code != 'WORK100':
                licencia_ids = self.env['hr.leave'].search([
                    ('employee_id', '=', self.employee_id.id),
                    ('date_to', '<=', self.date_to),
                    ('date_from', '>=', self.date_from),
                    ('holiday_status_id.work_entry_type_id.code', '=', work_entry_type.code),
                    ('state', '=', 'validate')], order='date_from asc')
                for licencia in licencia_ids:
                    attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': licencia.number_of_days,
                    'number_of_hours': hours,
                    'date_from' : licencia.date_from.strftime('%Y-%m-%d'),
                    'date_to' : licencia.date_to.strftime('%Y-%m-%d'),
                    'movimientos_personal': licencia.holiday_status_id.movimientos_personal or 0
                    }
                    res.append(attendance_line)
        return res




    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            res = self._get_worked_day_lines_values(domain=domain)
            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_contract_calendar()
            if self.date_from < contract.date_start:
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                out_days += (contract.date_start - self.date_from).days
                out_hours += out_time['hours']
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                out_days += out_time['days']
                out_hours += out_time['hours']

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        partner = line.partner_id
        #Read Employee when not a Payslip Run
        if not line.slip_id.payslip_run_id:
            partner = line.slip_id.employee_id.address_home_id
        return {
            'name': line.name,
            'partner_id': partner.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
        }

    def _compute_ausentismo(self):
        ausencias = 0
        licencias = 0
        vacaciones = 0
        for line in self.worked_days_line_ids:
            if 'AUSEN' in line.code.upper():
                ausencias += line.number_of_days
            if 'LICEN' in line.code.upper():
                licencias += line.number_of_days
            if 'VACA' in line.code.upper():
                vacaciones += line.number_of_days
        self.ausencias = ausencias
        self.licencias = licencias
        self.vacaciones = vacaciones

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    date_from = fields.Date(string='Desde')

    date_to = fields.Date(string='Hasta')

    movimientos_personal = fields.Selection(
     [('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')],
     default='0', string= "Código Movimiento")
