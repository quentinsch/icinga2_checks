#!/usr/local/bin/python3.9

import argparse
import dns.resolver
import sys

dns_results = []


# Override default usage message of argparse
class CapitalisedHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'UNKNOWN - '
        return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)


# Read command line arguments
parser = argparse.ArgumentParser(exit_on_error=False, formatter_class=CapitalisedHelpFormatter,
                                 usage='Valid arguments are required to run this program.')
parser.add_argument('-i', '--ip_addresses', nargs='+', required=True, help='Provide IP addresses to expect as result.')
parser.add_argument('-d', '--domain', required=True, help='Provide a domain to do a DNS check on.')
parser.add_argument('-w', '--warning', required=False, action='store_true', default=False,
                    help='If this flag is set it will exit as warning.')
parser.add_argument('-c', '--critical', required=False, action='store_true', default=False,
                    help='If this flag is set it will exit as critical.')
try:
    args = parser.parse_args()
except SystemExit:
    parser.exit(status=3)

# Check A-record of domain
try:
    dns_query_result = dns.resolver.resolve(args.domain, 'A')
except dns.resolver.NXDOMAIN:
    print('UNKNOWN - Domain ' + str(args.domain) + ' cannot be resolved!')
    sys.exit(3)
except dns.resolver.NoAnswer:
    print('UNKNOWN - Domain ' + str(args.domain) + ' did not response with an answer!')
    sys.exit(3)
except dns.resolver.NoNameservers:
    print('UNKNOWN - Domain ' + str(args.domain) + ' has no name servers!')
    sys.exit(3)
except dns.resolver:
    print('UNKNOWN - Domain ' + str(args.domain) + ' has a resolving error!')
    sys.exit(3)

# Add all results of the DNS query to the result list
for dns_record in dns_query_result:
    dns_results.append(dns_record.to_text())

# Check results and exit with proper message and exit code
for dns_result in dns_results:
    if dns_result in args.ip_addresses:
        print('OK - Domain ' + str(args.domain) + ' resolves as expected IP: ' + str(dns_result))
        sys.exit(0)
    else:
        if args.critical:
            print('CRITICAL - Domain ' + str(args.domain) + ' does not resolve as one of the expected IP(s): ' + str(
                dns_result) + '!')
            sys.exit(2)
        if args.warning:
            print('WARNING - Domain ' + str(args.domain) + ' does not resolve as one of the expected IP(s): ' + str(
                dns_result) + '!')
            sys.exit(1)
        else:
            print('UNKNOWN - Domain ' + str(args.domain) + ' does not resolve as one of the expected IP(s): ' + str(
                dns_result) + '!')
            sys.exit(3)
