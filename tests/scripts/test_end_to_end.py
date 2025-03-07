"""End to end test for the siptools package."""
from __future__ import unicode_literals

import os
import subprocess
import sys
import pytest


@pytest.mark.e2e
def test_end_to_end(testpath):
    """Test creation of SIP and asserting the validity
    of the created mets document with validation tools.
    """

    objects = 'tests/data/single/text-file.txt'
    dmd_file = 'tests/data/import_description/metadata/dc_description.xml'
    dmd_target = 'tests/data/single'
    file_to_sign = 'mets.xml'
    private_key = 'tests/data/rsa-keys.crt'

    environment = os.environ.copy()
    environment['PYTHONPATH'] = '.'
    environment['PYTHONIOENCODING'] = 'UTF-8'

    # Get the name of the currently running Python executable
    python = sys.executable

    command = [python, 'siptools/scripts/import_object.py',
               '--workspace', testpath, objects, '--skip_wellformed_check',
               '--file_format', 'text/plain', '',
               '--checksum', 'MD5', '1qw87geiewgwe9',
               '--date_created', '2017-01-11T10:14:13',
               '--charset', 'ISO-8859-15']
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/premis_event.py', 'creation',
               '2017-01-11T10:14:13', '--event_detail', 'Testing',
               '--event_outcome', 'success', '--event_outcome_detail',
               'Outcome detail', '--workspace', testpath, '--agent_name',
               'Demo Application', '--agent_type', 'software',
               '--event_target', objects]
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/import_description.py', dmd_file,
               '--workspace', testpath, '--dmdsec_target', dmd_target,
               '--remove_root']
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/compile_structmap.py',
               '--workspace', testpath]
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/compile_mets.py',
               '--workspace', testpath, 'ch', 'CSC',
               'urn:uuid:89e92a4f-f0e4-4768-b785-4781d3299b20',
               '--create_date', '2017-01-11T10:14:13',
               '--copy_files', '--clean']
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/sign_mets.py',
               '--workspace', testpath, private_key]
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    command = [python, 'siptools/scripts/compress.py',
               '--tar_filename', os.path.join(testpath, 'sip.tar'), testpath]
    child = subprocess.Popen(command, env=environment)
    child.communicate()
    assert child.returncode == 0

    schematron_path = '/usr/share/dpres-xml-schemas/schematron/'
    schematron_rules = [
        'mets_addml.sch',
        'mets_amdsec.sch',
        'mets_audiomd.sch',
        'mets_digiprovmd.sch',
        'mets_dmdsec.sch',
        'mets_ead3.sch',
        'mets_filesec.sch',
        'mets_mdwrap.sch',
        'mets_metshdr.sch',
        'mets_mix.sch',
        'mets_mods.sch',
        'mets_premis_digiprovmd.sch',
        'mets_premis_rightsmd.sch',
        'mets_premis.sch',
        'mets_premis_techmd.sch',
        'mets_rightsmd.sch',
        'mets_root.sch',
        'mets_sourcemd.sch',
        'mets_structmap.sch',
        'mets_techmd.sch',
        'mets_videomd.sch'
    ]
    for rule in schematron_rules:
        rule_path = os.path.join(schematron_path, rule)
        command = [
            python, '-m' 'ipt.scripts.check_xml_schematron_features', '-s',
            rule_path, os.path.join(testpath, file_to_sign)
        ]
        child = subprocess.Popen(command, env=environment)
        child.communicate()
        assert child.returncode == 0
