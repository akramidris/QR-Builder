from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import qrcode
from PIL import Image, ImageTk


APP_TITLE = "Contact QR Builder"
WINDOW_SIZE = "1040x700"
QR_PREVIEW_SIZE = 320
DEFAULT_STATUS = "Fill in at least a name or phone number, then generate the QR code."


def escape_vcard(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace("\n", "\\n")
    escaped = escaped.replace(";", r"\;")
    escaped = escaped.replace(",", r"\,")
    return escaped.strip()


def clean_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in (" ", "-", "_") else "_" for char in value)
    safe = "_".join(part for part in safe.split())
    return safe or "contact_qr"


class ContactQrApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(900, 620)
        self.root.configure(bg="#f4f1e8")

        self.fields: dict[str, tk.StringVar] = {}
        self.note_text: tk.Text | None = None
        self.qr_label: ttk.Label | None = None
        self.status_var = tk.StringVar(value=DEFAULT_STATUS)
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.last_qr_image: Image.Image | None = None
        self.last_vcard = ""

        self._build_styles()
        self._build_layout()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#f4f1e8")
        style.configure("Panel.TFrame", background="#fffdf7", relief="flat")
        style.configure("Title.TLabel", background="#f4f1e8", foreground="#1f2a2e", font=("Segoe UI Semibold", 24))
        style.configure("Body.TLabel", background="#fffdf7", foreground="#23343a", font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background="#f4f1e8", foreground="#4a5a5f", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#f4f1e8", foreground="#0e4f56", font=("Segoe UI", 10))
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
            text="Creates a QR code containing a contact card. Scanning it on a phone should open the add-contact flow.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        form_panel = ttk.Frame(root_frame, style="Panel.TFrame", padding=18)
        form_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        form_panel.columnconfigure(0, weight=1)
        form_panel.columnconfigure(1, weight=1)

        preview_panel = ttk.Frame(root_frame, style="Panel.TFrame", padding=18)
        preview_panel.grid(row=1, column=1, sticky="nsew")
        preview_panel.columnconfigure(0, weight=1)
        preview_panel.rowconfigure(1, weight=1)

        field_specs = [
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("phone", "Phone Number"),
            ("email", "Email"),
            ("company", "Company"),
            ("title", "Job Title"),
            ("website", "Website"),
            ("address", "Address"),
        ]

        for index, (field_key, label) in enumerate(field_specs):
            row = (index // 2) * 2
            column = index % 2
            wrapper = ttk.Frame(form_panel, style="Panel.TFrame")
            wrapper.grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 8, 8 if column == 0 else 0), pady=(0, 12))
            wrapper.columnconfigure(0, weight=1)
            ttk.Label(wrapper, text=label, style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))

            variable = tk.StringVar()
            entry = ttk.Entry(wrapper, textvariable=variable, style="Field.TEntry")
            entry.grid(row=1, column=0, sticky="ew")
            self.fields[field_key] = variable

        note_wrapper = ttk.Frame(form_panel, style="Panel.TFrame")
        note_wrapper.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(4, 12))
        note_wrapper.columnconfigure(0, weight=1)
        ttk.Label(note_wrapper, text="Notes", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.note_text = tk.Text(
            note_wrapper,
            height=6,
            wrap="word",
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
            background="#ffffff",
            foreground="#22343a",
            insertbackground="#22343a",
        )
        self.note_text.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(form_panel, style="Panel.TFrame")
        actions.grid(row=9, column=0, columnspan=2, sticky="ew")
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
        ttk.Button(actions, text="Export VCF", style="Secondary.TButton", command=self.save_vcf).grid(
            row=0, column=2, sticky="ew", padx=(8, 0)
        )
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self.clear_form).grid(
            row=0, column=3, sticky="ew", padx=(8, 0)
        )

        ttk.Label(preview_panel, text="QR Preview", style="Body.TLabel").grid(row=0, column=0, sticky="w")

        self.qr_label = ttk.Label(preview_panel, text="No QR code yet", anchor="center", style="Body.TLabel")
        self.qr_label.grid(row=1, column=0, sticky="nsew", pady=(12, 12))

        info_text = (
            "Most phones will detect this as a contact card.\n"
            "After scanning, they usually show an Add Contact screen.\n"
            "They do not silently save the contact without user confirmation."
        )
        ttk.Label(preview_panel, text=info_text, style="Body.TLabel", justify="left").grid(
            row=2, column=0, sticky="w", pady=(0, 12)
        )
        ttk.Label(preview_panel, textvariable=self.status_var, style="Status.TLabel", justify="left", wraplength=360).grid(
            row=3, column=0, sticky="ew"
        )

    def build_vcard(self) -> str:
        first_name = self.fields["first_name"].get().strip()
        last_name = self.fields["last_name"].get().strip()
        phone = self.fields["phone"].get().strip()
        email = self.fields["email"].get().strip()
        company = self.fields["company"].get().strip()
        title = self.fields["title"].get().strip()
        website = self.fields["website"].get().strip()
        address = self.fields["address"].get().strip()
        notes = self.note_text.get("1.0", "end").strip() if self.note_text else ""

        full_name = " ".join(part for part in (first_name, last_name) if part).strip()
        if not full_name and not phone:
            raise ValueError("Enter at least a name or phone number.")

        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{escape_vcard(last_name)};{escape_vcard(first_name)};;;",
            f"FN:{escape_vcard(full_name or phone)}",
        ]

        if company:
            lines.append(f"ORG:{escape_vcard(company)}")
        if title:
            lines.append(f"TITLE:{escape_vcard(title)}")
        if phone:
            lines.append(f"TEL;TYPE=CELL:{escape_vcard(phone)}")
        if email:
            lines.append(f"EMAIL;TYPE=INTERNET:{escape_vcard(email)}")
        if website:
            lines.append(f"URL:{escape_vcard(website)}")
        if address:
            lines.append(f"ADR;TYPE=HOME:;;{escape_vcard(address)};;;;")
        if notes:
            lines.append(f"NOTE:{escape_vcard(notes)}")

        lines.append("END:VCARD")
        return "\n".join(lines)

    def generate_qr(self) -> None:
        try:
            self.last_vcard = self.build_vcard()
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
        qr.add_data(self.last_vcard)
        qr.make(fit=True)
        image = qr.make_image(fill_color="#142226", back_color="#fffdf7").convert("RGB")
        self.last_qr_image = image

        preview = image.resize((QR_PREVIEW_SIZE, QR_PREVIEW_SIZE), Image.Resampling.NEAREST)
        self.preview_photo = ImageTk.PhotoImage(preview)
        if self.qr_label:
            self.qr_label.configure(image=self.preview_photo, text="")

        contact_name = self.contact_display_name()
        self.status_var.set(f'QR code ready for "{contact_name}". Use Save PNG or Export VCF if needed.')

    def contact_display_name(self) -> str:
        full_name = " ".join(
            part for part in (self.fields["first_name"].get().strip(), self.fields["last_name"].get().strip()) if part
        ).strip()
        if full_name:
            return full_name
        return self.fields["phone"].get().strip() or "contact"

    def save_png(self) -> None:
        if self.last_qr_image is None:
            self.generate_qr()
            if self.last_qr_image is None:
                return

        default_name = f"{clean_filename(self.contact_display_name())}_qr.png"
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

    def save_vcf(self) -> None:
        if not self.last_vcard:
            try:
                self.last_vcard = self.build_vcard()
            except ValueError as exc:
                self.status_var.set(str(exc))
                messagebox.showwarning(APP_TITLE, str(exc))
                return

        default_name = f"{clean_filename(self.contact_display_name())}.vcf"
        target = filedialog.asksaveasfilename(
            title="Export Contact File",
            defaultextension=".vcf",
            initialfile=default_name,
            filetypes=[("vCard File", "*.vcf")],
        )
        if not target:
            return

        Path(target).write_text(self.last_vcard, encoding="utf-8", newline="\n")
        self.status_var.set(f"Exported VCF to {Path(target).name}")

    def clear_form(self) -> None:
        for variable in self.fields.values():
            variable.set("")

        if self.note_text:
            self.note_text.delete("1.0", "end")

        self.last_qr_image = None
        self.last_vcard = ""
        self.preview_photo = None

        if self.qr_label:
            self.qr_label.configure(image="", text="No QR code yet")

        self.status_var.set(DEFAULT_STATUS)


def main() -> None:
    root = tk.Tk()
    ContactQrApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
