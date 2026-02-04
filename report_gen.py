from fpdf import FPDF
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
import re
from datetime import datetime

# --- STRATEGIC THEME ---
C_NAVY = (0, 45, 98)  # Headers
C_GREY_BG = (245, 245, 245)  # Sidebar
C_ACCENT = (180, 0, 0)  # Alerts
C_TEXT = (40, 40, 40)  # Body


def to_hex(rgb): return '#%02x%02x%02x' % rgb


class StrategicReport(FPDF):
    def header(self):
        # Brand Strip
        self.set_fill_color(*C_NAVY)
        self.rect(0, 0, 210, 20, 'F')

        # Title
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, "STRATEGIC CAPACITY & RISK ASSESSMENT", 0, 0, 'L')

        # Subtitle
        self.set_font('helvetica', '', 9)
        self.set_xy(0, 6)
        self.cell(200, 10, f"{datetime.now().strftime('%d %B %Y').upper()} | CONFIDENTIAL", 0, 0, 'R')
        self.ln(25)

    def footer(self):
        self.set_y(-12)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def safe_text(self, text):
        """Sanitizes text to prevent crashes and removes junk markdown links."""
        if not isinstance(text, str):
            text = str(text)

        # 1. Remove Markdown Links/Images
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)

        # 2. Symbol Replacements
        replacements = {
            '≈': '~=', '≠': '!=', '≤': '<=', '≥': '>=',
            '—': '-', '–': '-', '“': '"', '”': '"',
            '’': "'", '‘': "'", '…': '...', '•': '-',
            '−': '-', '×': 'x'
        }
        for char, sub in replacements.items():
            text = text.replace(char, sub)

        # 3. Encoding Safety
        return text.encode('latin-1', 'replace').decode('latin-1')

    def draw_sidebar(self, metrics):
        """Permanent Right Sidebar"""
        x_base = 140
        y_base = 20
        w = 70
        h = 277

        self.set_fill_color(*C_GREY_BG)
        self.rect(x_base, y_base, w, h, 'F')

        curr_y = y_base + 10
        pad = x_base + 6

        def sb_header(txt):
            nonlocal curr_y
            self.set_xy(pad, curr_y)
            self.set_font('helvetica', 'B', 9)
            self.set_text_color(*C_NAVY)
            self.cell(w - 10, 6, self.safe_text(txt.upper()), 0, 2)
            self.set_draw_color(*C_NAVY)
            self.line(pad, curr_y + 6, pad + w - 12, curr_y + 6)
            curr_y += 10

        def sb_row(label, val, bold=False, col=C_TEXT):
            nonlocal curr_y
            self.set_xy(pad, curr_y)
            self.set_font('helvetica', '', 9)
            self.set_text_color(80, 80, 80)
            self.cell(32, 5, self.safe_text(label), 0, 0)
            self.set_font('helvetica', 'B' if bold else '', 9)
            self.set_text_color(*col)
            self.cell(25, 5, self.safe_text(str(val)), 0, 1, 'R')
            curr_y += 7

        sb_header("CONFIGURATION")
        sb_row("Mode", metrics.get('transport_mode', 'Road'))
        sb_row("SLA Target", f"{metrics.get('sla', 0.95):.1%}")

        sb_header("OPERATIONS")
        sb_row("Avg Demand", metrics.get('avg_demand', 0))
        sb_row("Volatility", f"{metrics.get('std_dev', 0)} (sd)")
        sb_row("Safety Stock", metrics.get('safety_stock', 0), True, C_ACCENT)

        sb_header("RISK PROFILE")
        res = metrics.get('resilience_score', 0)
        c_res = (0, 100, 0) if res > 70 else C_ACCENT
        sb_row("Resilience", f"{res}/100", True, c_res)
        sb_row("Dependency", f"{metrics.get('dependency_ratio', 0):.1f}%")

        sb_header("IMPACT")
        sb_row("CO2 (kg)", f"{metrics.get('co2_emissions', 0):.0f}")
        sb_row("Loyalty", f"{metrics.get('loyalty_score', 0):.0f}")

    def render_custom_table(self, lines, x_start, col_width):
        """Renders a parsed markdown table as a real PDF grid"""
        self.set_x(x_start)
        self.set_font('helvetica', '', 8)

        data = []
        for line in lines:
            if '---' in line: continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 2:
                data.append(cells[:2])

        if not data: return

        row_height = 6
        w_col1 = 40
        w_col2 = col_width - w_col1

        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.1)

        for idx, row in enumerate(data):
            x_curr = self.get_x()
            y_curr = self.get_y()

            is_header = (idx == 0 and row[0].lower() == 'metric')
            fill = is_header
            if is_header: self.set_fill_color(240, 245, 255)

            # Key Column (Always Navy)
            self.set_font('helvetica', 'B', 8)
            self.set_text_color(*C_NAVY)
            self.multi_cell(w_col1, row_height, self.safe_text(row[0]), border=1, align='L', fill=fill)
            h1 = self.get_y() - y_curr

            # Value Column (Navy if header, else Text)
            self.set_xy(x_curr + w_col1, y_curr)
            self.set_font('helvetica', 'B' if is_header else '', 8)

            # --- FIX: Correct unpacking logic ---
            col_color = C_NAVY if is_header else C_TEXT
            self.set_text_color(*col_color)

            self.multi_cell(w_col2, row_height, self.safe_text(row[1]), border=1, align='L', fill=fill)
            h2 = self.get_y() - y_curr

            self.set_xy(x_start, y_curr + max(h1, h2))

        self.ln(5)

    def write_smart_content(self, text):
        """Parses Markdown and renders stylized PDF elements"""
        self.set_left_margin(10)
        self.set_right_margin(80)
        self.set_y(25)

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1;
                continue

            # 1. TABLE DETECTION
            if line.startswith('|'):
                table_buffer = [line]
                i += 1
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_buffer.append(lines[i].strip())
                    i += 1
                self.render_custom_table(table_buffer, 10, 120)
                continue

            # 2. KEY-VALUE PAIR DETECTION
            # Catches lines like "Metric" followed by "Value" in AI output
            if line == 'Metric' and i + 1 < len(lines) and lines[i + 1].strip() == 'Value':
                i += 2  # Skip headers
                data = []
                while i < len(lines):
                    key_line = lines[i].strip()
                    if not (key_line.startswith('**') and key_line.endswith('**')): break
                    key = key_line[2:-2].strip()
                    i += 1
                    if i >= len(lines): break
                    val_line = lines[i].strip()
                    data.append([key, val_line])
                    i += 1
                if data:
                    # Reconstruct as table rows
                    table_lines = ['| Metric | Value |'] + [f'| {k} | {v} |' for k, v in data]
                    self.render_custom_table(table_lines, 10, 120)
                continue

            # 3. HEADER DETECTION
            clean_line = line.replace('**', '').replace('__', '').replace('`', '')
            if line.startswith('#') or (len(clean_line) < 60 and clean_line.isupper()):
                clean_line = clean_line.lstrip('#').strip()
                self.ln(6)
                self.set_fill_color(240, 245, 255)
                self.rect(10, self.get_y(), 120, 8, 'F')
                self.set_xy(12, self.get_y() + 1.5)
                self.set_font('helvetica', 'B', 10)
                self.set_text_color(*C_NAVY)
                self.cell(0, 5, self.safe_text(clean_line.upper()), 0, 1)
                self.ln(2)

            # 4. BULLET DETECTION
            elif line.startswith(('* ', '- ', '•')):
                clean_line = clean_line.lstrip('*-• ').strip()
                self.set_x(15)
                self.set_font('helvetica', '', 11)
                self.set_text_color(*C_TEXT)
                self.cell(5, 6, '-', 0, 0)
                self.multi_cell(110, 6, self.safe_text(clean_line))
                self.ln(1)

            # 5. NORMAL PARAGRAPH
            else:
                self.set_font('helvetica', '', 11)
                self.set_text_color(*C_TEXT)
                self.multi_cell(120, 6, self.safe_text(clean_line))
                self.ln(3)
            i += 1


def generate_pdf(metrics, ai_summary):
    pdf = StrategicReport()
    pdf.add_page()

    # 1. SIDEBAR
    pdf.draw_sidebar(metrics)

    # 2. MAIN CONTENT
    pdf.write_smart_content(ai_summary)

    # 3. CHART (Bottom Left - Fixed)
    needed_height = 80
    if pdf.get_y() + needed_height > 280:
        pdf.add_page()
        # Optional: draw sidebar again on page 2
        # pdf.draw_sidebar(metrics)

    chart_y = max(pdf.get_y() + 10, 200)  # Minimum Y
    pdf.set_y(chart_y)

    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(100, 6, "CAPACITY RISK DISTRIBUTION", 0, 1)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 130, pdf.get_y())
    pdf.ln(2)

    try:
        mu = metrics.get('avg_demand', 100)
        sigma = metrics.get('std_dev', 20)
        cap = mu + metrics.get('safety_stock', 0)

        x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 300)
        y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

        plt.figure(figsize=(7, 3.5))
        plt.subplots_adjust(bottom=0.25, left=0.15, right=0.95, top=0.95)

        plt.plot(x, y, color=to_hex(C_NAVY), linewidth=2)

        x_safe = np.linspace(x[0], cap, 200)
        y_safe = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_safe - mu) / sigma) ** 2)
        plt.fill_between(x_safe, y_safe, color='#E6F0FF', alpha=1, label="Covered")

        x_risk = np.linspace(cap, x[-1], 100)
        y_risk = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_risk - mu) / sigma) ** 2)
        plt.fill_between(x_risk, y_risk, color='#FFE6E6', alpha=1, label="Risk")

        plt.axvline(cap, color=to_hex(C_ACCENT), linestyle='--', linewidth=1.5)

        plt.xlabel('Demand Volume (Units)')
        # Clean up
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_yaxis().set_visible(False)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            plt.savefig(tmp.name, dpi=150)
            img_path = tmp.name

        pdf.image(img_path, x=10, w=120)
        plt.close()
        os.unlink(img_path)
    except:
        pdf.cell(0, 10, "Visualization Error", 0, 1)

    return bytes(pdf.output(dest='S'))