import PyPDF2

class PdfToTextLoader:
    """
    Class for loading PDFs and saving them as text files.
    """

    def __init__(self, pdf_path, output_path):
        """
        Args:
            pdf_path (str): Path to PDF file.
            output_path (str): Path to save the text file.
        """
        self.pdf_path = pdf_path
        self.output_path = output_path

    def load_pdf(self):
        """
        Loads PDF file and saves it as a text file.
        """
        try:
            print(f"Loading PDF from: {self.pdf_path}")
            with open(self.pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                num_pages = pdf_reader.numPages
                text = ''
                for page_num in range(num_pages):
                    page = pdf_reader.getPage(page_num)
                    text += page.extractText()
                
            print(f"Saving text to: {self.output_path}")
            with open(self.output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)
            
            return text
        except Exception as e:
            print(f"Error: {str(e)}")
            return str(e)
