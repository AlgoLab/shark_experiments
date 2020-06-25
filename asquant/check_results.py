import sys, os, glob
import gzip

root_fold = sys.argv[1]
pvalue_tresh = float(sys.argv[2])

truth_fpath = os.path.join(root_fold, "input", "RTPCR_genes.csv")

SADs = [1,2,4,8]

rmats = []
sharked_rmats = []
for SAD in SADs:
    rmats.append(os.path.join(root_fold, "output", "rMATS", f"SAD{SAD}", "SE.MATS.JCEC.txt"))
    sharked_rmats.append(os.path.join(root_fold, "output", "sharked_rMATS", f"SAD{SAD}", "SE.MATS.JCEC.txt"))

suppa_fpath = os.path.join(root_fold, "output", "suppa2", "CTRL_KD.dpsi")
sharked_suppa_fpath = os.path.join(root_fold, "output", "sharked_suppa2", "CTRL_KD.dpsi")

# We need _1 to extract events; _2 for p_value (maybe useless since all pvalues are ~1)
spladder = []
sharked_spladder = []
for SAD in SADs:
    spladder.append((os.path.join(root_fold, "output", "spladder", f"SAD{SAD}", "difftest", "merge_graphs_exon_skip_C3.confirmed.txt.gz"),
                     os.path.join(root_fold, "output", "spladder", f"SAD{SAD}", "difftest", "testing", "test_results_C3_exon_skip.tsv")))
    sharked_spladder.append((os.path.join(root_fold, "output", "sharked_spladder", f"SAD{SAD}", "difftest", "merge_graphs_exon_skip_C3.confirmed.txt.gz"),
                             os.path.join(root_fold, "output", "sharked_spladder", f"SAD{SAD}", "difftest", "testing", "test_results_C3_exon_skip.tsv")))

def extract_exon_truth(truth_fpath):
    truth = {}
    truth_set = set()
    with open(truth_fpath) as truth_file:
        next(truth_file, None) # Drop header
        for line in truth_file:
            _,_,_,p1,p2,_,_,info = line.strip("\n").split(",")
            p1,p2 = int(p1),int(p2)
            gene_idx = info.split(";")[0]
            truth[gene_idx] = truth[gene_idx] + [(p1,p2)] if gene_idx in truth else [(p1,p2)]
            truth_set.add((gene_idx,p1,p2))
    return truth, truth_set

def extract_intron_truth(truth_fpath):
    truth = {}
    truth_set = set()
    with open(truth_fpath) as truth_file:
        next(truth_file, None) # Drop header
        for line in truth_file:
            _,_,_,_,_,_,_,info = line.strip("\n").split(",")
            if info.count(':') == 0:
                continue
            gene_etype,_,I1,I2,_ = info.split(':')
            gene_idx = gene_etype.split(';')[0]
            p1 = int(I1.split('-')[0])
            p2 = int(I2.split('-')[1])
            truth[gene_idx] = truth[gene_idx] + [(p1,p2)] if gene_idx in truth else [(p1,p2)]
            truth_set.add((gene_idx,p1,p2))
    return truth, truth_set

def evaluate_suppa(truth, truth_set, fpath, pvalue_tresh, s = ""):
    TPs = set()
    fps = 0
    with open(fpath) as suppa_file:
        next(suppa_file, None) # Drop header
        for line in suppa_file:
            header, dpsi, pvalue = line.strip('\n').split('\t')
            gene_etype, *rest = header.split(':')
            gene, etype = gene_etype.split(';')
            if etype in ["MX", "AF", "AL"]:
                continue
            if etype in ["A3", "A5", "RI"]:
                continue
            if gene not in truth:
                continue
            chrom, E1, E2, strand = rest
            
            (s1,skipped_start) = E1.split('-')
            (skipped_end,e2) = E2.split('-')

            skipped_start, skipped_end = int(skipped_start), int(skipped_end)
            dpsi, pvalue= float(dpsi), float(pvalue)

            if etype == "SE" and pvalue <= pvalue_tresh:
                if (skipped_start, skipped_end) in truth[gene]:
                    TPs.add((gene, skipped_start, skipped_end))
                else:
                    fps+=1

    print(s, len(truth_set & TPs), fps)
    return truth_set & TPs


def evaluate_rmats(truth, truth_set, fpath, pvalue_tresh, s = ""):
    TPs = set()
    fps = 0
    with open(fpath) as rmats_file:
        next(rmats_file, None) # Drop header
        for line in rmats_file:
            idx, gene, gene_sym, chrom, strand, skipped_start, skipped_end, upstream_start, upstream_end, downstream_start, downstream_end, _, _, _, _, _, _, _, pvalue, _, _, _, _ = line.strip('\n') .split('\t')
            gene = gene[1:-1]
            skipped_start, skipped_end = int(skipped_start)+1, int(skipped_end)
            upstream_end, downstream_start = int(upstream_end)-1, int(downstream_start)-1
            pvalue = float(pvalue)

            if gene not in truth:
                continue
            
            if pvalue <= pvalue_tresh:
                if (skipped_start, skipped_end) in truth[gene]:
                    TPs.add((gene, skipped_start, skipped_end))
                else:
                    fps+=1

    print(s, len(truth_set & TPs), fps)
    return truth_set & TPs

def evaluate_spladder(ex_truth, ex_truth_set, in_truth, in_truth_set, fpath_es_1, fpath_es_2, pvalue_tresh, s = ""):
    # Exon Skippings
    es_events = {}
    with gzip.open(fpath_es_1, "rt") as spladder_file:
        next(spladder_file, None) # Drop header
        for line in spladder_file:
            chrom, strand, event_idx, gene_idx, upstream_start, upstream_end, skipped_start, skipped_end, downstream_start, downstream_end, *_ = line.strip('\n').split('\t')
            skipped_start, skipped_end = int(skipped_start), int(skipped_end)
            if gene_idx in ex_truth:
                es_events[event_idx] = (gene_idx, skipped_start, skipped_end)

    es_TPs = set()
    es_fps = 0
    with open(fpath_es_2) as diffspladder_file:
        next(diffspladder_file, None) # Drop header
        for line in diffspladder_file:
            event_idx, gene_idx, pvalue, *_ = line.strip('\n').split('\t')
            event_idx = event_idx.split('_')[0] + '_' + event_idx.split('_')[1] + '.' + event_idx.split('_')[2]
            pvalue = float(pvalue)
            if gene_idx not in ex_truth:
                continue
            if pvalue <= pvalue_tresh:
                gene_idx, skipped_start, skipped_end = es_events[event_idx]
                if (skipped_start, skipped_end) in ex_truth[gene_idx]:
                    es_TPs.add((gene_idx, skipped_start, skipped_end))
                else:
                    es_fps+=1

    print(s, len(ex_truth_set & es_TPs), es_fps)
    return ex_truth_set & es_TPs

if __name__ == "__main__":
    ex_truth, ex_truth_set = extract_exon_truth(truth_fpath)
    in_truth, in_truth_set = extract_intron_truth(truth_fpath)
    
    print("Tool TPs FPs")
    print("")

    suppa_tps = evaluate_suppa(ex_truth, ex_truth_set, suppa_fpath, pvalue_tresh, "suppa2")
    sharked_suppa_tps = evaluate_suppa(ex_truth, ex_truth_set, sharked_suppa_fpath, pvalue_tresh, "suppa2.sharked")
    print("Diff:", len(suppa_tps & sharked_suppa_tps) - len(suppa_tps))
    print("")
    
    for i in range(0,4):
        rmats_fpath = rmats[i]
        sharked_rmats_fpath = sharked_rmats[i]
        SAD = SADs[i]
        rmats_tps = evaluate_rmats(ex_truth, ex_truth_set, rmats_fpath, pvalue_tresh, f"rMATS.SAD{SAD}")
        sharked_rmats_tps = evaluate_rmats(ex_truth, ex_truth_set, sharked_rmats_fpath, pvalue_tresh, f"rMATS.sharked.SAD{SAD}")
        print("Diff:", len(rmats_tps & sharked_rmats_tps) - len(rmats_tps))
        print("")

    for i in range(0,4):
        spladder_fpath_es_1, spladder_fpath_es_2 = spladder[i]
        sharked_spladder_fpath_es_1, sharked_spladder_fpath_es_2 = sharked_spladder[i]
        SAD = SADs[i]
        spladder_tps = evaluate_spladder(ex_truth, ex_truth_set, in_truth, in_truth_set, spladder_fpath_es_1, spladder_fpath_es_2, pvalue_tresh, f"spladder.SAD{SAD}")
        sharked_spladder_tps = evaluate_spladder(ex_truth, ex_truth_set, in_truth, in_truth_set, sharked_spladder_fpath_es_1, sharked_spladder_fpath_es_2, pvalue_tresh, f"spladder.sharked.SAD{SAD}")
        print("Diff:", len(spladder_tps & sharked_spladder_tps) - len(spladder_tps))
        print("")
