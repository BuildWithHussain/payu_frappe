import frappe

from payu.payu_integration.doctype.payu_transaction.payu_transaction import get_transactions_from_payu


def sync_pending_transactions():
    pending_orders = frappe.db.get_all("PayU Transaction", filters={"status": "Pending"}, pluck="name")
    txns = get_transactions_from_payu(pending_orders)

    for txn in txns:
        # update each txn
        pass

