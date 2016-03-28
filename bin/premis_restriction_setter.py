import argparse
from os.path import abspath, isdir
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.premisextensionnodes import Restriction
from pypremis.lib import PremisRecord
from pypremis.nodes import *


def gather_records(path):
    records = []
    if isdir(path):
        for x in FileWalker(path, filter_pattern="^.*\.premis.xml$"):
            records.append((load_record(x), x))
    else:
        records.append((load_record(path), path))
    return records


def load_record(path):
    return PremisRecord(frompath=path)


def build_rights_extension_node(restriction_code, restriction_reason=None,
                                donor_stipulation=None, linkingAgentIds=None,
                                active=True):
    rights_extension = RightsExtension()
    rights_extension.add_to_field('Restriction', build_restriction_node(
        restriction_code=restriction_code,
        restriction_reason=restriction_reason,
        donor_stipulation=donor_stipulation,
        linkingAgentIds=linkingAgentIds,
        active=active))
    return rights_extension


def build_restriction_node(restriction_code, active=True,
                           restriction_reason=None, donor_stipulation=None,
                           linkingAgentIds=None):
    restrictionNode = Restriction(restriction_code, active)
    if restriction_reason:
        for x in restriction_reason:
            restrictionNode.add_restrictionReason(x)
    if donor_stipulation:
        for x in donor_stipulation:
            restrictionNode.add_donorStipulation(x)
    if linkingAgentIds:
        for x in linkingAgentIds:
            restrictionNode.add_linkingAgentIdentifier(x)
    return restrictionNode


def main():
    # parser instantiation
    parser = argparse.ArgumentParser(description='Set uchicagoldr premis ' +
                                     'rights extension restriction nodes' +
                                     'in existing premis object records.')

    parser.add_argument(
        'path',
        help='Specify a path to a premis record, or a path to search for '+
        'premis records, all of which will be acted upon.'
    )
    parser.add_argument(
        'restriction',
        # choices = somecontrolledvocabhere,
        # https://docs.python.org/3/library/argparse.html#choices
        help='Specify the restriction code to apply to all ' +
        'found PREMIS records.'
    )
    parser.add_argument(
        '--reason',
        default=None,
        action='append',
        help='Specify the reason for applying the restriction'
    )
    parser.add_argument(
        '--donor-stipulation',
        action='append',
        default=None,
        help='Specify a donor stipulation'
    )

    args = parser.parse_args()

    # app code
    path = abspath(args.path)
    record_tups = gather_records(path)

    for x in record_tups:
        record = x[0]
        rec_path = x[1]
        if record.get_rights_list():
            rights = record.get_rights_list()[0]
            try:
                rights_extension = rights.get_rightsExtension(0)
                rights_extension.add_to_field('Restriction',
                                              build_restriction_node(
                                              args.restriction,
                                              True,
                                              args.reason,
                                              args.donor_stipulation
                                              ))
            except KeyError:
                rights.add_rightsExtension(build_rights_extension_node(
                                              args.restriction,
                                              True,
                                              args.reason,
                                              args.donor_stipulation
                ))
        else:
            rights = Rights(rightsExtension=build_rights_extension_node(
            args.restriction,
            args.reason,
            args.donor_stipulation
            ))
            record.add_rights(rights)
        record.write_to_file(rec_path)


if __name__ == '__main__':
    main()
