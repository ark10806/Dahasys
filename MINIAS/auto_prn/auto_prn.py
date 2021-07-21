from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import xls_path as param

def read_pdf_PDFMINER(pdf_file_path):
    output_string = StringIO()
    print(pdf_file_path)
    with open(pdf_file_path, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    # return str(output_string.getvalue())
    arr = output_string.getvalue().split('\n')

    sem_idx = [3, 5, 13, 15, 29, 30, 32, 33, 35, 37, 39, 41]
    sem = []
    for i in sem_idx:
        sem.append(arr[i].strip())
    
    return sem

def main():
    arr = read_pdf_PDFMINER(param.PATH_pdf)

    for i, e in enumerate(arr):
        print(f'[{i}]:{e}')

if __name__ == '__main__':
    main()
