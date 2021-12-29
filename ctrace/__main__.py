import argparse
import os
import sys


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')

    trace_parser = subparsers.add_parser('trace',
        help='Start tracing annotated containers')
    trace_parser.add_argument('--debug',
        default=False,
        action='store_true',
        help='Write eBPF events to /sys/kernel/debug/tracing/trace_pipe')

    options_parser = subparsers.add_parser('options',
        help='Generate run options with restrictions')
    options_parser.add_argument('Tracefile',
        help='File or directory with Tracefiles',
        nargs=argparse.ONE_OR_MORE)

    diff_parser = subparsers.add_parser('diff',
        help='Compare two Tracefiles')
    diff_parser.add_argument('Tracefile',
        help='Tracefile to compare',
        nargs=2)

    capability_parser = subparsers.add_parser('capability',
        help='Look up a capability')
    capability_parser.add_argument('query',
        help='ID or name to search',
        nargs=argparse.OPTIONAL)

    syscall_parser = subparsers.add_parser('syscall',
        help='Look up a syscall')
    syscall_parser.add_argument('query',
        help='ID or name to search',
        nargs=argparse.OPTIONAL)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.action == 'trace':
        from .cli.trace import main
        return main(
            debug=args.debug,
        )

    if args.action == 'diff':
        from .cli.diff import main
        return main(
            tracefile1=args.Tracefile[0],
            tracefile2=args.Tracefile[1],
        )

    if args.action == 'capability':
        from .cli.capability import main
        return main(
            query=args.query,
        )

    if args.action == 'syscall':
        from .cli.syscall import main
        return main(
            query=args.query,
        )

    parser.print_help()
    return os.EX_USAGE

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
