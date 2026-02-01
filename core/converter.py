
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml.text.run import CT_R
from docx.text.run import Run
from .reorder import ReorderEngine

class DocxConverter:
    def __init__(self):
        self.engine = ReorderEngine()

    def convert_file(self, input_path, output_path):
        doc = Document(input_path)
        
        # Process Document Body
        for para in doc.paragraphs:
            self.process_paragraph(para)
            
        # Process Tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self.process_paragraph(para)
                        
        doc.save(output_path)

    def process_paragraph(self, para):
        # Iterate over all children to catch Runs AND Hyperlinks
        for item in para._element:
            if isinstance(item, CT_R): # It's a normal Run
                run = Run(item, para)
                self.process_run(run)
            elif item.tag.endswith('hyperlink'): # It's a Hyperlink, which contains runs
                for child in item:
                    if isinstance(child, CT_R):
                        run = Run(child, para)
                        self.process_run(run)

    def process_run(self, run):
        if run.text:
            text = run.text
            
            if not text.strip():
                return  # Don't touch empty/whitespace runs
            
            # Check if text contains any Devanagari characters
            # Devanagari Unicode range: U+0900 to U+097F
            has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
            
            if not has_devanagari:
                # Pure English/ASCII text - leave it unchanged, don't change font
                return
            
            try:
                converted_text = self.engine.process(text)
                run.text = converted_text
            except Exception as e:
                print(f"Conversion skipped for run due to error: {e}")
                return
            
            # Only set Kruti font for converted (Hindi) text
            self.set_kruti_font(run)

    def set_kruti_font(self, run):
        run.font.name = 'Kruti Dev 010'
        # Force XML properties for all font types (important for Word)
        rPr = run._element.get_or_add_rPr()
        fonts = rPr.get_or_add_rFonts()
        
        fonts.set(qn('w:ascii'), 'Kruti Dev 010')
        fonts.set(qn('w:hAnsi'), 'Kruti Dev 010')
        fonts.set(qn('w:cs'), 'Kruti Dev 010')
        fonts.set(qn('w:eastAsia'), 'Kruti Dev 010')
