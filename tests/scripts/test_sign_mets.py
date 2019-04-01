"""Tests for ``siptools.scripts.sign_mets`` module"""
import os
import shutil
from click.testing import CliRunner
import siptools.scripts.sign_mets


def test_valid_sign_mets(testpath):
    """Test """

    output = os.path.join(testpath, 'signature.sig')
    signing_key = 'tests/data/rsa-keys.crt'
    arguments = ['--workspace', testpath, signing_key]

    # Create mets file in workspace
    mets = os.path.join(testpath, 'mets.xml')
    mets_source = 'tests/data/text-file.txt'
    shutil.copy(mets_source, mets)

    runner = CliRunner()
    result = runner.invoke(siptools.scripts.sign_mets.main, arguments)
    assert result.exit_code == 0

    with open(output) as open_file:
        assert "4ddd69b778405b4072d77762a85f9cf5e8e5ca83" in open_file.read()
