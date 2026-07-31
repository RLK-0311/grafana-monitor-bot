# WhatsApp Configuration Handover

## If another engineer takes over this project, update only the following:

### 1. Change Personal WhatsApp Chat
File:
config/whatsapp.yaml

Change:
personal_chat: "SonJIO (You)"

To:
personal_chat: "New Engineer Name"

------------------------------------------------------------

### 2. Change Office Group (if required)
File:
config/whatsapp.yaml

Change:
group_chat: "CM-MONITORING"

To:
group_chat: "New Group Name"

------------------------------------------------------------

### 3. Login with New WhatsApp Account
Folder:
browser/whatsapp_profile/

Delete or rename this folder.

Example:
browser/whatsapp_profile_old

Run the bot again and scan the QR code using the new engineer's WhatsApp account.

------------------------------------------------------------

### 4. No Python Code Changes Required

The following files DO NOT need any modification:

- src/whatsapp.py
- src/whatsapp_upload.py
- bot.py
- src/browser_manager.py
- src/whatsapp_report.py

------------------------------------------------------------

### 5. Handover Checklist

☐ Update personal_chat in config/whatsapp.yaml

☐ Update group_chat (if required)

☐ Delete/Rename browser/whatsapp_profile

☐ Run the bot

☐ Scan QR Code

☐ Verify personal message delivery

☐ Verify group image upload

☐ Verify alert summary

------------------------------------------------------------

Expected Result:
The project will continue working with the new engineer's WhatsApp account without changing any Python code.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##  what if instead of personal name i want to change like a new group in that

# WhatsApp Configuration Handover

## Change the Alert Destination

File:
config/whatsapp.yaml

Current:

personal_chat: "DEVOPS-ALERTS"
group_chat: "CM-MONITORING"

If the destination changes, simply update the chat names.

Example:

personal_chat: "NEW-DEVOPS-TEAM"
group_chat: "NEW-MONITORING-GROUP"

------------------------------------------------------------

## Change WhatsApp Account

Folder:
browser/whatsapp_profile/

Delete or rename the folder.

Run the bot.

Scan the QR code with the new WhatsApp account.

------------------------------------------------------------

## No Python Code Changes Required

The following files never need modification:

- bot.py
- src/whatsapp.py
- src/whatsapp_upload.py
- src/browser_manager.py
- src/whatsapp_report.py

------------------------------------------------------------

## Handover Checklist

☐ Update chat names in config/whatsapp.yaml

☐ Scan QR code with the new WhatsApp account

☐ Verify summary message delivery

☐ Verify screenshot album upload

☐ Verify automation completes successfully

------------------------------------------------------------

Result:
Only `config/whatsapp.yaml` and the WhatsApp login need to be changed. No Python code modifications are required.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
