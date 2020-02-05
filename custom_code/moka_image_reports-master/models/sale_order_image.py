
from odoo import fields, models

class SaleOrderimage(models.Model):
    #Add a field to show/hide the images in the the reports of sale order
    _inherit='sale.order'

    moka_images_show = fields.Selection([('none', 'No Images'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
                                        default="none", string="Sale Order Images", help="Select the format of the images you want to display on sale order.")

    def get_image(self, order_line_id):
        #Return the image linked to the product

        product_id = self.env['sale.order.line'].search([('id', '=', order_line_id)])

        return product_id.product_image.decode()
