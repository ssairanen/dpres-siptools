# encoding: utf-8
"""Unit tests for ``siptools.scripts.import_object`` module"""
import sys
import os.path
import datetime
import lxml.etree as ET
import pytest
from siptools.scripts import import_object
from siptools.utils import encode_path
from siptools.xml.mets import NAMESPACES


def test_import_object_ok(testpath):
    """Test import_object.main funtion with valid test data."""
    input_file = 'tests/data/structured/Documentation files/readme.txt'
    arguments = ['--workspace', testpath, '--skip_inspection', input_file]
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file.decode('utf-8'),
                                                suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1

    assert return_code == 0


def test_import_object_skip_inspection_ok(testpath):
    """Test import_object.main function --skip-inspection argument."""
    input_file = 'tests/data/text-file.txt'
    arguments = ['--workspace', testpath, input_file, '--skip_inspection',
                 '--format_name', 'image/dpx', '--format_version', '1.0',
                 '--digest_algorithm', 'MD5', '--message_digest',
                 '1qw87geiewgwe9',
                 '--date_created', datetime.datetime.utcnow().isoformat()]
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
                                                suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1

    assert return_code == 0


def test_import_object_skip_inspection_nodate_ok(testpath):
    """Test import_object.main function without --date_created argument."""
    input_file = 'tests/data/text-file.txt'
    arguments = ['--workspace', testpath, input_file, '--skip_inspection',
                 '--format_name', 'image/dpx', '--format_version', '1.0',
                 '--digest_algorithm', 'MD5', '--message_digest',
                 '1qw87geiewgwe9']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
                                                suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1
    assert return_code == 0


def test_import_object_structured_ok(testpath):
    #TODO: Missing function docstring. What is the purpose of this test?
    workspace = os.path.abspath(testpath)
    test_data = os.path.abspath(os.path.join(os.curdir,
                                             'tests/data/structured'))
    test_file = ""
    for element in iterate_files(test_data):
        arguments = ['--workspace', workspace, '--skip_inspection',
                     os.path.relpath(element, os.curdir)]
        return_code = import_object.main(arguments)
        test_file = os.path.relpath(element, os.curdir)
        output = os.path.join(testpath,
                              encode_path(test_file,
                                          suffix='-premis-techmd.xml'))

        tree = ET.parse(output)
        root = tree.getroot()

        assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                              namespaces=NAMESPACES)) == 1
        assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
def test_import_object_validate_pdf_ok(testpath):
    """Test PDF validation in import_object.main funciton."""
    input_file = 'tests/data/test_import.pdf'
    arguments = ['--workspace', testpath, 'tests/data/test_import.pdf']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
                                                suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
                      namespaces=NAMESPACES)[0] == 'application/pdf'
    assert root.xpath('//premis:formatVersion/text()',
                      namespaces=NAMESPACES)[0] == '1.4'

    assert return_code == 0


def test_import_object_utf8(testpath):
    """Test importing works for file that:

    * is a utf-8 encoded text file
    * has utf-8 encoded filename
    * is in utf-8 encoded directory

    import_object.main should create TechMD-file with utf8-encoded filename.
    """

    # Create directory that contains one file
    utf8_directory = os.path.join(testpath, 'directory Ä')
    os.mkdir(utf8_directory)
    utf8_file = os.path.join(utf8_directory, 'testfile Ö')
    with open(utf8_file, 'w') as file_:
        file_.write('Voi änkeröinen.')

    # Run function
    assert import_object.main(['--workspace', testpath, '--skip_inspection',
                               utf8_file]) == 0

    # Check output
    output = os.path.join(testpath, encode_path(utf8_file.decode('utf-8'),
                                                suffix='-premis-techmd.xml'))
    tree = ET.parse(output)
    root = tree.getroot()
    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/valid_tiff.tif'])
def test_import_object_validate_tiff_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/valid_tiff.tif']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'image/tiff'
    assert root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)[0] == '6.0'

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/valid_jpeg.jpeg'])
def test_import_object_validate_jpeg_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/valid_jpeg.jpeg']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'image/jpeg'
    assert root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)[0] in ['1.0', '1.01', '1.02']

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/text-file.txt'])
def test_import_object_validate_text_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/text-file.txt']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'text/plain; charset=UTF-8'
    assert len(root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)) == 0

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/csvfile.csv'])
def test_import_object_validate_csv_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/csvfile.csv']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'text/plain; charset=ISO-8859-15'
    assert len(root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)) == 0

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/mets_valid_minimal.xml'])
def test_import_object_validate_mets_xml_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/mets_valid_minimal.xml']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'text/xml; charset=UTF-8'
    assert root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)[0] == '1.0'

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.parametrize('input_file', ['tests/data/ODF_Text_Document.odt'])
def test_import_object_validate_odt_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/ODF_Text_Document.odt']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(input_file,
        suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
        namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
        namespaces=NAMESPACES)[0] == 'application/vnd.oasis.opendocument.text'
    assert root.xpath('//premis:formatVersion/text()',
        namespaces=NAMESPACES)[0] == '1.0'

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.skipif(not os.path.exists('/opt/file-5.30/lib64/libmagic.so.1'),
                    reason='Requires file-5.30')
@pytest.mark.parametrize('input_file', ['tests/data/MS_Excel_97-2003.xls'])
def test_import_object_validate_msexcel_ok(input_file, testpath):
    arguments = ['--workspace', testpath, 'tests/data/MS_Excel_97-2003.xls']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(
        input_file, suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
                      namespaces=NAMESPACES)[0] == 'application/vnd.ms-excel'
    assert root.xpath('//premis:formatVersion/text()',
                      namespaces=NAMESPACES)[0] == '11.0'

    assert return_code == 0


@pytest.mark.skipif('ipt' not in sys.modules, reason='Requires ipt')
@pytest.mark.skipif(not os.path.exists('/opt/file-5.30/lib64/libmagic.so.1'),
                    reason='Requires file-5.30')
@pytest.mark.parametrize('input_file',
                         ['tests/data/MS_Word_2007-2013_XML.docx'])
def test_import_object_validate_msword_ok(input_file, testpath):
    arguments = ['--workspace', testpath,
                 'tests/data/MS_Word_2007-2013_XML.docx']
    return_code = import_object.main(arguments)

    output = os.path.join(testpath, encode_path(
        input_file, suffix='-premis-techmd.xml'))

    tree = ET.parse(output)
    root = tree.getroot()

    assert len(root.xpath('/mets:mets/mets:amdSec/mets:techMD',
                          namespaces=NAMESPACES)) == 1
    assert root.xpath('//premis:formatName/text()',
                      namespaces=NAMESPACES)[0] == \
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.'
         'document')
    assert root.xpath('//premis:formatVersion/text()',
                      namespaces=NAMESPACES)[0] == '15.0'

    assert return_code == 0


def test_import_object_fail():
    """Test that import_object.main raises error if target file does not
    exist
    """
    input_file = 'tests/data/missing-file'
    with pytest.raises(IOError):
        arguments = [input_file]
        import_object.main(arguments)


@pytest.mark.parametrize('input_charset,output_charset',
                         [('ISO-8859-15', 'ISO-8859-15'),
                          ('ISO-8859-1', 'ISO-8859-15'),
                          ('US-ASCII', 'ISO-8859-15'),
                          ('UTF-8', 'UTF-8'),
                          ('UTF-16', 'UTF-16'),
                          ('UTF-16LE', 'UTF-16'),
                          ('UTF-16BE', 'UTF-16'),
                          ('UTF-32', 'UTF-32')])
def test_return_charset_ok(input_charset, output_charset):
    """Test ``return_charset`` function with valid inputs"""
    assert import_object.return_charset(input_charset) == output_charset


def test_return_charset_invalid():
    """Test ``return_charset`` function with invalid charset as input."""
    with pytest.raises(ValueError):
        import_object.return_charset('KOI8-R')


def iterate_files(path):
    """Iterate through all files inside a directory."""
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            yield os.path.join(root, name)
