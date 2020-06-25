import sys
from Bio import SeqIO

def main():
    in_fq_path = sys.argv[1]
    out_fq1_path = in_fq_path[:-6] + "_1.fastq"
    out_fq2_path = in_fq_path[:-6] + "_2.fastq"

    out_fq1 = open(out_fq1_path, 'w')
    out_fq2 = open(out_fq2_path, 'w')
    for record in SeqIO.parse(in_fq_path, "fastq"):
        if record.id[-1] == "1":
            SeqIO.write(record, out_fq1, "fastq")
        else:
            SeqIO.write(record, out_fq2, "fastq")
    out_fq1.close()
    out_fq2.close()

if __name__ == "__main__":
    main()
