import sys, os
import statistics

def main():
    fpaths = sys.argv[1:]

    data = {}
    for fpath in fpaths:
        f = open(fpath)
        next(f)
        for line in f:
            k,c,q,mult,TP,FP,FN,P,R,secs,ram = line.strip('\n').split(',')
            key = (k,c,q,mult)
            if key not in data:
                data[key] = {'pre':[], 'rec':[], 'sec':[], 'ram':[]}
            data[key]['pre'].append(float(P))
            data[key]['rec'].append(float(R))
            data[key]['sec'].append(round(float(secs)))
            data[key]['ram'].append(float(ram))
        f.close()
    
    print("k,c,q,mult,Pav,Psd,Rav,Rsd,Secsavs,Secssd,ram")
    for key in data:
        k,c,q,mult = key
        print(k,
              c,
              q,
              mult,
              round(statistics.mean(data[key]['pre'])*100,2),
              round(statistics.pstdev(data[key]['pre'])*100,2),
              round(statistics.mean(data[key]['rec'])*100,2),
              round(statistics.pstdev(data[key]['rec'])*100,2),
              statistics.mean(data[key]['sec']),
              round(statistics.pstdev(data[key]['sec']),2),
              statistics.mean(data[key]['ram']), sep=',')
        

if __name__ == "__main__":
    main()