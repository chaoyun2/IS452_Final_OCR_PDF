from fpdf import FPDF
import os
import glob
import pytesseract
from PIL import Image
from PyPDF2 import PdfFileMerger, PdfFileReader
from collections import OrderedDict


def detect_confirm_image():
    # InputType: None
    # ReturnType:List
    # Functionality: detect all image files in current folder, and return their names as a list
    print('Step 1: Detecting image files in current folder (searching for jpg, png and jpeg)')
    files = []
    # Support image file format: jpg, png and jpeg
    for file_type in ['*.jpg', '*.png', '*.jpeg']:
        files.extend(glob.glob(file_type))
    print(' Totally {0} Image Files were detected for processing:'.format(len(files)))
    for num, file in enumerate(files):
        print('  {0}: {1}'.format(num+1, file))

    # Confirm with user whether the file list is good to go
    confirm = input('Continue? (Y/N):')
    return sorted(files) if confirm[0].upper() == 'Y' else None


def ocr_image_text(files):
    # InputType: List
    # ReturnType:Dictionary
    # Functionality: use pytesseract to recognize text in all images, save those text in a Dictionary and make the
    #   file name as key. Return the Dictionary.
    print('\nStep 2: Extracting text from Image files...')
    # use OrderedDict to track the text data, thus the output PDF will be well ordered
    text_dic = OrderedDict()
    length = len(files)
    for num, file in enumerate(files):
        # Print a notice line once start processing a new file
        print(' Recognizing text in image {0}, {1} files remaining...'.format(file, length - num - 1))
        pic = Image.open(os.path.abspath(file))
        # pytesseract converting text from image to string
        text_dic[file] = pytesseract.image_to_string(pic, lang = 'eng')
    print('Finishing step 2 and creating export_image.pdf')
    return text_dic


class PDF(FPDF):
    # This is the class of PDF, it was build on FPDF.
    # Major functions: write PDF footer, write image to PDF, write text to PDF, generate PDF content and merge PDF.
    def footer(self):
        # InputType: self
        # ReturnType:None
        # Functionality: Define the footer for PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def w_image(self, files):
        # InputType: self, List
        # ReturnType:No Return, will write a PDF of converted images
        # Functionality: Converting images to one single PDF "export_image.pdf"
        print('\nStep3: Converting original images to PDF...')
        for image in files:
            print(' Converting {0}...'.format(image))
            self.add_page()
            self.alias_nb_pages()
            self.set_font('Times', 'B', 15)
            self.set_fill_color(r=160)
            self.set_y(0)
            self.cell(w=200, h=5, txt=image, border=0, ln=1, align='C', fill=1)
            self.image(image, y=5, w=210, h=297)
        print('Finishing step 3 and creating export_image.pdf...')
        self.output("export_image.pdf", "F")
        self.close()

    def w_text(self, ocr_dic):
        # InputType: self, Dictionary
        # ReturnType: List
        # Functionality: Write recognized text from images to PDF "export_text.pdf", Return content information for
        #   further content creation
        self.alias_nb_pages()
        content_record = []

        for title, text in ocr_dic.items():
            print(' Converting text in {0}...'.format(title))
            self.add_page()
            content_record.append(title.lower().ljust(84, '*') + str(self.page_no()) + '\n')
            self.set_font('Times', 'B', 15)
            self.set_fill_color(r=160)
            self.set_y(0)
            self.cell(w=210, h=9, txt=title, border=0, ln=1, align='C', fill=1)
            self.set_font('Times', '', 12)
            self.multi_cell(w=0, h=5, txt=text)
        self.output("export_text.pdf")
        self.close()
        return content_record

    def w_content(self, content_record):
        # InputType: self, List
        # ReturnType: No return, will create a content PDF "export_content.pdf" based on recognized text PDF
        # Functionality: Create content PDF for better indexing page number of desired image text.
        print(' Creating content for recognized images...')
        pdf_content = FPDF()
        pdf_content.add_page()
        pdf_content.set_font('Times', 'B', 18)
        pdf_content.set_fill_color(r=160)
        pdf_content.cell(w=180, h=9, txt='CONTENT', border=0, ln=1, align='C', fill=1)
        pdf_content.set_font('Times', '', 12)
        pdf_content.multi_cell(w=0, h=5, txt=''.join(content_record))
        pdf_content.output("export_content.pdf")
        pdf_content.close()

    def w_ocr(self, ocr_dic):
        # InputType: self, Dictionary
        # ReturnType: No return, will create a PDF from merging "export_content.pdf" and "export_text.pdf"
        # Functionality: Merging PDFs
        print('\nStep4: Converting recognized text to PDF...')
        pdfs = ['export_content.pdf', 'export_text.pdf']
        merger = PdfFileMerger()
        # Get content information and create text PDF
        content_record = self.w_text(ocr_dic)
        # create content PDF
        self.w_content(content_record)

        for pdf in pdfs:
            f = open(pdf, 'rb')
            merger.append(PdfFileReader(f))
            f.close()

        with open('export_OCR.pdf', 'wb') as fout:
            merger.write(fout)

        merger.close()

        print('Finishing step 4 and creating export_OCR.pdf...')


def clean_tmp_files():
    # InputType: None
    # ReturnType: None
    # Functionality: Remove PDFs, because they have been merged to another new PDF
    os.remove('export_content.pdf')
    os.remove('export_text.pdf')


def main():
    files = detect_confirm_image()
    if files:
        text_dic = ocr_image_text(files)
        pdf_image = PDF()
        pdf_image.w_image(files)
        pdf_ocr = PDF()
        pdf_ocr.w_ocr(text_dic)
        clean_tmp_files()
        print('\nPDF Converting process completed successfully, PDF created: ')
        print(' export_image.pdf: Converted original images, one per page')
        print(' export_OCR.pdf: Converted recognized text in images with content')
    else:
        print('\nProcess terminated from user.')


main()

