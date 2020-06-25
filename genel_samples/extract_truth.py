import sys
import gffutils

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
    bed_path = sys.argv[2]

    gtf = openGTF(gtf_path)
    transcripts = set()
    for gene in gtf.features_of_type('gene'):
        for transcript in gtf.children(gene, featuretype='transcript', order_by='start'):
            transcripts.add(transcript.id)

    for line in open(bed_path):
        read_idx = line.split('\t')[3]
        tr_idx = read_idx.split(':')[2]
        if tr_idx in transcripts:
            print(line, end='')

if __name__ == "__main__":
    main()
