
{
    'name': 'Sale Order Images',
    'version': '1.0.1',
    'category': 'Sale Order',
    'sequence': 20,
    'summary': 'Add the images in the sale order and invoice reports and preview.',
    'description': "",
    'depends': ['sale',
                'sale_management'],
    'data': ['views/Devis/sale_order_form.xml',
             'views/Devis/sale_order_preview.xml',
             'views/Devis/sale_order_report.xml'],
    'installable': True,
    'auto-install': False,
    'website': 'https://www.mokatourisme.fr',
}
