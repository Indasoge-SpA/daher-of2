{
    'name': 'Chilean Payroll',
    'category': 'Payroll Localization',
    'sequence': 295,
    'summary': 'Manage your employee payroll records for Chile',
    'author': 'Konos',
    'website': 'http://konos.cl',
    'depends': [
            'hr_payroll',
            'hr_payroll_account',
            'hr_holidays',
        ],
    'version': '15.0.0.1.4',
    'description': """
Chilean Payroll & Human Resources.
==================================
    -Payroll configuration for Chile localization.
    -All contributions rules for Chile payslip.
    * Employee Basic Info
    * Employee Contracts
    * Attendance, Holidays and Sick Licence
    * Employee PaySlip
    * Allowances / Deductions / Company Inputs
    * Extra Time
    * Pention Indicators
    * Payroll Books
    * Previred Plain Text
    , ...
    Report
  """,
    'active': True,
    'data': [
        'views/menu_root.xml',
        'views/res_company.xml',
        'views/hr_indicadores_previsionales_view.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee.xml',
        'views/hr_payslip_view.xml',
        'views/hr_afp_view.xml',
        'views/hr_department_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/report_templates.xml',
        'views/report_payslip.xml',
        'views/report_hrsalarybymonth.xml',
        'views/res_config_settings_views.xml',
        'views/hr_salary_books.xml',
        'views/hr_holiday_views.xml',
        'views/hr_leave_views.xml',
        'views/wizard_export_csv_previred_view.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_analytic_account.xml',
        'data/l10n_cl_hr_indicadores.xml',
        'data/l10n_cl_hr_isapre.xml',
        'data/l10n_cl_hr_afp.xml',
        'data/l10n_cl_hr_mutual.xml',
        'data/l10n_cl_hr_apv.xml',
        'data/hr_type_employee.xml',
        'data/resource_calendar_attendance.xml',
        'data/hr_holidays_status.xml',
        'data/hr_contract_type.xml',
        'data/l10n_cl_hr_ccaf.xml',
        'data/account_journal.xml',
        'data/l10n_cl_hr_payroll_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
