import os 
import sys
from xlsx_parse import XlsxParse
from graph_manage import GraphManager


def main(xlsxpath):
    xlsx_parse = XlsxParse(xlsxpath)
    gm = GraphManager()
    gm.add_fixed_node()
    doc_info = xlsx_parse.get_doc_info()
    gm.add_doc_info(doc_info)
    requirement_info = xlsx_parse.get_requirement_info()
    gm.add_requirement_info(requirement_info)
    


if __name__ == '__main__':
    main(sys.argv[1])