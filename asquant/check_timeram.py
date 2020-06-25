import sys, os

import datetime
import time

root_fold = sys.argv[1] #"/home/prj_gralign/data/recomb-sperim/comparison/"
in_fold = os.path.join(root_fold, "input")
out_fold = os.path.join(root_fold, "output")
samples = ["SRR1513329", "SRR1513330", "SRR1513331", "SRR1513332", "SRR1513333", "SRR1513334"]

def print_time_ram(fpath, s=""):
    i = 0
    secs = 0
    ram = 0
    for line in open(fpath):
        if i == 4: # wall clock
            t = line.strip('\n').split(' ')[-1]
            t = t.split('.')[0] # to remove milliseconds
            if t.count(":") == 1: # min:sec
                t = time.strptime(t,'%M:%S')
                secs = int(datetime.timedelta(hours=t.tm_hour,minutes=t.tm_min,seconds=t.tm_sec).total_seconds())
            elif t.count(":") == 2: # hour:min:sec
                t = time.strptime(t,'%H:%M:%S')
                secs = int(datetime.timedelta(hours=t.tm_hour,minutes=t.tm_min,seconds=t.tm_sec).total_seconds())
        elif i == 9: # Max RAM in kbytes
            ram = round(float(line.strip('\n').split(' ')[-1])/1024/1024, 1)
        i+=1
    print(s, secs, ram, sep=',')

def main():
    print("Step,Time(secs),RAM(GB)")
    SADs = [f"SAD{i}" for i in [1,2,4,8]]
    
    tool = "shark"
    steps = ["assoc"]
    for sample in samples:
        for step in steps:
            fpath = os.path.join(out_fold, tool, "{}.{}.time".format(sample, step))
            print_time_ram(fpath, tool + "." + step + "." + sample)

    tool = "STAR"

    for sad in SADs:
        fpath = os.path.join(in_fold, f"star_index_{sad}.time")
        print_time_ram(fpath, f"STAR.index.{sad}")

    for sample in samples:
        for sad in SADs:
            fpath = os.path.join(out_fold, tool, sad, sample + ".time")
            print_time_ram(fpath, tool + "." + sad + "." + sample)
            fpath = os.path.join(out_fold, "sharked_" + tool, sad, sample + ".time")
            print_time_ram(fpath, tool + ".sharked." + sad + "." + sample)

    tool = "salmon"
    fpath = os.path.join(in_fold, "salmon_index.time")
    print_time_ram(fpath, "salmon.index")
    for sample in samples:
        fpath = os.path.join(out_fold, tool, sample + ".time")
        print_time_ram(fpath, tool + "." + sample)
        fpath = os.path.join(out_fold, "sharked_" + tool, sample + ".time")
        print_time_ram(fpath, tool + "." + sample + ".sharked")

    tool = "rMATS"
    for sad in SADs:
        fpath = os.path.join(out_fold, tool, sad, tool + ".time")
        print_time_ram(fpath, tool + "." + sad)

    for sad in SADs:
        fpath = os.path.join(out_fold, f"sharked_{tool}", sad, "sharked_" + tool + ".time")
        print_time_ram(fpath, tool + ".sharked." + sad)

    tool = "spladder"
    for sad in SADs:
        for i in [1,2]:
            fpath = os.path.join(out_fold, tool, sad, f"difftest.{i}.time")
            print_time_ram(fpath, tool + f".{sad}.{i}")

    for sad in SADs:
        for i in [1,2]:
            fpath = os.path.join(out_fold, "sharked_" + tool, sad, f"difftest.{i}.time")
            print_time_ram(fpath, tool + f".sharked.{sad}.{i}")

    tool = "suppa2"
    steps = ["iso_tmp", "ioe", "psi", "dpsi"]
    for step in steps:
        fpath = os.path.join(out_fold, tool, "{}.time".format(step))
        print_time_ram(fpath, tool + ".{}".format(step))

        fpath = os.path.join(out_fold, "sharked_" + tool, "{}.time".format(step))
        print_time_ram(fpath, tool + ".{}".format(step) + ".sharked")

if __name__ == "__main__":
    main()
