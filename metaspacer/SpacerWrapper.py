from subprocess import PIPE, STDOUT, Popen, run
import json
import os
import glob
from chctools import horndb as H
import io

class SpacerWrapper:

    def __init__(self, z3_path):
        self.spacer_process = None # Process | None
        self.spacer_state = None # "running" | "saturation" | "refutation" | "error" | "timeout" | None

        self.options_for_visualization = ["fp.spacer.trace_file=spacer.log", "fp.print_statistics=true", "-v:1"]
        self.z3_path = z3_path
        self.db = None
        self.rels = None
        #backup on instantiation
        self.backup_prev_run()

    def backup_prev_run(self):
        # how many runs are there
        no_of_runs = len(glob.glob("run_*"))
        new_folder = "run_"+str(no_of_runs)
        os.mkdir(new_folder)

        # move the files into the newly created folder
        if os.path.exists("input_file.smt2"): os.rename('input_file.smt2', '%s/input_file.smt2'%new_folder)
        if os.path.exists("verbose"): os.rename('verbose', '%s/verbose'%new_folder)
        if os.path.exists("stat"): os.rename('stat', '%s/stat'%new_folder)
        if os.path.exists(".z3-trace"): os.rename('.z3-trace', '%s/.z3-trace'%new_folder)
        if os.path.exists("spacer.log"): os.rename('spacer.log', '%s/spacer.log'%new_folder)
        for benchmark_file in glob.glob('pool_solver*'):
            os.rename(benchmark_file, "%s/%s"%(new_folder, benchmark_file))



    # run Spacer iteratively
    def startIterative(self, input_file, user_options):
        if self.spacer_process is not None:
            self.spacer_process.kill()
            print("Killing previous running Z3 Process")
            self.verbose_file.close()
            self.stat_file.close()
            # save all the data from previous runs
            self.backup_prev_run()
        args = [self.z3_path]
        args.extend(user_options.split())
        args.extend(self.options_for_visualization)
        args.append(input_file)

        #clear DB
        del self.db
        del self.rels

        #load the file into db for parsing in the future
        self.db = H.load_horn_db_from_file(input_file)
        self.rels = []
        for rel_name in self.db._rels:
            rel = self.db.get_rel(rel_name)
            self.rels.append(rel)

        self.verbose_file = open("verbose", "w")
        self.stat_file = open("stat", "w")

        print("Running cmd:\n%s"% " ".join(args))
        self.spacerProcess = Popen(args, stdin=PIPE, stdout=self.stat_file, stderr=self.verbose_file)
        
        return "success"

