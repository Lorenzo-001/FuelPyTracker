import os
from datetime import datetime

from fpdf import FPDF
from sqlalchemy.orm import Session

from src.database import crud

# =============================================================================
# CLASSE ESTESA FPDF
# =============================================================================

class ServicePDF(FPDF):
    """
    Classe personalizzata per la generazione di PDF, estende FPDF.
    Gestisce layout standardizzati come Header con Logo/Fallback e Footer con disclaimer.
    """

    def header(self):
        """
        Definisce l'intestazione di ogni pagina del documento.
        Gestisce dinamicamente la presenza del logo aziendale o disegna un fallback geometrico.
        """
        # 1. Banda Superiore Decorativa
        self.set_fill_color(44, 62, 80)
        self.rect(0, 0, 210, 5, 'F')

        # 2. Risoluzione Percorsi Risorse
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
        logo_path = os.path.join(project_root, 'assets', 'logo.png')

        show_default_header = True

        # 3. Gestione Rendering Logo
        if os.path.exists(logo_path):
            try:
                # Rendering immagine (h=20 mantiene aspect ratio)
                self.image(logo_path, 10, 8, h=20)
                # Spaziatura verticale per evitare sovrapposizioni con il corpo
                self.ln(25) 
                show_default_header = False
            except Exception:
                # Fallback silenzioso in caso di file immagine corrotto
                show_default_header = True

        # 4. Gestione Rendering Intestazione Testuale (Fallback)
        if show_default_header:
            self._draw_geometric_logo()

            # Titolo Applicazione
            self.set_xy(25, 12)
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(44, 62, 80)
            self.cell(0, 12, 'FuelPyTracker', 0, 1, 'L')
            
            # Sottotitolo Descrittivo
            self.set_xy(25, 20)
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, 'Digital Maintenance Record System', 0, 1, 'L')
            
            self.ln(10)

    def _draw_geometric_logo(self):
        """Helper interno: Disegna un logo vettoriale geometrico (quadrato rosso) se manca l'immagine."""
        self.set_xy(10, 12)
        self.set_fill_color(231, 76, 60)
        self.set_draw_color(44, 62, 80)
        self.rect(10, 12, 12, 12, 'FD')
        
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 13)
        self.cell(12, 10, 'FPT', 0, 0, 'C')

    def footer(self):
        """
        Definisce il piè di pagina con disclaimer legale e numerazione.
        """
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y()) # Linea separatrice orizzontale
        
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        
        disclaimer = (
            "DOCUMENTO GENERATO AUTOMATICAMENTE. "
            "I dati riportati sono stati inseriti dall'utente e non costituiscono certificazione legale della casa madre."
        )
        self.cell(0, 5, disclaimer, 0, 1, 'C')
        self.cell(0, 5, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'R')

    def section_label(self, label, value):
        """
        Helper per renderizzare coppie 'Etichetta: Valore' con formattazione tecnica standardizzata.
        
        Args:
            label (str): L'etichetta del campo.
            value (Any): Il valore da visualizzare (viene sanificato e convertito).
        """
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(30, 6, label.upper(), 0, 0, 'L')
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        
        # Gestione encoding latin-1 per compatibilità font standard PDF
        try: 
            value = str(value).encode('latin-1', 'replace').decode('latin-1')
        except Exception: 
            pass
        self.cell(60, 6, value, 0, 0, 'L')


# =============================================================================
# LOGICA DI GENERAZIONE REPORT
# =============================================================================

def generate_maintenance_report(
    db: Session, 
    user_id: str, 
    owner_name: str, 
    plate: str, 
    car_model: str, 
    year: int = None
) -> bytes:
    """
    Orchestra la generazione del report di manutenzione in formato PDF.
    
    Args:
        db (Session): Sessione database attiva.
        user_id (str): ID dell'utente proprietario.
        owner_name (str): Nome visualizzato nel report.
        plate (str): Targa del veicolo.
        car_model (str): Modello del veicolo.
        year (int, optional): Anno per filtro report. Se None, genera storico completo.
        
    Returns:
        bytes: Il contenuto binario del file PDF generato.
    """

    # 1. Recupero e Filtraggio Dati
    # Ottiene tutti i record e applica filtri in memoria se necessario
    maintenances = crud.get_all_maintenances(db, user_id)
    
    if year:
        maintenances = [m for m in maintenances if m.date.year == year]
        report_title = f"REGISTRO MANUTENZIONE {year}"
    else:
        report_title = "STORICO MANUTENZIONE (COMPLETO)"

    # Ordinamento decrescente (dal più recente)
    maintenances.sort(key=lambda x: x.date, reverse=True)
    
    # Calcolo aggregati
    total_spent = sum(m.cost for m in maintenances)
    current_km = maintenances[0].total_km if maintenances else 0

    # 2. Inizializzazione PDF
    pdf = ServicePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # 3. Rendering Intestazione Report
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, report_title, 0, 1, 'C')
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Data emissione: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(5)

    # 4. Rendering Scheda Tecnica Veicolo
    # Creazione box con background grigio chiaro
    start_y = pdf.get_y()
    pdf.set_draw_color(180, 180, 180)
    pdf.set_fill_color(248, 249, 250) 
    pdf.rect(10, start_y, 190, 25, 'DF')
    
    pdf.set_xy(12, start_y + 3)
    
    def safe_text(text):
        """Helper locale per sanitizzazione encoding stringhe utente."""
        if not text: return ""
        try:
            return str(text).encode('latin-1', 'replace').decode('latin-1')
        except Exception:
            return str(text)

    # Riga 1: Dati Proprietario e Targa
    pdf.section_label("Proprietario:", safe_text(owner_name))
    pdf.set_x(110)
    pdf.section_label("Targa:", safe_text(plate.upper()))
    pdf.ln(8)
    
    # Riga 2: Dati Veicolo e KM
    pdf.set_x(12)
    pdf.section_label("Veicolo:", safe_text(car_model))
    pdf.set_x(110)
    pdf.section_label("KM Rilevati:", f"{current_km:,}".replace(',', '.'))
    pdf.ln(8)

    # Riga 3: Totali Finanziari
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(30, 6, "TOTALE SPESO:", 0, 0, 'L')
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(231, 76, 60)
    # Formattazione valuta manuale per evitare glifi non supportati
    pdf.cell(60, 6, f"{total_spent:,.2f} EUR".replace(',', 'X').replace('.', ',').replace('X', '.'), 0, 0, 'L')

    pdf.ln(15)

    # 5. Costruzione Tabella Interventi
    cols_w = [22, 22, 35, 30, 56, 25] 
    headers = ["DATA", "KM", "TIPO", "SCADENZA", "DESCRIZIONE", "COSTO"]
    
    # Rendering Header Tabella (Tutte le intestazioni centrate orizzontalmente)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_line_width(0.3)
    
    for i, h in enumerate(headers):
        pdf.cell(cols_w[i], 8, h, 1, align='C', fill=True)
    pdf.ln()

    # Rendering Corpo Tabella
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(0, 0, 0)
    fill = False
    
    # Caso Lista Vuota
    if not maintenances:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 10, "Nessun intervento registrato nel periodo selezionato.", 0, align='C')
    
    # Iterazione Righe
    for m in maintenances:
        date_str = m.date.strftime("%d/%m/%Y")
        km_str = f"{m.total_km:,}".replace(',', '.')
        
        # Logica stringa scadenza
        scad_str = "-"
        if m.expiry_km:
            scad_str = f"{m.expiry_km:,} km".replace(',', '.')
        elif m.expiry_date:
            scad_str = m.expiry_date.strftime("%d/%m/%y")
        
        note = safe_text(m.description or "-")
        tipo = safe_text(m.expense_type)
        cost_str = f"{m.cost:.2f}".replace('.', ',')

        # Calcolo righe necessarie per la descrizione
        pdf.set_font('Helvetica', '', 8)
        lines = pdf.multi_cell(cols_w[4], 4.5, note, dry_run=True, output="LINES")
        num_lines = max(1, len(lines))
        row_h = max(7.0, num_lines * 4.5 + 2.0)

        # Gestione automatica del salto pagina prima della riga
        if pdf.get_y() + row_h > pdf.page_break_trigger:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_fill_color(44, 62, 80)
            pdf.set_text_color(255, 255, 255)
            for i, h in enumerate(headers):
                pdf.cell(cols_w[i], 8, h, 1, align='C', fill=True)
            pdf.ln()
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(0, 0, 0)

        curr_x = pdf.get_x()
        curr_y = pdf.get_y()

        if fill:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)

        # Stampa celle con altezza coordinata row_h
        pdf.cell(cols_w[0], row_h, date_str, 'LRB', align='C', fill=fill)
        pdf.cell(cols_w[1], row_h, km_str, 'LRB', align='C', fill=fill)

        # Cella Tipo (grassetto)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(cols_w[2], row_h, tipo, 'LRB', align='L', fill=fill)
        pdf.set_font('Helvetica', '', 8)

        # Cella Scadenza
        pdf.cell(cols_w[3], row_h, scad_str, 'LRB', align='C', fill=fill)

        # Cella Descrizione Multilinea
        x_desc = pdf.get_x()
        y_desc = pdf.get_y()
        pdf.rect(x_desc, y_desc, cols_w[4], row_h, 'DF' if fill else 'D')
        pad_y = (row_h - (num_lines * 4.5)) / 2
        pdf.set_xy(x_desc, y_desc + pad_y)
        pdf.multi_cell(cols_w[4], 4.5, note, border=0, align='L')
        pdf.set_xy(x_desc + cols_w[4], y_desc)

        # Cella Costo (allineata a destra)
        pdf.cell(cols_w[5], row_h, cost_str, 'LRB', align='R', fill=fill)

        pdf.set_xy(10, curr_y + row_h)
        fill = not fill # Toggle colore riga

    # 6. Rendering Totale Finale
    if maintenances:
        pdf.set_font('Helvetica', 'B', 8)
        total_width_labels = sum(cols_w[:-1])
        pdf.cell(total_width_labels, 7, "TOTALE PERIODO", 1, align='R')
        pdf.cell(cols_w[-1], 7, f"{total_spent:,.2f}".replace('.', ','), 1, align='R', fill=True)

    return bytes(pdf.output())