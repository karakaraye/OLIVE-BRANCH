# Each screen is read-only until its functional module is implemented.
ROLE_SCREENS = {
    "reception": (
        "reception",
        "Guest stays",
        "Handle arrivals, departures and guest stays.",
    ),
    "cashier": ("outlet", "Outlet till", "Handle sales for your assigned outlet."),
    "stores": ("stock", "Stock records", "Record stock movements and counts."),
    "accountant": (
        "reconciliation",
        "Reconciliation",
        "Reconcile sales and collections.",
    ),
    "manager": ("approvals", "Approvals", "Review actions that require approval."),
    "owner": ("reports", "Reports", "View hotel reports."),
    "admin": (
        "accounts",
        "Staff administration",
        "Manage named staff accounts and roles.",
    ),
}


def screen_permission(screen):
    return f"access_{screen}_screen"
