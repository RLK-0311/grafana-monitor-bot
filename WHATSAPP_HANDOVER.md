# WhatsApp Configuration Handover

This document explains everything that needs to be changed when handing over the Grafana Monitoring Bot to another engineer.

---

# 1. Change the Alert Destination

File:

config/whatsapp.yaml

Current configuration:

```yaml
personal_chat: "Grafana_Alerts"
group_chat: "CM-MONITORING"
```

If the destination changes, simply update the chat names.

Example:

```yaml
personal_chat: "DEVOPS-ALERTS"
group_chat: "NEW-MONITORING-GROUP"
```

No Python code changes are required.

---

# 2. Change WhatsApp Account

Folder:

```
browser/whatsapp_profile/
```

Delete or rename the folder.

Example:

```
browser/whatsapp_profile_old
```

Run the bot again.

WhatsApp Web will ask for a QR Code.

Scan it using the new engineer's WhatsApp account.

The new session will automatically be saved inside:

```
browser/whatsapp_profile/
```

---

# 3. Grafana Login

If Grafana credentials change, update:

```
config/grafana.yaml
```

Replace the existing username and password with the new user's credentials.

The bot is configured to automatically log in whenever Grafana redirects to the login page.

No additional code changes are required.

---

# 4. Dashboard URLs

Dashboard URLs are stored in:

```
config/dashboards.yaml
```

Currently the project captures screenshots for 20 dashboards.

To monitor additional dashboards:

- Add the new dashboard name.
- Add its Grafana URL.
- Save the file.

No Python code changes are required.

---

# 5. If WhatsApp QR Code Appears Again

Sometimes WhatsApp Web expires the login session.

If this happens:

1. Run the bot manually.
2. Wait until WhatsApp Web opens.
3. Scan the QR code.
4. Close nothing.
5. The session will be stored again.

The scheduled automation will continue working afterwards.

---

# 6. If Grafana Login Page Appears

If screenshots show the Grafana login page instead of dashboards:

- Verify the username and password in:

```
config/grafana.yaml
```

- Run the bot once manually.

The automation will automatically log in using the configured credentials.

---

# 7. Files That Normally Need Configuration Changes

Configuration Files

```
config/whatsapp.yaml
config/grafana.yaml
config/dashboards.yaml
```

---

# 8. Files That Normally Do NOT Require Modification

The following project files should continue working without modification:

```
bot.py
src/browser_manager.py
src/dashboard_capture.py
src/whatsapp.py
src/whatsapp_upload.py
src/whatsapp_report.py
src/alert_engine.py
src/report_generator.py
```

---

# 9. Handover Checklist

☐ Update chat names in `config/whatsapp.yaml`

☐ Update Grafana credentials in `config/grafana.yaml` (if required)

☐ Update dashboard URLs in `config/dashboards.yaml` (if required)

☐ Delete or rename `browser/whatsapp_profile` if changing WhatsApp account

☐ Run the bot

☐ Scan the QR code (if requested)

☐ Verify Grafana dashboards open correctly

☐ Verify alert summary message is delivered

☐ Verify screenshot album is uploaded

☐ Verify scheduled automation is working

---

# 10. Expected Result

Only configuration files need to be updated during handover.

The core Python code does not require any modifications.

The automation will continue functioning after:

- Updating configuration files.
- Logging into WhatsApp (if required).
- Updating Grafana credentials (if required).

---

# 11. Future Improvements

The project is currently stable and working as expected.

Future enhancement:

- Improve the alert evaluation logic for better accuracy and optimization.

-------------------------------------------------------------------------------------------------------------------------------------------
