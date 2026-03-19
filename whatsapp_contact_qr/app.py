from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote

import qrcode
from PIL import Image, ImageTk


APP_TITLE = "WhatsApp QR Builder"
WINDOW_SIZE = "980x660"
QR_PREVIEW_SIZE = 320
DEFAULT_STATUS = "Enter a WhatsApp number, then generate the QR code."


def clean_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in (" ", "-", "_") else "_" for char in value)
    safe = "_".join(part for part in safe.split())
    return safe or "whatsapp_qr"


def normalize_phone(value: str) -> str:
    digits_only = "".join(char for char in value if char.isdigit())
    if len(digits_only) < 8:
        raise ValueError("Enter a valid WhatsApp number with country code. Example: 60123456789")
    return digits_only


class WhatsAppQrApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(860, 580)
        self.root.configure(bg="#eef1eb")

        self.phone_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.last_qr_image: Image.Image | None = None
        self.last_whatsapp_url = ""
        self.qr_label: ttk.Label | None = None
        self.message_text: tk.Text | None = None
        self.status_var = tk.StringVar(value=DEFAULT_STATUS)

        self._build_styles()
        self._build_layout()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#eef1eb")
        style.configure("Panel.TFrame", background="#fbfdf7")
        style.configure("Title.TLabel", background="#eef1eb", foreground="#1d2b22", font=("Segoe UI Semibold", 24))
        style.configure("Body.TLabel", background="#fbfdf7", foreground="#22352a", font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background="#eef1eb", foreground="#4b5f54", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#eef1eb", foreground="#115c3e", font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI Semibold", 10))
        style.configure("Secondary.TButton", font=("Segoe UI", 10))
        style.configure("Field.TEntry", padding=6)

    def _build_layout(self) -> None:
        root_frame = ttk.Frame(self.root, style="Root.TFrame", padding=18)
        root_frame.pack(fill="both", expand=True)
        root_frame.columnconfigure(0, weight=5)
        root_frame.columnconfigure(1, weight=4)
        root_frame.rowconfigure(1, weight=1)

        header = ttk.Frame(root_frame, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Creates a QR code that opens a WhatsApp chat instead of a contact card.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        form_panel = ttk.Frame(root_frame, style="Panel.TFrame", padding=18)
        form_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        form_panel.columnconfigure(0, weight=1)

        preview_panel = ttk.Frame(root_frame, style="Panel.TFrame", padding=18)
        preview_panel.grid(row=1, column=1, sticky="nsew")
        preview_panel.columnconfigure(0, weight=1)
        preview_panel.rowconfigure(1, weight=1)

        phone_wrapper = ttk.Frame(form_panel, style="Panel.TFrame")
        phone_wrapper.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        phone_wrapper.columnconfigure(0, weight=1)
        ttk.Label(phone_wrapper, text="WhatsApp Number", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Entry(phone_wrapper, textvariable=self.phone_var, style="Field.TEntry").grid(row=1, column=0, sticky="ew")
        ttk.Label(
            phone_wrapper,
            text="Use the full international number. Example: 60123456789",
            style="Body.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        name_wrapper = ttk.Frame(form_panel, style="Panel.TFrame")
        name_wrapper.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        name_wrapper.columnconfigure(0, weight=1)
        ttk.Label(name_wrapper, text="Label Name", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Entry(name_wrapper, textvariable=self.name_var, style="Field.TEntry").grid(row=1, column=0, sticky="ew")

        message_wrapper = ttk.Frame(form_panel, style="Panel.TFrame")
        message_wrapper.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        message_wrapper.columnconfigure(0, weight=1)
        ttk.Label(message_wrapper, text="Pre-filled Message", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.message_text = tk.Text(
            message_wrapper,
            height=10,
            wrap="word",
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
            background="#ffffff",
            foreground="#22352a",
            insertbackground="#22352a",
        )
        self.message_text.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(form_panel, style="Panel.TFrame")
        actions.grid(row=3, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)
        actions.columnconfigure(3, weight=1)

        ttk.Button(actions, text="Generate QR", style="Action.TButton", command=self.generate_qr).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(actions, text="Save PNG", style="Secondary.TButton", command=self.save_png).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(actions, text="Copy Link", style="Secondary.TButton", command=self.copy_link).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self.clear_form).grid(
            row=0, column=3, sticky="ew", padx=(8, 0)
        )

        ttk.Label(preview_panel, text="QR Preview", style="Body.TLabel").grid(row=0, column=0, sticky="w")

        self.qr_label = ttk.Label(preview_panel, text="No QR code yet", anchor="center", style="Body.TLabel")
        self.qr_label.grid(row=1, column=0, sticky="nsew", pady=(12, 12))

        info_text = (
            "Scanning this QR should open a WhatsApp chat.\n"
            "If WhatsApp is installed, most phones will hand off to the app.\n"
            "The message can be pre-filled, but it will not send automatically."
        )
        ttk.Label(preview_panel, text=info_text, style="Body.TLabel", justify="left").grid(
            row=2, column=0, sticky="w", pady=(0, 12)
        )
        ttk.Label(preview_panel, textvariable=self.status_var, style="Status.TLabel", justify="left", wraplength=340).grid(
            row=3, column=0, sticky="ew"
        )

    def build_whatsapp_url(self) -> str:
        phone = normalize_phone(self.phone_var.get().strip())
        message = self.message_text.get("1.0", "end").strip() if self.message_text else ""
        url = f"https://wa.me/{phone}"
        if message:
            url = f"{url}?text={quote(message)}"
        return url

    def display_name(self) -> str:
        name = self.name_var.get().strip()
        if name:
            return name
        try:
            return normalize_phone(self.phone_var.get().strip())
        except ValueError:
            return "whatsapp"

    def generate_qr(self) -> None:
        try:
            self.last_whatsapp_url = self.build_whatsapp_url()
        except ValueError as exc:
            self.status_var.set(str(exc))
            messagebox.showwarning(APP_TITLE, str(exc))
            return

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(self.last_whatsapp_url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="#123727", back_color="#fbfdf7").convert("RGB")
        self.last_qr_image = image

        preview = image.resize((QR_PREVIEW_SIZE, QR_PREVIEW_SIZE), Image.Resampling.NEAREST)
        self.preview_photo = ImageTk.PhotoImage(preview)
        if self.qr_label:
            self.qr_label.configure(image=self.preview_photo, text="")

        self.status_var.set(f'WhatsApp QR ready for "{self.display_name()}".')

    def save_png(self) -> None:
        if self.last_qr_image is None:
            self.generate_qr()
            if self.last_qr_image is None:
                return

        default_name = f"{clean_filename(self.display_name())}_whatsapp_qr.png"
        target = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png")],
        )
        if not target:
            return

        self.last_qr_image.save(target)
        self.status_var.set(f"Saved PNG to {Path(target).name}")

    def copy_link(self) -> None:
        if not self.last_whatsapp_url:
            try:
                self.last_whatsapp_url = self.build_whatsapp_url()
            except ValueError as exc:
                self.status_var.set(str(exc))
                messagebox.showwarning(APP_TITLE, str(exc))
                return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_whatsapp_url)
        self.root.update()
        self.status_var.set("WhatsApp link copied to clipboard.")

    def clear_form(self) -> None:
        self.phone_var.set("")
        self.name_var.set("")

        if self.message_text:
            self.message_text.delete("1.0", "end")

        self.last_whatsapp_url = ""
        self.last_qr_image = None
        self.preview_photo = None

        if self.qr_label:
            self.qr_label.configure(image="", text="No QR code yet")

        self.status_var.set(DEFAULT_STATUS)


def main() -> None:
    root = tk.Tk()
    WhatsAppQrApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
