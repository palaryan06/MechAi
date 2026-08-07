"""Script to programmatically generate a synthetic workshop manual PDF fixture."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


def generate_sample_manual_pdf(output_path: Path) -> Path:
    """Generate a deterministic multi-page workshop manual PDF fixture."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()

    # Set document metadata
    doc.set_metadata(
        {
            "title": "Sample Automotive Workshop Manual",
            "author": "MechAI Engineering",
            "subject": "Cooling System Service & Diagnostic Procedures",
            "keywords": "automotive, cooling, thermostat, torque, inspection",
            "creator": "MechAI PDF Fixture Generator",
            "producer": "PyMuPDF",
        }
    )

    # --- Page 1: Overview and Safety Guidelines ---
    page1 = doc.new_page(width=612, height=792)  # Standard Letter size

    # Title
    page1.insert_text(
        fitz.Point(50, 70),
        "MECHAI AUTOMOTIVE SERVICE MANUAL",
        fontsize=18,
        fontname="helv",
        color=(0, 0.2, 0.4),
    )

    # Section Header
    page1.insert_text(
        fitz.Point(50, 110),
        "Section 11: Engine Cooling System",
        fontsize=14,
        fontname="helv",
        color=(0.1, 0.1, 0.1),
    )

    # Paragraph with Bold / Italic specifications
    page1.insert_text(
        fitz.Point(50, 150),
        "General Description and Operating Principles:",
        fontsize=11,
        fontname="helv",
    )

    desc_text = (
        "The cooling system maintains engine operating temperature within the optimal range "
        "of 88C to 95C. A wax-pellet thermostat regulates coolant flow through the radiator."
    )
    page1.insert_textbox(
        fitz.Rect(50, 165, 560, 220),
        desc_text,
        fontsize=10,
        fontname="times-roman",
    )

    # Warning text
    page1.insert_text(
        fitz.Point(50, 240),
        "WARNING: Never open radiator cap when engine is hot.",
        fontsize=10,
        fontname="helv",
        color=(0.8, 0, 0),
    )

    # Fastener specification
    page1.insert_text(
        fitz.Point(50, 270),
        "Thermostat Housing Bolt Torque: 12 Nm (106 in-lb).",
        fontsize=10,
        fontname="helv",
    )

    # --- Page 2: Procedures, Table, and Component Diagram ---
    page2 = doc.new_page(width=612, height=792)

    page2.insert_text(
        fitz.Point(50, 70),
        "Thermostat Replacement Procedure",
        fontsize=14,
        fontname="helv",
        color=(0, 0.2, 0.4),
    )

    step_text = (
        "1. Disconnect negative battery cable.\n"
        "2. Drain engine coolant into a clean container.\n"
        "3. Disconnect radiator upper hose from water outlet.\n"
        "4. Remove water outlet fitting bolts and remove thermostat.\n"
        "5. Install new thermostat with jiggle valve facing upward.\n"
        "6. Tighten mounting bolts to specified torque (12 Nm)."
    )
    page2.insert_textbox(
        fitz.Rect(50, 95, 560, 210),
        step_text,
        fontsize=10,
        fontname="times-roman",
    )

    # Create and insert a synthetic RGB image (e.g. 120x80 color block schematic)
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 120, 80), 0)
    pix.set_rect(fitz.IRect(0, 0, 120, 80), (220, 240, 255))
    for x in range(30, 90):
        for y in range(20, 60):
            pix.set_pixel(x, y, (30, 100, 200))

    img_rect = fitz.Rect(50, 230, 170, 310)
    page2.insert_image(img_rect, pixmap=pix)

    page2.insert_text(
        fitz.Point(50, 325),
        "Figure 11-1: Thermostat Assembly and Jiggle Valve Orientation",
        fontsize=9,
        fontname="helv",
    )

    # Table text
    page2.insert_text(
        fitz.Point(50, 360),
        "Cooling System Service Specifications Table:",
        fontsize=11,
        fontname="helv",
    )

    table_text = (
        "Item                        | Specification | Limit\n"
        "----------------------------+---------------+---------------\n"
        "Thermostat Opening Valve    | 82 C (180 F)  | 80 - 84 C\n"
        "Thermostat Full Open Lift   | 8.5 mm or more| Min 8.0 mm\n"
        "Radiator Cap Relief Pressure| 108 kPa       | 93 - 123 kPa\n"
    )
    page2.insert_textbox(
        fitz.Rect(50, 375, 560, 470),
        table_text,
        fontsize=9,
        fontname="courier",
    )

    doc.save(str(output_path))
    doc.close()
    return output_path


if __name__ == "__main__":
    target = Path(__file__).parent / "sample_manual.pdf"
    generate_sample_manual_pdf(target)
    print(f"Generated fixture at: {target}")
