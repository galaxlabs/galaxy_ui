# Copyright (c) 2026, Galaxy Labs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UITheme(Document):

    def validate(self):
        # Enforce single active theme
        if (self.status or "Draft")!="Published":
            self.is_active = 0
            self.published_on = None
            self.published_by = None
    
        if self.is_active:
            self.status = "Published"
            if not self.published_on:
                self.published_on = frappe.utils.now_datetime()
            if not self.published_by:
                self.published_by = frappe.session.user

            frappe.db.sql(
                """UPDATE `tabUI Theme` SET is_active=0 WHERE name!=%s""",
                (self.name,),
            )
        
        # Sync system tokens from parent fields
        self.sync_system_tokens()

        # Clean tokens (format + trimming)
        if getattr(self, "tokens", None):
            for r in self.tokens:
                r.token = (r.token or "").strip()
                r.light_value = (r.light_value or "").strip()
                r.dark_value = (r.dark_value or "").strip()

                if not r.token and not r.light_value and not r.dark_value:
                    r.enabled = 0

                if r.enabled and r.token and not r.token.startswith("--"):
                    frappe.throw(f"Token must start with -- : {r.token}")

    # -----------------------------------------------------
    # AUTO TOKEN GENERATION
    # -----------------------------------------------------

    def sync_system_tokens(self):
        """
        Generate / update system tokens from parent UI Theme fields.
        Does NOT override Custom tokens.
        """

        mapping = {
            "primary_color": "--ui-primary",
            "background_color": "--ui-bg",
            "card_color": "--ui-card",
            "border_color": "--ui-border",
            "text_primary": "--ui-text",
            "text_muted": "--ui-text-muted",
            "sidebar_bg": "--ui-sidebar-bg",
            "sidebar_text": "--ui-sidebar-text",
            "navbar_bg": "--ui-navbar-bg",
            "navbar_text": "--ui-navbar-text",
        }

        existing = {}
        for row in self.tokens or []:
            if row.source == "System":
                existing[row.token] = row

        for fieldname, token_name in mapping.items():
            light = (self.get(fieldname) or "").strip()
            dark = (self.get(f"{fieldname}_dark") or "").strip()

            if not light:
                continue

            dark_value = dark if dark else light

            if token_name in existing:
                row = existing[token_name]
                row.enabled = 1
                row.light_value = light
                row.dark_value = dark_value
            else:
                self.append("tokens", {
                    "enabled": 1,
                    "token": token_name,
                    "type": "color",
                    "light_value": light,
                    "dark_value": dark_value,
                    "source": "System",
                })
