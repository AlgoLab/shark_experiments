/**
 * shark - Mapping-free filtering of useless RNA-Seq reads
 * Copyright (C) 2019 Tamara Ceccato, Luca Denti, Yuri Pirola, Marco Previtali
 *
 * This file is part of shark.
 *
 * shark is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * shark is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with shark; see the file LICENSE. If not, see
 * <https://www.gnu.org/licenses/>.
 **/

#include <chrono>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <string>
#include <vector>
#include <unordered_map>
#include <deque>

#include "common.hpp"
#include "argument_parser.hpp"
#include "FastqSplitter.hpp"
#include "kmer_utils.hpp"

using namespace std;

auto start_t = chrono::high_resolution_clock::now();

void pelapsed(const string &s = "") {
  auto now_t = chrono::high_resolution_clock::now();
  cerr << "[count-collisions/" << s << "] Time elapsed "
       << chrono::duration_cast<chrono::milliseconds>(now_t - start_t).count()/1000
       << endl;
}

uint64_t get_hash(uint64_t kmer, uint64_t rckmer) {
  return _get_hash(min(kmer, rckmer)) % opt::bf_size;
}

typedef std::unordered_map<uint64_t, deque<uint64_t>> kmer_map_t;

bool add_to_map(uint64_t kmer, uint64_t rckmer, kmer_map_t& map) {
  const uint64_t key = get_hash(kmer, rckmer);
  const uint64_t canonical = min(kmer, rckmer);
  if (map.count(key) == 0) {
    map[key] = deque<uint64_t>();
    map[key].push_back(canonical);
    return false;
  }
  deque<uint64_t>& vals = map[key];
  for(uint64_t ok: vals) {
    if (ok == canonical) return false;
  }
  vals.push_back(canonical);
  return true;
}


class ReadAnalyzer {
public:
  typedef std::array<size_t, 3> output_t;

  ReadAnalyzer(kmer_map_t& _map, uint _k) :
  map(_map), k(_k) {}

  output_t operator()(vector<elem_t> *reads) const {
    size_t collided_queries = 0;
    size_t success_queries = 0;
    size_t tot_queries = 0;
    for(const auto & p : *reads) {
      const string& read_seq = p.first;
      unsigned int len = 0;
      for (unsigned int pos = 0; pos < read_seq.size(); ++pos) {
        len += to_int[read_seq[pos]] > 0 ? 1 : 0;
      }
      if(len >= k) {
        int pos = 0;
        uint64_t kmer = build_kmer(read_seq, pos, k);
        if(kmer == (uint64_t)-1) continue;
        uint64_t rckmer = revcompl(kmer, k);
        tot_queries++;
        const auto el = map.find(get_hash(kmer, rckmer));
        if (el != map.cend()) {
          success_queries++;
          if (el->second.size() > 1) collided_queries++;
        }

        for (; pos < (int)read_seq.size(); ++pos) {
          uint8_t new_char = to_int[read_seq[pos]];
          if(new_char == 0) { // Found a char different from A, C, G, T
            ++pos; // we skip this character then we build a new kmer
            kmer = build_kmer(read_seq, pos, k);
            if(kmer == (uint64_t)-1) break;
            rckmer = revcompl(kmer, k);
            --pos; // p must point to the ending position of the kmer, it will be incremented by the for
          } else {
            --new_char; // A is 1 but it should be 0
            kmer = lsappend(kmer, new_char, k);
            rckmer = rsprepend(rckmer, reverse_char(new_char), k);
          }
          tot_queries++;
          const auto el = map.find(get_hash(kmer, rckmer));
          if (el != map.cend()) {
            success_queries++;
            if (el->second.size() > 1) collided_queries++;
          }
        }
      }
    }
    return { tot_queries, success_queries, collided_queries };
  }


private:
  const kmer_map_t& map;
  const uint k;

};

/*****************************************
 * Main
 *****************************************/
int main(int argc, char *argv[]) {
  parse_arguments(argc, argv);

  /*** 0. Check input files and initialize variables **************************/
  // Transcripts
  gzFile ref_file = gzopen(opt::fasta_path.c_str(), "r");
  kseq_t *seq = kseq_init(ref_file);
  kseq_destroy(seq);
  gzclose(ref_file);

  // Sample 1
  gzFile read1_file = gzopen(opt::sample1_path.c_str(), "r");
  seq = kseq_init(read1_file);
  kseq_destroy(seq);
  gzclose(read1_file);

  // Sample 2
  gzFile read2_file = nullptr;
  if(opt::paired_flag) {
    read2_file = gzopen(opt::sample2_path.c_str(), "r");
    seq = kseq_init(read2_file);
    kseq_destroy(seq);
    gzclose(read2_file);
  }

  kmer_map_t map;
  vector<string> legend_ID;
  int seq_len;

  if(opt::verbose) {
    cerr << "Reference texts: " << opt::fasta_path << endl;
    cerr << "Sample 1: " << opt::sample1_path << endl;
    if(opt::paired_flag)
      cerr << "Sample 2: " << opt::sample2_path << endl;
    cerr << "K-mer length: " << opt::k << endl;
    cerr << "Minimum base quality: " << static_cast<int>(opt::min_quality) << endl;
    cerr << endl;
  }

  /****************************************************************************/

  /*** 1. Iteration over transcripts ***********************************/
  ref_file = gzopen(opt::fasta_path.c_str(), "r");
  seq = kseq_init(ref_file);
  int nidx = 0;
  size_t kmers = 0;
  // open and read the .fa, every time a kmer is found the relative index is
  // added to BF
  while ((seq_len = kseq_read(seq)) >= 0) {
    string input_name = seq->name.s;
    legend_ID.push_back(input_name);

    if ((uint)seq_len >= opt::k) {
      int _p = 0;
      uint64_t kmer = build_kmer(seq->seq.s, _p, opt::k);
      if(kmer == (uint64_t)-1) continue;
      uint64_t rckmer = revcompl(kmer, opt::k);
      add_to_map(kmer, rckmer, map);
      ++kmers;

      for (int p = _p; p < seq_len; ++p) {
        uint8_t new_char = to_int[seq->seq.s[p]];
        if(new_char == 0) { // Found a char different from A, C, G, T
          ++p; // we skip this character then we build a new kmer
          kmer = build_kmer(seq->seq.s, p, opt::k);
          if(kmer == (uint64_t)-1) break;
          rckmer = revcompl(kmer, opt::k);
          --p; // p must point to the ending position of the kmer, it will be incremented by the for
        } else {
          --new_char; // A is 1 but it should be 0
          kmer = lsappend(kmer, new_char, opt::k);
          rckmer = rsprepend(rckmer, reverse_char(new_char), opt::k);
        }
        add_to_map(kmer, rckmer, map);
        ++kmers;
      }
    }
    ++nidx;
  }
  kseq_destroy(seq);
  gzclose(ref_file);

  pelapsed("collisions computed from transcripts (" + to_string(nidx) + " genes)");

  size_t count = 0;
  size_t count_distinct = 0;
  for (const auto& it: map) {
    count += (it.second.size() - 1);
    if (it.second.size() > 1) count_distinct++;
  }
  std::cout << "Collisions:            " << count << std::endl;
  std::cout << "Collisions (distinct): " << count_distinct << std::endl;
  std::cout << "Elements:              " << map.size() << std::endl;
  std::cout << "K-mers:                " << kmers << std::endl;


  /****************************************************************************/

  /*** 2. Iteration over the sample *****************************************/
  {
    kseq_t *sseq1 = nullptr, *sseq2 = nullptr;
    read1_file = gzopen(opt::sample1_path.c_str(), "r");
    sseq1 = kseq_init(read1_file);
    if(opt::paired_flag) {
      read2_file = gzopen(opt::sample2_path.c_str(), "r");
      sseq2 = kseq_init(read2_file);
    }

    tbb::filter_t<void, FastqSplitter::output_t*>
      sr(tbb::filter::serial, FastqSplitter(sseq1, sseq2, 50000, opt::min_quality));
    tbb::filter_t<FastqSplitter::output_t*, ReadAnalyzer::output_t>
      ra(tbb::filter::parallel, ReadAnalyzer(map, opt::k));

    size_t collided_queries = 0;
    size_t success_queries = 0;
    size_t tot_queries = 0;
    tbb::filter_t<void, void> pipeline_reads = sr &
      ra &
      tbb::make_filter<ReadAnalyzer::output_t, void>(tbb::filter::serial,
                                                [&](ReadAnalyzer::output_t x) {
                                                  tot_queries += x[0];
                                                  success_queries += x[1];
                                                  collided_queries += x[2];
                                                }
                                                );
    tbb::parallel_pipeline(opt::nThreads, pipeline_reads);

    kseq_destroy(sseq1);
    gzclose(read1_file);
    if(opt::paired_flag) {
      kseq_destroy(sseq2);
      gzclose(read2_file);
    }
    std::cout << "Total queries:         " << tot_queries << std::endl;
    std::cout << "Success queries:       " << success_queries << std::endl;
    std::cout << "Collided queries:      " << collided_queries << std::endl;
  }
  pelapsed("Sample completed");

  /****************************************************************************/

  pelapsed("Analysis completed");
  return 0;
}
