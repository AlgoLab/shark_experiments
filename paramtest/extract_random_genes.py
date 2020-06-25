import sys
import random

import gffutils

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

def main():
    gtf_path = sys.argv[1]
    n_genes_to_select = int(sys.argv[2])
    gtf = open_gtf(gtf_path)
    n_tot_genes = 0
    for gene in gtf.features_of_type('gene'):
        n_tot_genes += 1

    idxs = list(range(0,n_tot_genes))
    random.shuffle(idxs)
    idxs = idxs[0:n_genes_to_select]
    i = 0
    for gene in gtf.features_of_type('gene'):
        if i in idxs:
            print(gene)
            for transcript in gtf.children(gene, featuretype='transcript', order_by='start'):
                print(transcript)
                for exon in gtf.children(transcript, featuretype='exon', order_by='start'):
                    print(exon)
        i+=1

if __name__ == '__main__':
    main()
