import aspose.words as aw
import PyPDF2


# Load word document
doc = aw.Document("текст к презентации.docx")
# Save as PDF
doc.save("PDF.pdf")


file = open('PDF.pdf', 'rb')
readpdf = PyPDF2.PdfFileReader(file)
totalpages = readpdf.numPages
print(totalpages)
