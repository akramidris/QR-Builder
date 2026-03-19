# QR Builders

Desktop QR code tools built with Python and Tkinter.

This repository contains two separate apps:

- `phone_contact_qr` creates QR codes for contact cards using `vCard`
- `whatsapp_contact_qr` creates QR codes that open a WhatsApp chat

## Project Structure

```text
qr_code_contact/
|-- phone_contact_qr/
|   |-- app.py
|   |-- start_app.bat
|   |-- start.sh
|   |-- requirements.txt
|   `-- README.md
|-- whatsapp_contact_qr/
|   |-- app.py
|   |-- start_app.bat
|   |-- start.sh
|   |-- requirements.txt
|   `-- README.md
`-- README.md
```

## Apps

### 1. Phone Contact QR

Folder: `phone_contact_qr`

What it does:
- creates a QR code containing a `vCard`
- shows a live QR preview
- saves the QR as PNG
- exports the contact as a `.vcf` file

Expected phone behavior:
- scanning the QR usually opens the phone's add-contact screen
- the user still needs to confirm saving the contact

### 2. WhatsApp QR

Folder: `whatsapp_contact_qr`

What it does:
- creates a QR code that opens a WhatsApp chat
- supports an optional pre-filled message
- shows a live QR preview
- saves the QR as PNG
- copies the generated WhatsApp link

Expected phone behavior:
- scanning the QR should open a WhatsApp chat flow
- a pre-filled message can appear, but it does not send automatically

## Run

Open the README inside the app folder you want to use:

- `phone_contact_qr/README.md`
- `whatsapp_contact_qr/README.md`

## Windows Builds

Fresh prebuilt Windows executables are stored in:

- `windows_builds/PhoneContactQR.exe`
- `windows_builds/WhatsAppQR.exe`

## Requirements

- Python 3
- `tkinter`
- internet is only needed the first time packages are installed

## GitHub Notes

- `.venv` is ignored and should not be committed
- `__pycache__` and `*.pyc` files are ignored
- `build/` and `dist/` are ignored because they contain generated EXE output
- if you make the repository public, choose a license before publishing

## Push To GitHub

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
