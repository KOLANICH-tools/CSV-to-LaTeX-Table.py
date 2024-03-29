#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from optparse import OptionParser
import re
import codecs
from warnings import warn

warn("We have moved from M$ GitHub to https://codeberg.org/KOLANICH-tools/CSV-to-LaTeX-Table.py , read why on https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo .")

class Parser(object):

    def filter_characters(self,word):
        '''Remove or escape certain characters so that they don't get inserted into the table'''
        remove = ["\n","\r"]
        for r in remove:
            word = word.replace(r,"")
        return word
    
    def indent(self,level):
        if not self.options.no_format:
            return "\t"*level
        else:
            return ""

    def write(self,string,level=0):
        sys.stdout.write(self.indent(level) + string)
        
    def writeln(self,string,level=0):
        self.write(string + os.linesep,level)
    
    def print_table_heading(self):
        '''Prints the LaTeX heading for the table'''
        if self.options.custom:
            self.write("\\begin{"+self.options.custom+"}")
        else:
            self.write("\\begin{table}")
        if self.options.position != "":
            if self.options.position[0] == "[" and self.options.position[-1] == "]":
                self.write(self.options.position)
            else:
                self.write("[" + self.options.position + "]")
        if not self.options.custom:
            self.writeln("")
            if self.options.centering:
                self.writeln("\\centering",1)
            self.write("\\begin{" + self.options.environment + "}",1)
    
    def print_table_ending(self):
        '''Prints the LaTeX ending for the table'''
        self.writeln("\\hline",2)
        if self.options.custom:
            self.writeln("\\end{"+self.options.custom+"}")
        else:
            self.writeln("\\end{" + self.options.environment + "}",1)
            self.writeln("\\end{table}")

    def print_table_format(self,line):
        '''Prints the format of the table, based on splitting the first line by the delimiter'''
        count = len(self.correct_multiple_columns(line).split(self.options.delimiter))
        self.write("{")
        
        #If we have a full spec just write it out
        if "|" in self.options.table_spec:
            self.write(self.options.table_spec)
        else:
            for i in range(0,count):
                self.write("|" + self.options.table_spec)
            self.write("|")
        self.writeln("}")

    def print_table_header(self,line):
        '''Print the first line of the table'''
        self.writeln("\\hline",2)
        header = self.get_line(line)
        if self.options.multiline:
            header = header.split(" & ")
            header = map(lambda x : "\multicolumn{1}{|X|}{\centering " + x + "}",header)
            header = " & ".join(header)
        self.print_line(header)
        self.writeln("\\hline",2)

    def get_line(self, line, citeColumns=None, mathMode=False):
        line = self.correct_multiple_columns(line)
        line = line.split(self.options.delimiter)
        line = map(self.filter_characters,line)
        if mathMode:
            line = (  ( ("$"+el.replace("$", "\\$")+"$") if (el and i not in citeColumns) else el ) for i, el in enumerate(line)  )

        if citeColumns:
            line = list(line)
            for cC in citeColumns:
                line[cC] = "\\cite{"+line[cC]+"}"
        return " & ".join(line)

    def print_line(self,line, citeColumns=None, mathMode=False):
        '''Print a regular line, but formatted'''
        self.write(self.get_line(line, citeColumns, mathMode),2)
        self.writeln(" \\\\ ")
    
    def correct_multiple_columns(self,line):
        '''Corrects multiple delimiters if they should be corrected'''
        if self.options.ignore_multiple:
            line = re.sub(re.escape(self.options.delimiter)*2 + '+', self.options.delimiter, line)
        return line
        
    def parse(self,filename):
        if not self.options.dataOnly:
            self.print_table_heading()
        format_written = False
        header_written = False
        with open(filename, encoding="utf-8") as f:
            for line in f:
                if not self.options.dataOnly:
                    if not format_written:
                        self.print_table_format(line)
                        format_written = True
                if self.options.use_header and not header_written:
                    self.print_table_header(line)
                    header_written = True
                else:
                    self.print_line(line, self.options.citeColumns, self.options.mathMode)
        if not self.options.dataOnly:
            self.print_table_ending()

commaSeparatedListRe=re.compile(", ?")
def commaSeparatedList(listStr):
    return [m for m in commaSeparatedListRe.split(listStr) if m]

def integersList(listStr):
    return [int(m) for m in commaSeparatedList(listStr) if m]

def main():
    if not sys.stdout.isatty():
        sys.stdout=open(sys.stdout.fileno(), "wt", encoding="utf-8")
    
    optionparser = OptionParser()

    optionparser.add_option("-H", "--no-header",dest="use_header",default=True,action="store_false",help="No header will be generated for the table.")
    optionparser.add_option("-d", "--delimiter",dest="delimiter",type="string",default=",",help="Specify the delimiter to use for splitting colums.")
    optionparser.add_option("-i", "--ignore-multi",action="store_true",dest="ignore_multiple",default=False,help="Set whether multiple delimiters should be treated as one single delimeter or not.")
    optionparser.add_option("-t", "--tab",dest="use_tab",default=False,action="store_true",help="A shortcut for setting the delimiter to a tab character.")
    optionparser.add_option("-f", "--file",dest="filename",default="",help="Specify the file to convert.")
    optionparser.add_option("-n", "--no-format",dest="no_format",default=False,action="store_true",help="Do not format the source written out.")
    optionparser.add_option("-T", "--table-spec",dest="table_spec",default="",help="Specify the table spec to use (such as l for left justified, c for centered, etc.). Any strings with a pipe will be treated as the entire spec. Defaults to 'l'.")
    optionparser.add_option("--environment",dest="environment",type="string", default=None, help="Specify the table environment.")
    optionparser.add_option("-x", "--tabularx",dest="tabularx",default=False,action="store_true",help="Use the tabularx environment instead of the tabular environment.")
    optionparser.add_option("-m", "--multiline",dest="multiline",default=False,action="store_true",help="Use multiline headers with dynamic expanding. The table spec defaults to X when using this option.")
    optionparser.add_option("-c", "--centering",dest="centering",default=False,action="store_true",help="Center the table.")
    optionparser.add_option("-p", "--position",dest="position",default="",help="Set the float position of the table (h,H,H!)")
    optionparser.add_option("--custom", dest="custom", type="string", default="longtable", help="Don't use table and tabular, use a custom tag with longtable-compatible interface instead")
    optionparser.add_option("-D", "--data-only",dest="dataOnly",default=False,action="store_true",help="Don't wrap the data into anything, I'll do it myself! Useful if you wanna caption the table.")
    optionparser.add_option("-C", "--cite-columns", dest="citeColumns", type="string", default=None, help="wrap these columns into a \\cite")
    optionparser.add_option("-M", "--math-mode",dest="mathMode",default=False,action="store_true",help="Apply math mode to cells.")


    (options,args) = optionparser.parse_args()

    #If the tab flag is set, change the delimiter
    if options.use_tab:
        options.delimiter = "\t"
    
    if options.citeColumns:
        options.citeColumns=set(integersList(options.citeColumns))
    else:
        options.citeColumns=set()
    
    if options.environment is None:
        #If the tabularx flag is set, use the tabularx environment
        if options.tabularx:
            options.environment = "tabularx"
        else:
            options.environment = "tabular"
        
    #If the multiline options is set make sure the table_spec defaults to X
    if options.multiline:
        options.table_spec = "X"

    #If we still don't have a table spec then default to l
    if options.table_spec == "":
        options.table_spec = "l"
        
    #If a filename isn't specified then attempt to take the last argument
    if(options.filename == ""):
        filename = sys.argv[len(sys.argv)-1]
    else:
        filename = options.filename

    if not os.path.isfile(filename):
        print(filename,"is not a valid file name. The file name should be specified with the '-f' option, or be the last argument.")
        sys.exit(1)
        

    parser = Parser()
    parser.options = options
    parser.parse(filename)

if __name__=="__main__":
    main()
