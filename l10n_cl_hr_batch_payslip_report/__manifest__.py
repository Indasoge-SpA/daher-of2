# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2022 Konos
#
##############################################################################
{
    'name': "Payslip Batch Report",
    'category': 'Payroll',
    'version': '15.0.1.0',
    'author': 'Konos',
    'description': """
        This Module allows to print Chilean Payslip Batch PDF & Excel Report.
        * Allows user to print Payslip Batch PDF & Excel report.
        * User can see the salary computation group by the Salary rule Category & Salary Rules.
    """,
    'summary': """ This Module allows to print Payroll PDF & Excel Report. payslip report | employee payslip report | payslip batch report | batch report | batch payslip report. """,
    'depends': ['base', 'l10n_cl_hr'],
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_batch_payslip_report.xml',
        'report/report_batch_payslip_template.xml',
        'report/report.xml'
    ],
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
