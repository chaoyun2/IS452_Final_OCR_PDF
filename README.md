# IS452_Final_OCR_PDF
This is the final project of IS452: converting images to PDF and support OCR features.


## Prerequisites
Python3+

python packages:
  
* PIL:`pip install pillow`
* pytesseract: `pip install pytesseract`
* fpdf: `pip install fpdf`
* pypdf2: `pip install pypdf2`

tesseract-OCR: please find its github for installing information [HERE](https://github.com/tesseract-ocr/tesseract/wiki/Downloads).
After installation, you should also add the installed directory to PATH. This is important, because this is the only way to have "pytesseart" and "tesseract-OCR" bind together.

## How to use the program
The source code is "chaoyun2_image_OCR_PDF.py". It will process image files in its execution folder and generate two PDF. For test purpose, please put all these provided png files and .py file in the same folder and execute the program.  
At first, you will see the program scaned the current folder and print out all image file names and waiting for user confirmation. Please enter "Y" for continue or "N" for termination. The program will keep reporting status along the process pipline till the end of execution and export final two PDF.
