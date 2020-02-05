# -*- coding: utf-8 -*-

{
    'name': "Moka Prestation",
    'summary': "Gérer vos dossier groupes.",
    'author': "Corentin FOSSAERT",
    'license': "AGPL-3",
    'website': "http://www.mokatourisme.fr",
    'category': 'CRM',
    'version': '12.0.1.0.1',
    'depends': ['sale',
                'sale_management',
                'crm',
                'calendar'],
    'data': ['Views/Devis/devis_form.xml',
             'Views/Devis/devis_report.xml',
             'Views/Devis/devis_preview.xml',
             'Views/CRM/crm_form.xml',
             'Views/CRM/crm_calendar_form.xml',
             'Views/MD/md_form.xml',
             'Views/Invoice/invoice_form.xml',
             'Views/Invoice/invoice_report.xml',
             'Views/Calendar/calendar_form.xml',
             'Views/Calendar/calendar_form_popup.xml',
             ],
    'installable': True,
    'auto_install': False
}
