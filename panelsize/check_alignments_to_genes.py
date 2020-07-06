import sys

from collections import Counter

import gffutils
import pysam

def open_gtf(gtf_path):
    try:
        gtf = gffutils.FeatureDB("{}.db".format(gtf_path),
                                 keep_order=True)
    except ValueError:
        gtf = gffutils.create_db(gtf_path,
                                 dbfn="{}.db".format(gtf_path),
                                 force=True, keep_order=True,
                                 disable_infer_genes=True,
                                 disable_infer_transcripts=True,
                                 merge_strategy='merge',
                                 sort_attribute_values=True)
        gtf = gffutils.FeatureDB("{}.db".format(gtf_path), keep_order=True)
    return gtf

def build_gt_dict(gtf):
    tr2gene = {}
    for gene in gtf.features_of_type('gene'):
        gene_idx = gene.id
        for tr in gtf.children(gene, featuretype='transcript'):
            tr_idx = tr.id
            tr2gene[tr_idx] = gene_idx
    return tr2gene

def main():
    sam_path = sys.argv[1]
    bed_path = sys.argv[2]
    gtf_path = sys.argv[3]

    gtf = open_gtf(gtf_path)
    tr2gene = build_gt_dict(gtf)

    truth = Counter()
    for line in open(bed_path, 'r'):
        read_name = line.split("\t")[3]
        transcript_name = read_name.split(':')[2]
        gene_name = tr2gene[transcript_name]
        truth.update({(read_name, gene_name):1})
    
    out = Counter()
    with pysam.AlignmentFile(sam_path, 'r') as aln_file:
        for aln in aln_file:
            if aln.is_unmapped: # or aln.is_secondary or aln.is_supplementary:
                continue
            given_gene_idx = aln_file.get_reference_name(aln.reference_id)
            if given_gene_idx in tr2gene:
                # read is aligned to a transcript (pufferfish)
                given_gene_idx = tr2gene[given_gene_idx]
            read_idx = aln.query_name
            association = (read_idx,given_gene_idx)
            if association not in out:
                out.update({association:1})
    
    truth_size = sum(truth.values())
    out_size = sum(out.values())
    TP = sum((truth&out).values())
    FP = sum((out-truth).values())
    FN = sum((truth-out).values())

    print('TP', 'FP', 'FN', 'P', 'R', sep='\t')
    P = TP/(TP+FP) if TP+FP != 0 else 0
    R = TP/(TP+FN) if TP+FN != 0 else 0
    print(TP, FP, FN, round(P,3), round(R,3), sep='\t')

if __name__ == '__main__':
    main()
