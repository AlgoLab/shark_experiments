import sys, os, glob, statistics
import itertools

def get_subfolds(path):
    bn = os.path.basename
    dn = os.path.dirname
    quartile = int(bn(dn(path))[1])
    sample = int(bn(dn(dn(path))).split('_')[1])
    return quartile, sample

def mean(L):
    return round(statistics.mean(L), 4)

def median(L):
    return round(statistics.median(L), 4)

def sd(L):
    return round(statistics.stdev(L), 4)

def main():
    csv_list = glob.glob(sys.argv[1])
    results = {}
    samples = set()
    quartiles = set()
    for csv in csv_list:
        k = get_subfolds(csv) # (quartile,sample)
        if k not in results:
            results[k] = {'P' : [], 'R' : [], 'TP' : [], 'FP' : [], 'FN' : []}
        TP,FP,FN,P,R = open(csv).readlines()[1].strip('\n').split('\t')
        TP,FP,FN = int(TP),int(FP),int(FN)
        P,R = float(P),float(R)
        results[k]['TP'].append(TP)
        results[k]['FP'].append(FP)
        results[k]['FN'].append(FN)
        results[k]['P'].append(P)
        results[k]['R'].append(R)

    Qs = sorted(set([k[0] for k in results.keys()]))
    Ss = sorted(set([k[1] for k in results.keys()]))
    
    print("ReadLen,GeneLenQuartile,TP,FP,FN,med(P),avg(P),sd(P),med(R),avg(R),sd(R)")
    for sample,quartile in itertools.product(Ss, Qs):
        P = results[(quartile, sample)]['P']
        R = results[(quartile, sample)]['R']
        TP = results[(quartile, sample)]['TP']
        FP = results[(quartile, sample)]['FP']
        FN = results[(quartile, sample)]['FN']
        #print(sample, quartile, round(mean(P)*100,3), round(mean(R)*100,3), sep=',')
        print(sample, quartile, mean(TP), mean(FP), mean(FN), median(P), mean(P), sd(P), median(R), mean(R), sd(R), sep=',')

if __name__ == "__main__":
    main()
