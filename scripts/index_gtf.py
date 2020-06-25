import sys
import random

import gffutils

def index_gtf(gtf_path):
    try:
        gffutils.FeatureDB("{}.db".format(gtf_path),
                           keep_order=True)
    except ValueError:
        gffutils.create_db(gtf_path,
                           dbfn="{}.db".format(gtf_path),
                           force=True, keep_order=True,
                           disable_infer_genes=True,
                           disable_infer_transcripts=True,
                           merge_strategy='merge',
                           sort_attribute_values=True)
        gffutils.FeatureDB("{}.db".format(gtf_path), keep_order=True)

def main():
    gtf_path = sys.argv[1]
    index_gtf(gtf_path)

if __name__ == '__main__':
    main()
