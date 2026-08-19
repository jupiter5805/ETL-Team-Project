def find_sales_order_changes(
    previous_snapshot,
    current_snapshot,
):
    previous_orders = {
        row["sales_order_id"]: row
        for row in previous_snapshot
    }

    changed_orders = []

    for current_order in current_snapshot:
        sales_order_id = current_order["sales_order_id"]

        if sales_order_id not in previous_orders:
            changed_orders.append(current_order)
            continue

        previous_order = previous_orders[sales_order_id]

        if current_order != previous_order:
            changed_orders.append(current_order)

    return changed_orders
