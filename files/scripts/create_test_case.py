# © 2023 Codemaze and Codemaze-Web by Danilo Cleber Becke

from argparse import ArgumentParser
from os import linesep
import subprocess

# parse arguments
parser = ArgumentParser(usage='create_test_case.py \'python test.py\' 1 [-c]')
parser.add_argument('executable_command')
parser.add_argument('test_number')
parser.add_argument('--closed', '-c', help='whether this is a closed test', action='store_true')
parser.add_argument('--timeout', '-t', default=2, help='execution timeout. Default = 2')
args = parser.parse_args()

# execute
command = args.executable_command.split(' ')
exit_code = 1
stdin = ''
stdout = ''
while exit_code != 0:
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        stdin += input('# ') + linesep
        stdout, stderr = process.communicate(input=stdin, timeout=args.timeout)
        print('--- current input')
        print(stdin, end='')
        print('--- current output')
        print(stdout, end='')
        print('------------------')
        exit_code = process.returncode

# normalize stdin
stdin = stdin.replace(linesep, '\n')

# save files
base_filename = ('closed' if args.closed else 'open') + '_test_' + args.test_number
with open(base_filename + '.in', 'w', encoding='utf-8') as test_in:
    test_in.write(stdin)
with open(base_filename + '.out', 'w', encoding='utf-8') as test_out:
    test_out.write(stdout)
