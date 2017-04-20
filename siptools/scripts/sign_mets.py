"""Command line tool for creating digital signatures for SIP"""

import sys
import argparse
import ipt.sip.signature


def main(arguments=None):
    """The main method for sign_mets"""
    args = parse_arguments(arguments)

    signature = ipt.sip.signature.ManifestSMIME(
        signature_filename=args.signature_filename,
        private_key=args.private_key,
        public_key=args.private_key,
        target_path=args.file_to_sign
    )

    signature.write_signature_file()

    print "sign_mets created file: %s" % args.signature_filename

    return 0


def parse_arguments(arguments):
    """ Create arguments parser and return parsed command line argumets"""
    parser = argparse.ArgumentParser(
        description="Create digital signature (signature.sig) for METS file.")

    parser.add_argument(
        "file_to_sign", default="mets.xml",
        help="File to be signed. Default is mets.xml")
    parser.add_argument(
        "signature_filename", default="signature.sig",
        help="Filename for signature default is signature.sig")
    parser.add_argument("private_key", help="Path for private key")

    return parser.parse_args(arguments)


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
