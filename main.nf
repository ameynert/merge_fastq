#!/usr/bin/env nextflow
/*
========================================================================================
                         nf-core/merge_fastq
========================================================================================
 nf-core/merge_fastq Analysis Pipeline.
 #### Homepage / Documentation
 https://github.com/nf-core/merge_fastq
----------------------------------------------------------------------------------------
*/


def helpMessage() {
    log.info"""
    =======================================================
                                              ,--./,-.
              ___     __   __   __   ___     /,-._.--~\'
        |\\ | |__  __ /  ` /  \\ |__) |__         }  {
        | \\| |       \\__, \\__/ |  \\ |___     \\`-._,-`-,
                                              `._,._,\'
     nf-core/merge_fastq v${workflow.manifest.version}
    =======================================================
    Usage:

    The typical command for running the pipeline is as follows:

    nextflow run nf-core/merge_fastq --inputdir fastq_files --outputdir merged_fastq_files

    Optional arguments:
      --inputdir                    Path to input data [fastq_files] - multiple directories separated by commas
      --outdir                      The output directory where the results will be saved [merged_fastq_files]
      --toremove                    Optional suffix to remove from input sample names, e.g. sample_toremove_S1_L001_R1_001.fastq.gz
      --suffix                      Optional suffix for output sample names, e.g. sample_suffix_R[1,2].fastq.gz
    """.stripIndent()
}

// Show help emssage
params.help = false
if (params.help){
    helpMessage()
    exit 0
}


// Defines reads and outputdir
params.inputdir = "fastq_files"
params.outdir = 'merged_fastq_files'
params.suffix = ''
params.toremove = ''

// Header 
println "========================================================"
println "       M E R G E _ F A S T Q    P I P E L I N E         "
println "========================================================"
println "['Pipeline Name']     = ameynert/merge_fastq"
println "['Pipeline Version']  = workflow.manifest.version"
println "['Inputdir']          = $params.inputdir"
println "['Output dir']        = $params.outdir"
println "['Working dir']       = workflow.workDir"
println "['Container Engine']  = workflow.containerEngine"
println "['Current home']      = $HOME"
println "['Current user']      = $USER"
println "['Current path']      = $PWD"
println "['Working dir']       = workflow.workDir"
println "['Script dir']        = workflow.projectDir"
println "['Config Profile']    = workflow.profile"
println "========================================================"


// Separate input directories by comma on the command line, convert to file objects and pass
// to merge_fastq

input_dir_strings = params.inputdir.split(',')
input_dir_files = file(input_dir_strings[0])
for (i = 1; i < input_dir_strings.size(); i = i + 1) {
  input_dir_files += ',' + file(input_dir_strings[i])
}

// Identify groups of FastQ files
process identify_groups {

    output:
    stdout into group_output_ch

    script:
    """
    identify_fastq_files_to_merge.py ${input_dir_files} ${params.toremove}
    """
}

// Split the output by lines
group_output_ch
    .splitCsv()
    .map { row -> tuple(row[0], row[1], row[2]) }
    .set { group_ch }
 
// Merge FastQ files
process merge_fastq {

    publishDir params.outdir, mode: 'move'

    input:
    tuple val(sample_name), val(read_end), val(files) from group_ch

    output:
    file("*.log")
    file("*.gz")

    script:
    """
    merge_and_rename_NGI_fastq_files.py ${files} ${sample_name} ${read_end} ./ ${params.suffix} > ${sample_name}.merge.log
    """
}

workflow.onComplete { 
    println ( workflow.success ? "Merging done! transferring merged files and wrapping up..." : "Oops .. something went wrong" )
    log.info "[nf-core/test] Pipeline Complete"

}

