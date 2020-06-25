import sys
import random
import gffutils

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

def openGTF(gtf_path):
    try:
        gtf = gffutils.FeatureDB("{}.db".format(gtf_path),
                                 keep_order=True)
    except ValueError:
        gtf = gffutils.create_db(gtf_path,
                                 dbfn="{}.db".format(gtf_path),
                                 force=True,
                                 keep_order=True,
                                 disable_infer_genes=True,
                                 disable_infer_transcripts=True,
                                 merge_strategy='merge',
                                 sort_attribute_values=True)
        gtf = gffutils.FeatureDB("{}.db".format(gtf_path),
                                 keep_order=True)
    return gtf

def main():
    gtf_path = sys.argv[1]
    q = int(sys.argv[2])
    n = int(sys.argv[3])

    gtf = openGTF(gtf_path)
    ls = []
    for gene in gtf.features_of_type('gene'):
        if gene.source == "mirbase":
            continue
        ls.append(gene.end-gene.start+1)

    a = np.array(ls)
    Qs = [0]
    for i in [.25, .5, .75, 1]:
        x = np.quantile(a, i-0.25)
        y = np.quantile(a, i)
        Qs.append(y)
        print(x, y, len([l for l in ls if l>x and l<=y]), file=sys.stderr)

    genes_in_quartile = []
    for gene in gtf.features_of_type('gene'):
        if gene.source == "mirbase":
            continue
        if Qs[q-1] < gene.end-gene.start+1 <= Qs[q]:
            genes_in_quartile.append(gene.id)

    random.shuffle(genes_in_quartile)
    selected_genes = genes_in_quartile[0:n]
    
    for gene in gtf.features_of_type('gene'):
        if gene.id not in selected_genes:
            continue
        print(gene)
        for transcript in gtf.children(gene, featuretype='transcript', order_by='start'):
            print(transcript)
            for exon in gtf.children(transcript, featuretype='exon', order_by='start'):
                print(exon)

if __name__ == "__main__":
    main()
