# pmbusorgcli init / main file
__version__ = '0.0.1'

import sys
import argparse
import logging
from pmbusorgcli import operation_parser

from pmbusorgcli.interfaces import dryrun
from pmbusorgcli.interfaces import aardvark

import pmbusorgcli.smbus_helpers as smbus_helpers
from .byte_helpers import byte_transmission_str

from time import sleep


def smbus_step_verbose_string(step):

    if(step['step_type'] in smbus_helpers.smbus_transaction_types):
        smbus_transaction = step['step_type']
        step_str = smbus_transaction + \
            ' on address 0x' + step['device_address'].hex() + ': '
        if smbus_transaction != 'receive_byte':
            step_str += ' cmd:' + byte_transmission_str(step['command'])
        if ((smbus_transaction != 'send_byte') and
            (smbus_transaction in
             smbus_helpers.smbus_transaction_write_types) or
            (smbus_transaction in
             smbus_helpers.smbus_transaction_process_call_types)):
            step_str += ' data:' + byte_transmission_str(step['data'])
        if ((smbus_transaction in
             smbus_helpers.smbus_transaction_read_types) or
            (smbus_transaction in
             smbus_helpers.smbus_transaction_process_call_types)):
            if 'expect' in step:
                step_str += ' exp:' + byte_transmission_str(step['expect'])
            if 'mask' in step:
                step_str += ' w/mask:' + byte_transmission_str(step['mask'])
        if step['pec']:
            step_str += '[PEC]'

        return step_str


def smbus_step_handler(step,
                       interface,
                       is_verbose_mode):

    if(is_verbose_mode):
        step_string = smbus_step_verbose_string(step)
        print('Performing step: ' + step_string)
    smbus_transaction = step['step_type']
    if(smbus_transaction == 'send_byte'):
        interface.send_byte(step['device_address'],
                            step['command'],
                            step['pec'])
    elif(smbus_transaction == 'write_byte'):
        interface.write_byte(step['device_address'],
                             step['command'],
                             step['data'],
                             step['pec'])
    elif(smbus_transaction == 'write_word'):
        interface.write_word(step['device_address'],
                             step['command'],
                             step['data'],
                             step['pec'])
    elif(smbus_transaction == 'write_block'):
        interface.write_block(step['device_address'],
                              step['command'],
                              step['data'],
                              step['pec'])
    elif(smbus_transaction == 'receive_byte'):
        readback = interface.receive_byte(step['device_address'],
                                          step['pec'])
    elif(smbus_transaction == 'read_byte'):
        readback = interface.read_byte(step['device_address'],
                                       step['command'],
                                       step['pec'])
    elif(smbus_transaction == 'read_word'):
        readback = interface.read_word(step['device_address'],
                                       step['command'],
                                       step['pec'])
    elif(smbus_transaction == 'read_block'):
        readback = interface.read_block(step['device_address'],
                                        step['command'],
                                        step['pec'])
    elif(smbus_transaction == 'process_call'):
        readback = interface.process_call(step['device_address'],
                                          step['command'],
                                          step['data'],
                                          step['pec'])
    elif(smbus_transaction == 'block_process_call'):
        readback = interface.block_process_call(step['device_address'],
                                                step['command'],
                                                step['data'],
                                                step['pec'])

    if(smbus_transaction in smbus_helpers.smbus_transaction_write_types):
        return

    # check readback.
    if readback is None:
        logging.error('Readback value not returned, skipping')
        return

    if(interface.__class__.__module__ == 'pmbusorgcli.interfaces.dryrun'):
        print('Readback check: Dry run, no comparison performed')
        return

    if 'expect' in step:
        readback_expect = step['expect']
    else:
        logging.warning('Warning: no readback expect defined, skipping')
        return

    if 'mask' in step:
        readback_mask = step['mask']
    else:
        # create a default mask of 'FF' bytes
        readback_mask = bytes([255] * len(readback_expect))

    assert len(readback_mask) == len(readback)

    masked_readback = bytes(list(map(lambda maskbyte, readbackbyte:
                                     maskbyte & readbackbyte,
                                     readback_mask, readback)))

    if readback_expect == masked_readback:
        if is_verbose_mode:
            print('Readback match: readback ' +
                  byte_transmission_str(readback) +
                  ' (w/mask: ' + byte_transmission_str(readback_mask) +
                  ' ) matches expected ' +
                  byte_transmission_str(readback_expect))
    else:
        logging.error('Readback does NOT match - readback ' +
                      byte_transmission_str(readback) +
                      ' (w/mask: ' + byte_transmission_str(readback_mask) +
                      ' ) didn\'t match ' +
                      byte_transmission_str(readback_expect))


def steps_handler(steps,
                  interface,
                  is_verbose_mode):

    interface.open()

    for step in steps:
        step_type = step['step_type']
        if step_type in smbus_helpers.smbus_transaction_types:
            smbus_step_handler(step, interface, is_verbose_mode)
        elif step_type == 'delay':
            time = step['time_in_seconds']
            if(is_verbose_mode):
                print('Delay: waiting for ' + str(time) + ' seconds...')
            sleep(time)

    interface.close()


def operation_handler(opparser,
                      system_arg,
                      operation_arg,
                      interface_arg,
                      is_dry_run,
                      is_verbose_mode):

    # parse operation/steps
    systems = opparser.systems()
    system_names = list(map(lambda system: system['data']['name'], systems))
    if system_arg not in system_names:
        logging.error('Error, system %s not found in input file',
                      system_arg)
        return

    system_element = (systems[system_names.index(system_arg)])['element']
    operations = opparser.operations(system_element)
    operation_names = list(map(lambda operation: operation['data']['name'],
                               operations))
    if operation_arg not in operation_names:
        logging.error('Error, operation %s not found in input file',
                      operation_arg)
        return

    operation_element = (operations[
        operation_names.index(operation_arg)])['element']
    steps = opparser.operation_steps(operation_element)

    # find interface
    if(is_dry_run):
        print("Operating in dry run mode. (No transmissions will occur)")
        interface = dryrun.SMBusInterface()
    elif(interface_arg == 'aardvark'):
        print("Performing operation with aardvark interface")
        interface = aardvark.SMBusInterface()
    elif(interface_arg is None):
        logging.error("Error: SMBus interface not specified.\n\
            Use the -i argument with an available interface option")
        return
    else:
        logging.error("Error: Unsupported interface")
        return

    steps_handler(steps,
                  interface,
                  is_verbose_mode)


def list_system_ops(opparser):
        # list out the available systems and operations
    systems = opparser.systems()
    for system in systems:
        print('System: ' +
              system['data']['name'] +
              ' rev: ' +
              system['data']['revision'])
        print('  Description: ' +
              system['data']['description'])
        print('  Operations:')
        ops = opparser.operations(system['element'])
        for op in ops:
            print('    ' + op['data']['name'])


def run(args):
    argparser = argparse.ArgumentParser(
        description='PMBus.org command line interface tool')
    argparser.add_argument('file', type=argparse.FileType('r'),
                           default=sys.stdin,
                           help='The pmbus operation file (xml) to be used.')

    argparser.add_argument('-l', '--list', nargs='?', default=False,
                           const=True,
                           help='List available systems & operations.')

    argparser.add_argument('-s', '--system', type=str,
                           help='System name for the operation to be performed')
    argparser.add_argument('-o', '--operation', type=str,
                           help='System\'s operation name to be performed')

    argparser.add_argument('-i', '--interface', choices=['aardvark'],
                           help='Specify the pmbus host interface used.')
    argparser.add_argument('--dry-run', nargs='?', default=False, const=True,
                           help='Do not perform any actions on interface.')
    argparser.add_argument('-v', '--verbose',
                           nargs='?', default=False, const=True,
                           help='verbose mode')

    print('PMBusOrgCLI ' + __version__)

    args = argparser.parse_args()

    print('Parsing file: ' + args.file.name)
    opparser = operation_parser.PMBusFileParser(args.file.name)

    if(args.list):
        list_system_ops(opparser)

    elif((args.system is not None) and
         (args.operation is not None)):
        operation_handler(opparser,
                          args.system,
                          args.operation,
                          args.interface,
                          args.dry_run,
                          args.verbose)

    else:
        print('Error: Invalid options. Use pmbusorgcli to: \n' +
              '- List out systems/operations: \n' +
              '  \'pmbusorgcli.exe myFile.xml -l\' \n' +
              '- Perform an operation (dry run): \n' +
              '  \'pmbusorgcli.exe myFile.xml -s mySystem -o myOperation --dry-run --verbose \n' +
              '- Perform an operation (with interface): \n' +
              '  \'pmbusorgcli.exe myFile.xml -s mySystem -o myOperation -i aardvark --verbose \n')
