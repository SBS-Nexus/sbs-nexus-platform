from modules.rechnungsverarbeitung.src.invoices.services.overdue_alerts import (
    emit_overdue_invoice_alerts_for_tenant,
)

TENANTS = ["tenant-a", "tenant-b"]  # später dynamisch aus Tenant-Verwaltung

if __name__ == "__main__":
    total = 0
    for tenant in TENANTS:
        created = emit_overdue_invoice_alerts_for_tenant(tenant)
        print(f"Tenant {tenant}: created {created} alerts")
        total += created
    print("Total alerts created:", total)
