import os
from fpdf import FPDF
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import crud

class ServicePDF(FPDF):
    def header(self):
        # --- BANDA SUPERIORE ---
        self.set_fill_color(44, 62, 80)
        self.rect(0, 0, 210, 5, 'F')

        # --- GESTIONE LOGO ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
        logo_path = os.path.join(project_root, 'assets', 'logo.png')

        show_default_header = True

        if os.path.exists(logo_path):
            # LOGO REALE (Sostituisce Titolo e Sottotitolo)
            try:
                # Usiamo h=20 per fissare l'altezza e mantenere le proporzioni (evita distorsioni)
                # x=10, y=8 posiziona l'immagine subito sotto la banda superiore
                self.image(logo_path, 10, 8, h=20)
                # Aggiungiamo uno spazio verticale per staccare il contenuto dal logo
                self.ln(25) 
                show_default_header = False
            except:
                # Se l'immagine è corrotta, fallback al default
                show_default_header = True

        if show_default_header:
            # --- LAYOUT PREDEFINITO (Fallback) ---
            self._draw_geometric_logo()

            # Titolo App
            self.set_xy(25, 12)
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(44, 62, 80)
            self.cell(0, 12, 'FuelPyTracker', 0, 1, 'L')
            
            # Sottotitolo
            self.set_xy(25, 20)
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, 'Digital Maintenance Record System', 0, 1, 'L')
            
            self.ln(10)

    def _draw_geometric_logo(self):
        """Disegna il quadrato rosso FPT se manca l'immagine"""
        self.set_xy(10, 12)
        self.set_fill_color(231, 76, 60)
        self.set_draw_color(44, 62, 80)
        self.rect(10, 12, 12, 12, 'FD')
        
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 13)
        self.cell(12, 10, 'FPT', 0, 0, 'C')

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y()) # Linea separatrice
        
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        
        disclaimer = (
            "DOCUMENTO GENERATO AUTOMATICAMENTE. "
            "I dati riportati sono stati inseriti dall'utente e non costituiscono certificazione legale della casa madre."
        )
        self.cell(0, 5, disclaimer, 0, 1, 'C')
        self.cell(0, 5, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'R')

    def section_label(self, label, value):
        """Helper per stampare coppie Etichetta: Valore in stile tecnico"""
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(30, 6, label.upper(), 0, 0, 'L')
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        # Usiamo decode per gestire caratteri speciali se necessario
        try: 
            value = str(value).encode('latin-1', 'replace').decode('latin-1')
        except: 
            pass
        self.cell(60, 6, value, 0, 0, 'L')

def generate_maintenance_report(db: Session, user_id: str, owner_name: str, plate: str, car_model: str, year: int = None) -> bytes:
    # 1. Recupero Dati
    maintenances = crud.get_all_maintenances(db, user_id)
    
    # Filtro Anno
    if year:
        maintenances = [m for m in maintenances if m.date.year == year]
        report_title = f"REGISTRO MANUTENZIONE {year}"
    else:
        report_title = "STORICO MANUTENZIONE (COMPLETO)"

    # Ordine Cronologico
    maintenances.sort(key=lambda x: x.date, reverse=True)
    
    total_spent = sum(m.cost for m in maintenances)
    current_km = maintenances[0].total_km if maintenances else 0

    # 2. Setup PDF
    pdf = ServicePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # --- INTESTAZIONE DOCUMENTO ---
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, report_title, 0, 1, 'C')
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Data emissione: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(5)

    # --- SCHEDA TECNICA VEICOLO ---
    start_y = pdf.get_y()
    pdf.set_draw_color(180, 180, 180)
    pdf.set_fill_color(248, 249, 250) 
    pdf.rect(10, start_y, 190, 25, 'DF')
    
    pdf.set_xy(12, start_y + 3)
    
    # Encoding sicuro per le stringhe utente (gestisce accenti e caratteri strani)
    def safe_text(text):
        if not text: return ""
        try:
            return str(text).encode('latin-1', 'replace').decode('latin-1')
        except:
            return str(text)

    # Riga 1
    pdf.section_label("Proprietario:", safe_text(owner_name))
    pdf.set_x(110)
    pdf.section_label("Targa:", safe_text(plate.upper()))
    pdf.ln(8)
    
    # Riga 2
    pdf.set_x(12)
    pdf.section_label("Veicolo:", safe_text(car_model))
    pdf.set_x(110)
    pdf.section_label("KM Rilevati:", f"{current_km:,}".replace(',', '.'))
    pdf.ln(8)

    # Riga 3
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(30, 6, "TOTALE SPESO:", 0, 0, 'L')
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(231, 76, 60)
    # Usa EUR invece del simbolo € per evitare crash font
    pdf.cell(60, 6, f"{total_spent:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'), 0, 0, 'L')

    pdf.ln(15)

    # --- TABELLA INTERVENTI ---
    cols_w = [25, 25, 40, 70, 30]
    
    # *** CORREZIONE QUI SOTTO: Modificato "COSTO (€)" in "COSTO (EUR)" ***
    headers = ["DATA", "KM", "TIPO INTERVENTO", "DESCRIZIONE / NOTE", "COSTO (EUR)"]
    
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_line_width(0.3)
    
    for i, h in enumerate(headers):
        align = 'R' if i == 4 else 'C' if i < 2 else 'L'
        pdf.cell(cols_w[i], 8, h, 1, 0, align, True)
    pdf.ln()

    # Body Tabella
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(0, 0, 0)
    fill = False
    
    if not maintenances:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 10, "Nessun intervento registrato nel periodo selezionato.", 0, 1, 'C')
    
    for m in maintenances:
        pdf.set_fill_color(245, 245, 245)
        
        date_str = m.date.strftime("%d/%m/%Y")
        km_str = str(m.total_km)
        
        # Pulizia stringhe note e tipo
        note = safe_text(m.description or "")
        if len(note) > 45: note = note[:42] + "..."
        
        tipo = safe_text(m.expense_type)
        if len(tipo) > 22: tipo = tipo[:20] + ".."

        cost_str = f"{m.cost:.2f}".replace('.', ',')

        pdf.cell(cols_w[0], 7, date_str, 'LRB', 0, 'C', fill)
        pdf.cell(cols_w[1], 7, km_str, 'LRB', 0, 'C', fill)
        
        current_font = pdf.font_style
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(cols_w[2], 7, tipo, 'LRB', 0, 'L', fill)
        pdf.set_font('Helvetica', '', 8)
        
        pdf.cell(cols_w[3], 7, note, 'LRB', 0, 'L', fill)
        pdf.cell(cols_w[4], 7, cost_str, 'LRB', 0, 'R', fill)
        
        pdf.ln()
        fill = not fill

    # Totale fondo pagina
    if maintenances:
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(sum(cols_w[:-1]), 7, "TOTALE PERIODO", 1, 0, 'R')
        pdf.cell(cols_w[-1], 7, f"{total_spent:,.2f}".replace('.', ','), 1, 0, 'R', True)

    return bytes(pdf.output())