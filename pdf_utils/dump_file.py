import pdfrw
import sys

# PDF Format Keys
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_FIELD_TYPE = '/FT'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
PARENT_KEY = '/Parent'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

def dump_fields(fp):
    '''
    Helper function to print out different fields in a PDF.

    Useful for generating keyfiles, debugging, etc.
    '''

    template_pdf = pdfrw.PdfReader(fp)
    annotations = template_pdf.pages[0][ANNOT_KEY]
    
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        print(annotations)
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    type = annotation[ANNOT_FIELD_TYPE]
                    print (key, type)
                else:
                    print ('NOT ANNOT FIELD KEY')
                    if annotation['/AS']:
                        print ('Button', annotation['/AP']['/D'].keys(), annotation[PARENT_KEY][ANNOT_FIELD_KEY])
                    else:
                        print ('Text: ', annotation[PARENT_KEY][ANNOT_FIELD_KEY])
                        print (annotation[PARENT_KEY][ANNOT_VAL_KEY])

if __name__ == '__main__':
    dump_fields(sys.argv[1])
