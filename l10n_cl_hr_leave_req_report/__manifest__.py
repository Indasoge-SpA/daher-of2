# -*- coding: utf-8 -*-
# Part of Konos. See LICENSE file for full copyright and licensing details.

{
    'name': "Chilean Leave Request Report in Odoo",

    'summary': """
        This apps helps to print employee leave request report
    """,

    'description': """
        leave
        leave request report
        print leave request report
        print leave
        print leave report
        print leave request
        print hr Employees Leave Request Report
        print hr leave reports
        print hr employees reports
        print hr reports
        hr leave reports
        hr employees reports
        holiday reports
        hr holiday reports
""",

    'author': "Konos Soluciones & Servicios",

    'website': "https://www.konos.cl",

    'category': 'Human Resource',
    'version': '0.1',

    'depends': [
        'base',
        'hr',
        'hr_holidays',
        'l10n_cl_hr'
    ],

    'data': [
        'reports/report_templates.xml',
        'reports/hr_leave_req_report.xml',
        'reports/hr_leave_req_report_template.xml',
    ],

    'demo': [
    ],

    "images": [
        'static/description/Banner.png'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
