import argparse

parser = argparse.ArgumentParser(
    description=(
        'Summarizes and plots completed DM/SL shifts.'
    )
)
parser.add_argument(
    '-r',
    '--rundb',
    help=(
        'Current rundb file, which can be download from '
        'https://lbrundb.cern.ch (in csv format).'
    ),
    required=True
)
parser.add_argument(
    '-s',
    '--shifters',
    help='Shifter names and timing slots for shifts (in json format).',
    required=True
)
parser.add_argument(
    '-o',
    '--output-dir',
    help='Plots and summary will be saved to this directory.',
    default='./results/'
)

def main():
    args = parser.parse_args()
    from . import shiftsummary
    import os

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    shiftsummary(args.rundb, args.shifters, args.output_dir)
