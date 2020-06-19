#!/usr/bin/env python

import re
import os
import sys
import shutil
import argparse
import collections

def identify_groups(input_dirs, toremove):
    
    #Gather all fastq files in inputdir and its subdirs
    fastq_files=[]
    for input_dir in input_dirs.split(','):
        for subdir, dirs, files in os.walk(input_dir):
            for fastq in  files:
                if fastq.endswith('.fastq.gz'):
                    fastq_files.append(os.path.join(subdir, fastq))
   
    #Match NGI sample number from flowcell
    sample_pattern=re.compile('^(.+)({})+_S[0-9]+(_.+)*_R([1-2])_'.format(toremove))
    #Remove files that already have the right name (i.e have been merged already)
    matches=[]
    for fastq_file in fastq_files:
        try:
            match=sample_pattern.search(os.path.basename(fastq_file)).group(1)
            if match:
                matches.append(fastq_file)
        except AttributeError:
            continue
    fastq_files=matches
     
    while fastq_files:
        tomerge=[]
        
        #grab one sample to work on
        first=fastq_files[0]
        fq_bn=os.path.basename(first)
        sample_name=sample_pattern.match(fq_bn).group(1)
        fastq_files_read1=[]
        fastq_files_read2=[]
        
        for fq in fastq_files:
            this_sample_pattern = re.compile("^" + sample_name + '{}_S[0-9]+(_.+)*_R([1-2])_'.format(toremove))
            if this_sample_pattern.match(os.path.basename(fq)) and "_R1_" in os.path.basename(fq):
                fastq_files_read1.append(fq) 
                
            if this_sample_pattern.match(os.path.basename(fq)) and "_R2_" in os.path.basename(fq):
                fastq_files_read2.append(fq) 


        fastq_files_read1.sort()
        fastq_files_read2.sort()

        print(sample_name + ",1," + ":".join(fastq_files_read1))
        print(sample_name + ",2," + ":".join(fastq_files_read2))
        
        for fq in fastq_files_read1:
            fastq_files.remove(fq)
        for fq in fastq_files_read2:
            fastq_files.remove(fq)
        
if __name__ == "__main__":
   parser = argparse.ArgumentParser(description=""" Identifies groups of FASTQ files to merge into one file by read end and sample name. Looks through the given dir and subdirs.""")
   parser.add_argument("input_dir", nargs='?', default='.', help="Comma separated base directory list for the fastq files that should be merged.")
   parser.add_argument("to_remove", nargs='?', default='', help="Optional sample suffix to be removed from output files.")
   args = parser.parse_args() 
   identify_groups(args.input_dir, args.to_remove)
