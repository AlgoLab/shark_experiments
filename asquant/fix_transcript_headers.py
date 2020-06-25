from Bio import SeqIO
import sys

def main():
    in_fa = sys.argv[1]
    for record in SeqIO.parse(in_fa, "fasta"):
        record.id = record.id.split('.')[0]
        SeqIO.write(record, sys.stdout, "fasta")

if __name__ == "__main__":
    main()
