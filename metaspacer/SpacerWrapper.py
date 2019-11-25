from subprocess import PIPE, STDOUT, Popen, run
import json
import os
import glob
class SpacerWrapper:

    def __init__(self, z3Path):
        self.spacerProcess = None # Process | None
        self.spacerState = None # "running" | "saturation" | "refutation" | "error" | "timeout" | None

        self.optionsForVisualization = ["fp.spacer.trace_file=spacer.log", "fp.print_statistics=true", "-v:1"]
        self.z3Path = z3Path

    # run Spacer fully automatically on the given input file, and return all the output generated by Spacer
    def start(self, inputFile, userOptions):
        if self.spacerProcess != None:
            print("Killing previous running Z3 Process")
            self.spacerProcess.kill()

        # note: if an option is supplied twice, Spacer ignores the first occurence
        #       we therefore add the user options first, so that user options conflicting
        #       with visualization options are ignored
        args = [self.z3Path]
        args.extend(userOptions.split())
        args.extend(self.optionsForVisualization)
        args.append(inputFile)

        verbose_file = open("verbose", "w")
        stat_file = open("stat", "w")
        self.spacerProcess = Popen(args, stdout=stat_file, stderr=verbose_file, universal_newlines=True)
        return_code = self.spacerProcess.wait()
        if return_code!=0:
            return {}, []
        else:
            with open("spacer.log", "r") as f:
                progress_trace = f.readlines()

            return progress_trace

    # run Spacer iteratively
    def startIterative(self, inputFile, userOptions):
        if self.spacerProcess != None:
            print("Killing previous running Z3 Process")
            self.spacerProcess.kill()

        # save all the data from previous runs
        # how many runs are there

        no_of_runs = len(glob.glob("run_*"))
        new_folder = "run_"+str(no_of_runs)
        os.mkdir(new_folder)

        # move the files into the newly created folder
        if os.path.exists("verbose"): os.rename('verbose', '%s/verbose'%new_folder)
        if os.path.exists("stat"): os.rename('stat', '%s/stat'%new_folder)
        if os.path.exists(".z3-trace"): os.rename('.z3-trace', '%s/.z3-trace'%new_folder)
        if os.path.exists("spacer.log"): os.rename('spacer.log', '%s/spacer.log'%new_folder)
        for benchmark_file in glob.glob('pool_solver*'):
            os.rename(benchmark_file, "%s/%s"%(new_folder, benchmark_file))

        # note: if an option is supplied twice, Spacer ignores the first occurence
        #       we therefore add the user options first, so that user options conflicting
        #       with visualization options are ignored

        args = [self.z3Path]
        args.extend(userOptions.split())
        args.extend(self.optionsForVisualization)
        args.append(inputFile)

        verbose_file = open("verbose", "w")
        stat_file = open("stat", "w")

        self.spacerProcess = Popen(args, stdin=PIPE, stdout=stat_file, stderr=verbose_file)
        
        return "success"

    # perform one clause selection using selectedId
    # return the output generated by that clause selection
    def select(self, selectedId):
        self.spacerProcess.stdin.write(str.encode(str(selectedId) + "\n"))
        self.spacerProcess.stdin.flush()

        newLines = self.collectOutput()
        return newLines

    # helper method
    def collectOutput(self):
        # process lines until a line occurs with either is 1) a commando to enter a number 2) refutation found 3) saturation reached 4) user error
        newLines = []
        line = self.spacerProcess.stdout.readline().decode().rstrip()
        while(True):
            if line.startswith("Pick a clause:"):
                self.spacerState = "running"
                return newLines
            elif line.startswith("% Refutation found. Thanks to"): # TODO: use SZS status instead?
                self.spacerState = "refutation"
                return newLines
            elif line.startswith("% SZS status Satisfiable"):
                self.spacerState = "saturation"
                return newLines
            elif line.startswith("User error: "):
                self.spacerState = "error"
                return newLines
            else:
                newLines.append(line)
                line = self.spacerProcess.stdout.readline().decode().rstrip()


