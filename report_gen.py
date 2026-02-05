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
C_TEXT = (30, 30, 30)  # Body Text


def to_hex(rgb): return '#%02x%02x%02x' % rgb


class StrategicReport(FPDF):
    def header(self):
        # Brand Strip
        self.set_fill_color(*C_NAVY)
        self.rect(0, 0, 210, 20, 'F')

        # Title
        self.set_font('helvetica', 'B', 14)
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
        """Sanitizes text to prevent crashes and removes junk."""
        if not isinstance(text, str): text = str(text)

        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)

        replacements = {
            '≈': '~=', '≠': '!=', '≤': '<=', '≥': '>=',
            '—': '-', '–': '-', '“': '"', '”': '"',
            '’': "'", '‘': "'", '…': '...', '•': '-',
            '−': '-', '×': 'x', '**': '', '__': '', '*': ''
        }
        for char, sub in replacements.items():
            text = text.replace(char, sub)

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

    def render_table(self, table_lines):
        data = []
        for line in table_lines:
            if '---' in line: continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 2: data.append(cells[:2])

        if not data: return

        self.ln(2)
        row_height = 6
        col_w = [45, 75]

        self.set_font('helvetica', 'B', 9)
        self.set_fill_color(240, 245, 255)
        self.set_text_color(*C_NAVY)

        if len(data) > 0:
            x_start = self.get_x()
            self.cell(col_w[0], 8, self.safe_text(data[0][0]), 1, 0, 'L', 1)
            self.cell(col_w[1], 8, self.safe_text(data[0][1]), 1, 1, 'L', 1)

        self.set_font('helvetica', '', 9)
        self.set_text_color(*C_TEXT)

        for row in data[1:]:
            x_curr = self.get_x()
            y_curr = self.get_y()
            self.multi_cell(col_w[0], row_height, self.safe_text(row[0]), 1, 'L')
            h1 = self.get_y() - y_curr
            self.set_xy(x_curr + col_w[0], y_curr)
            self.multi_cell(col_w[1], row_height, self.safe_text(row[1]), 1, 'L')
            h2 = self.get_y() - y_curr
            self.set_xy(x_curr, y_curr + max(h1, h2))

        self.ln(5)

    def write_smart_content(self, text):
        self.set_left_margin(10)
        self.set_right_margin(80)
        self.set_y(25)

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = self.safe_text(lines[i].strip())

            if not line:
                i += 1;
                self.ln(2);
                continue

            # TABLE
            if line.startswith('|'):
                table_buffer = [line]
                i += 1
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_buffer.append(lines[i].strip())
                    i += 1
                self.render_table(table_buffer)
                continue

            # HEADER
            if line.startswith('#') or (len(line) < 60 and line.isupper()):
                clean = line.lstrip('#').strip()
                self.ln(5)
                self.set_font('helvetica', 'B', 12)
                self.set_text_color(*C_NAVY)
                self.cell(0, 8, clean, 0, 1)
                self.ln(2)
                i += 1
                continue

            # KEY-VALUE (Bold Labels)
            split_match = re.match(r'^([^:]+):(.+)', line)
            if split_match:
                label = split_match.group(1).strip() + ":"
                val = split_match.group(2).strip()

                if len(label) < 60:
                    self.set_font('helvetica', 'B', 10)
                    self.set_text_color(*C_NAVY)
                    self.write(5, label + " ")

                    self.set_font('helvetica', '', 10)
                    self.set_text_color(*C_TEXT)
                    self.write(5, val)
                    self.ln(5)
                    i += 1
                    continue

            # BULLETS
            if line.startswith(('*', '-', '•')):
                clean = line.lstrip('*-• ').strip()
                self.set_x(15)
                self.set_font('helvetica', '', 10)
                self.set_text_color(*C_TEXT)
                self.cell(5, 5, chr(149), 0, 0)
                # FIX 1: Justified Bullets
                self.multi_cell(110, 5, clean, align='J')
                self.ln(2)
                i += 1
                continue

            # NORMAL TEXT
            self.set_font('helvetica', '', 10)
            self.set_text_color(*C_TEXT)
            # FIX 1: Justified Paragraphs
            self.multi_cell(120, 5, line, align='J')
            self.ln(1)
            i += 1


def generate_pdf(metrics, ai_summary):
    pdf = StrategicReport()
    pdf.add_page()

    # 1. SIDEBAR
    pdf.draw_sidebar(metrics)

    # 2. CONTENT
    pdf.write_smart_content(ai_summary)

    # 3. CHART
    needed = 90
    if pdf.get_y() + needed > 280: pdf.add_page()

    # FIX 2: Dynamic position, NO max() forcing it to bottom
    chart_y = pdf.get_y() + 10
    pdf.set_y(chart_y)

    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(100, 6, "CAPACITY RISK DISTRIBUTION", 0, 1)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 190, pdf.get_y())  # Full width line
    pdf.ln(2)

    try:
        mu = metrics.get('avg_demand', 100)
        sigma = metrics.get('std_dev', 20)
        cap = mu + metrics.get('safety_stock', 0)

        x = np.linspace(mu - 4.5 * sigma, mu + 4.5 * sigma, 300)
        y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

        # High Res, Expanded
        plt.figure(figsize=(10, 4))
        plt.subplots_adjust(bottom=0.2, left=0.08, right=0.95, top=0.9)

        plt.plot(x, y, color=to_hex(C_NAVY), linewidth=2.5)

        x_safe = np.linspace(x[0], cap, 200)
        y_safe = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_safe - mu) / sigma) ** 2)
        plt.fill_between(x_safe, y_safe, color='#E6F0FF', alpha=1)

        x_risk = np.linspace(cap, x[-1], 100)
        y_risk = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_risk - mu) / sigma) ** 2)
        plt.fill_between(x_risk, y_risk, color='#FFE6E6', alpha=1)

        plt.axvline(cap, color=to_hex(C_ACCENT), linestyle='--', linewidth=2)

        # FIX 3: BOTH LABELS LIGHT (No Bold)
        plt.xlabel('Demand Volume (Units)', fontsize=11)
        plt.ylabel('Probability', fontsize=11)

        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(True)
        ax.spines['left'].set_color('#BBBBBB')
        ax.spines['bottom'].set_color('#BBBBBB')

        ax.get_yaxis().set_visible(True)
        ax.tick_params(axis='both', colors='#444444', labelsize=10)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            plt.savefig(tmp.name, dpi=300, bbox_inches='tight')
            img_path = tmp.name

        # Wide Placement
        pdf.image(img_path, x=10, w=180)
        plt.close()
        os.unlink(img_path)
    except:
        pdf.cell(0, 10, "Visualization Unavailable", 0, 1)

    return bytes(pdf.output(dest='S'))