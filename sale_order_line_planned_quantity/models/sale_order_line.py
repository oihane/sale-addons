# Copyright (c) 2024 Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    planned_quantity = fields.Float(
        string="Planned Quantity",
        compute="_compute_planned_quantity",
        digits="Product Unit of Measure",
        store=True,
        copy=False,
    )
    difference_between_ordered_planned = fields.Boolean(
        string="Difference Between Ordered And Planned",
        store=True,
        copy=False,
        compute="_compute_planned_quantity",
    )

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_planned_quantity(self):
        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                for move in outgoing_moves:
                    if move.state in ('done', 'cancel'):
                        continue
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                for move in incoming_moves:
                    if move.state in ('done', 'cancel'):
                        continue
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                line.update({
                    'planned_quantity': qty,
                    'difference_between_ordered_planned': bool(line.product_uom_qty != qty),
                })
            else:
                line.update({
                    'planned_quantity': line.product_uom_qty,
                    'difference_between_ordered_planned': False,
                })

    # @api.depends(
    #     "product_uom_qty",
    #     "move_ids",
    #     "move_ids.state",
    #     "move_ids.product_uom_qty",
    #     "move_ids.picking_type_id",
    #     "move_ids.picking_type_id.use_to_calculate_planned_quantities",
    # )
    # def _compute_planned_quantity(self):
    #     for line in self:
    #         planned_quantity = 0
    #         moves_planned_quantities = False
    #         if line.qty_delivered_method == "stock_move":
    #             moves = line.move_ids.filtered(
    #                 lambda m: m.state not in ("done", "cancel") and not m.scrapped
    #             )
    #             if line.move_ids:
    #                 moves_planned_quantities = line.move_ids.filtered(
    #                     lambda x: x.picking_type_id.use_to_calculate_planned_quantities
    #                 )
    #                 if moves_planned_quantities:
    #                     moves = moves_planned_quantities.filtered(
    #                         lambda x: x.state != "cancel"
    #                     )
    #                     if moves:
    #                         planned_quantity = sum(moves.mapped("product_uom_qty"))
    #         line.planned_quantity = planned_quantity if moves_planned_quantities else 0

    # @api.depends(
    #     "planned_quantity",
    #     "state",
    #     "product_uom_qty",
    # )
    # def _compute_difference_between_ordered_planned(self):
    #     for line in self:
    #         moves_planned_quantities = False
    #         if line.move_ids:
    #             moves_planned_quantities = line.move_ids.filtered(
    #                 lambda x: x.picking_type_id.use_to_calculate_planned_quantities
    #             )
    #         if moves_planned_quantities:
    #             line.difference_between_ordered_planned = bool(
    #                 line.product_uom_qty != line.planned_quantity
    #                 and line.state != "draft"
    #             )
    #         else:
    #             line.difference_between_ordered_planned = False
