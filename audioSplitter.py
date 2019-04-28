import subprocess
import argparse


argumentsDescMsg = 'Initialize bot optios.'
functionArgHelp  = 'function to use'
inputArgHelp     = 'input audio file'
outputDirArgHelp = 'output directory'
intervalsArgHelp = 'list of intervals of the form: hh:mm:ss(start) hh:mm:ss(end)'
funcDefault      = 'split_by_intervals'


def split_interval(input_file, output_file, start, end):
    split = 'ffmpeg -i {ifl} -ss {st} -vn -c copy -to {ed} {of}'.format(
            ifl=input_file, of=output_file, st=start, ed=end)
    subprocess.call(split, shell=True)


def split_by_intervals(inputFile, outputDir, intervals):
    for interval in intervals:
        outputFile = outputDir+'_'+interval['start']+'-'+interval['end']+inputFile[-4::1]
        split_interval(inputFile, outputFile, interval['start'], interval['end'])


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    #TODO: support for more functions
    #parser.add_argument('-f', metavar='FUNCTION', type=str, default=funcDefault, help=functionArgHelp)
    parser.add_argument('input', metavar='INPUT FAILE', type=str, help=inputArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT FILE', type=str, help=outputDirArgHelp)
    parser.add_argument('intervals', metavar='INTERVALS', type=str, nargs='+', help=intervalsArgHelp)
    args = parser.parse_args()
 
    intervals = [{'start':interval[0], 'end':interval[1]} for interval in 
            zip(args.intervals[0::2], args.intervals[1::2])]
    return {'audio':args.input, 'outputDir':args.outputdir, 'intervals':intervals}


def main():
    audioLine = parse_input()
    split_by_intervals(audioLine['input'], audioLine['outputDir'], audioLine['intervals'])


if __name__ == '__main__':
    main()
