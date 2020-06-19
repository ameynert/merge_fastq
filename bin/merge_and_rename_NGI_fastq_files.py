#!/usr/bin/env python

import re
import os
import sys
import shutil
import argparse
import collections

def merge_files(sample_name, read_nb, file_list, dest_dir, suffix):
    outfile=os.path.join(dest_dir, "{}{}_R{}.fastq.gz".format(sample_name, suffix, read_nb))
    tomerge = file_list.split(':')
    print("Merging the following files:")
    if not tomerge:
        print("No read {} files found".format(read_nb))
        return
    for fq in tomerge:
        print(fq)
    print("as {}".format(outfile))
    with open(outfile, 'wb') as wfp:
        for fn in tomerge:
            with open(fn, 'rb') as rfp:
                shutil.copyfileobj(rfp, wfp)
        

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description=""" Merges the given list of FASTQ files. Output as {dest_dir}/{sample_name}{suffix}_R{read_end}.fastq.gz.""")
   parser.add_argument("files", nargs='?', default='.', help="Colon-delimited list of FASTQ files to merge.")
   parser.add_argument("sample_name", nargs='?', default='.', help="Output sample name.")
   parser.add_argument("read_end", nargs='?', default='.', help="Read end (1 or 2).")
   parser.add_argument("dest_dir", nargs='?', default='.', help="Path to where the merged files should be output. ")
   parser.add_argument("suffix", nargs='?', default='', help="Optional suffix for sample names in output file names, e.g. sample_R1.fastq.gz. ")
   args = parser.parse_args() 
   merge_files(args.sample_name, args.read_end, args.files, args.dest_dir, args.suffix)

