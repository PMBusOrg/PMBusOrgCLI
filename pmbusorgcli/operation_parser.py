import logging
from lxml import etree, objectify
from camel_snake_kebab import snake_case

from .byte_helpers import hexstr_to_bytes

from .smbus_helpers import smbus_transaction_types,\
    smbus_transaction_write_types,\
    smbus_transaction_read_types,\
    smbus_transaction_process_call_types

# from byte_helpers import hexstr_to_bytes


class PMBusFileParser:

    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.tree = etree.parse(self.filepath, self.parser)
        self.root = self.tree.getroot()

        assert self.root.tag == '{http://smbus.org/2017/SMBusCommandSequence}smbus'

        # strip namespace references
        for elem in self.root.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[(i + 1):]
        objectify.deannotate(self.root, cleanup_namespaces=True)

    def delay_step(self,
                   step_element):

        scale = step_element.attrib['scale']
        assert scale in ['s', 'ms']
        time_in_seconds = int(step_element.attrib['time'])
        if(scale == 'ms'):
            time_in_seconds /= 100

        step_dict = dict(
            {'step_type': step_element.tag},
            **{'time_in_seconds': time_in_seconds})
        return step_dict

    def smbus_transaction_step(self,
                               smbus_transaction,
                               device_info_dict,
                               step_element):

        step_dict = dict(device_info_dict,
                         **{'step_type': smbus_transaction},
                         **{'pec': step_element.attrib['pec'] == 'True'})

        # grab child data
        trans_subelements = []
        trans_subelements_tags = []
        for child in step_element:
            trans_subelements.append(child)
            trans_subelements_tags.append(child.tag)

        assert 'command' in step_element.attrib
        command_bytes = hexstr_to_bytes(step_element.attrib['command'])
        if((smbus_transaction == 'send_byte') or
           (smbus_transaction == 'receive_byte')):
            assert len(command_bytes) == 1

        step_dict = dict(step_dict, **{'command': command_bytes})

        if(((smbus_transaction in smbus_transaction_write_types) or
            (smbus_transaction in smbus_transaction_process_call_types)) and
           ((smbus_transaction != 'send_byte') and
                (smbus_transaction != 'receive_byte'))):
            assert 'data' in trans_subelements_tags
            data_text = trans_subelements[
                trans_subelements_tags.index('data')].text
            data_bytes = hexstr_to_bytes(data_text)
            step_dict = dict(step_dict, **{'data': data_bytes})

        if((smbus_transaction in smbus_transaction_read_types) or
           (smbus_transaction in smbus_transaction_process_call_types)):
            # process optional elements expect & mask
            if 'expect' in trans_subelements_tags:
                expect_bytes = hexstr_to_bytes(trans_subelements[
                    trans_subelements_tags.index('expect')].text)
                step_dict = dict(step_dict, **{'expect': expect_bytes})
            if 'mask' in trans_subelements_tags:
                mask_bytes = hexstr_to_bytes(trans_subelements[
                    trans_subelements_tags.index('mask')].text)
                step_dict = dict(step_dict, **{'mask': mask_bytes})

        return step_dict

    def operation_device_steps(self, device_info_dict, device_element):
        steps = []

        for step in device_element:
            step_type = snake_case(step.tag)
            if step_type in smbus_transaction_types:
                stepdata = self.smbus_transaction_step(
                    step_type,
                    device_info_dict,
                    step)
            elif step_type == 'delay':
                stepdata = self.delay_step(
                    step)
            else:
                logging.error('Error: unsupported operation step tag %s',
                              step.tag)
            steps.append(stepdata)

        return steps

    def operation_steps(self, operation_element):
        # operation steps are flattened to
        # have device information in every step
        steps = []
        for device in operation_element:
            assert device.tag == 'device'
            device_address_str = device.attrib['address']
            device_address_unshifted = bytes([int(device_address_str, 0)])
            device_info_dict = {'device_address': device_address_unshifted,
                                'device_name': device.attrib['name']}

            device_steps = self.operation_device_steps(
                device_info_dict,
                device)
            [steps.append(device_step) for device_step in device_steps]

        return steps

    def operations(self, system_element):
        operations = []
        for child in system_element:
            assert child.tag == 'op'
            operations.append({'element': child, 'data': child.attrib})
        return operations

    def systems(self):
        systems = []
        for child in self.root:
            assert child.tag == 'system'
            systems.append({'element': child, 'data': child.attrib})
        return systems
