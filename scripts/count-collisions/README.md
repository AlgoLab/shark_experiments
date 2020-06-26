# Count collisions

Utility to count the number of hash collisions an false positives in the membership queries


## Dependencies

It requires Intel TBB (tested with version 2017 update 7)

## Compilation

Please run `make`.

## Usage
```
Usage: count-collisions -r <references> -1 <sample1> [OPTIONAL ARGUMENTS]

Arguments:
      -r, --reference                   reference sequences in FASTA format (can be gzipped)
      -1, --sample1                     sample in FASTQ (can be gzipped)

Optional arguments:
      -h, --help                        display this help and exit
      -2, --sample2                     second sample in FASTQ (optional, can be gzipped)
      -k, --kmer-size                   size of the kmers to index (default:17, max:31)
      -b, --bf-size                     bloom filter size in GB (default:1)
      -q, --min-base-quality            minimum base quality (assume FASTQ Illumina 1.8+ Phred scale, default:0, i.e., no filtering)
      -t, --threads                     number of threads (default:1)
      -v, --verbose                     verbose mode
```

## Output format

`count-collisions` outputs to `stdout` the following stats:

* Collisions: number of distinct canonical kmers (of the reference) that have the same hash value
* Collisions (distinct): number of distinct hash values that are the image of more than one canonical kmer
* Elements: total number of hash values
* K-mers: total number of canonical kmers of the reference
* Total queries: total number of membership queries performed using the kmers in the sample
* Success queries: number of the membership queries that resulted with a 1 in the Bloom filter
* Collided queries: number of the membership queries that resulted in a false positive
  (i.e., the canonical kmer maps to an hash value that is the image of more than one canonical kmer of the reference)
