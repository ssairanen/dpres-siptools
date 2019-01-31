"""Tests for ``siptools.scripts.create_audiomd`` module"""

import os.path
import pytest
import lxml.etree as ET

import siptools.scripts.create_audiomd as create_audiomd

AUDIOMD_NS = 'http://www.loc.gov/audioMD/'
NAMESPACES = {"amd": AUDIOMD_NS}


def test_create_audiomd_elem():
    """Test that ``create_audiomd`` returns valid audiomd.
    """

    audiomd = create_audiomd.create_audiomd(
        "tests/data/audio/valid-wav.wav")["0"]

    file_data = "/amd:AUDIOMD/amd:fileData"
    audio_info = "/amd:AUDIOMD/amd:audioInfo"

    # Check namespace
    assert audiomd.nsmap["amd"] == "http://www.loc.gov/audioMD/"

    # Check individual elements
    path = "/amd:AUDIOMD[@ANALOGDIGITALFLAG='FileDigital']"
    assert len(audiomd.xpath(path, namespaces=NAMESPACES)) == 1

    path = "%s/amd:audioDataEncoding" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PCM'

    path = "%s/amd:bitsPerSample" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '16'

    path = "%s/amd:compression/amd:codecCreatorApp" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unap)'

    path = "%s/amd:compression/amd:codecCreatorAppVersion" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unap)'

    path = "%s/amd:compression/amd:codecName" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == \
        'PCM signed 16-bit little-endian'

    path = "%s/amd:compression/amd:codecQuality" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'lossless'

    path = "%s/amd:dataRate" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '768'

    path = "%s/amd:dataRateMode" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'Fixed'

    path = "%s/amd:samplingFrequency" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '48'

    path = "%s/amd:duration" % audio_info
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PT0.77S'

    path = "%s/amd:numChannels" % audio_info
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '1'


def test_stream():
    """Test that ``create_audiomd`` returns valid audiomd from a
       video container.
    """

    audiomd = create_audiomd.create_audiomd(
        "tests/data/video/mp4.mp4")["1"]

    file_data = "/amd:AUDIOMD/amd:fileData"
    audio_info = "/amd:AUDIOMD/amd:audioInfo"

    path = "%s/amd:audioDataEncoding" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'AAC'

    path = "%s/amd:bitsPerSample" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '0'

    path = "%s/amd:compression/amd:codecCreatorApp" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unav)'

    path = "%s/amd:compression/amd:codecCreatorAppVersion" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unav)'

    path = "%s/amd:compression/amd:codecName" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == \
        'AAC (Advanced Audio Coding)'

    path = "%s/amd:compression/amd:codecQuality" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unav)'

    path = "%s/amd:dataRate" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '385'

    path = "%s/amd:dataRateMode" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'Fixed'

    path = "%s/amd:samplingFrequency" % file_data
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '48'

    path = "%s/amd:duration" % audio_info
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PT5.31S'

    path = "%s/amd:numChannels" % audio_info
    assert audiomd.xpath(path, namespaces=NAMESPACES)[0].text == '6'


def test_invalid_wav_file():
    """Test that calling create_audiomd() for file that can not be parsed
    raises ValueError
    """
    with pytest.raises(ValueError):
        create_audiomd.create_audiomd("non-existent.wav")


def test_create_audiomd(testpath):
    """Test that ``create_audiomd`` writes AudioMD file and
    amd-reference file.
    """
    creator = create_audiomd.AudiomdCreator(testpath)

    # Debug print
    print "\n\n%s" % ET.tostring(
        create_audiomd.create_audiomd("tests/data/audio/valid-wav.wav")["0"],
        pretty_print=True
    )

    # Append WAV and broadcast WAV files with identical metadata
    creator.add_audiomd_md("tests/data/audio/valid-wav.wav")
    creator.add_audiomd_md("tests/data/audio/valid-bwf.wav")

    creator.write()

    # Check that amd-reference and one AudioMD-amd files are created
    assert os.path.isfile(os.path.join(testpath, 'amd-references.xml'))

    filepath = os.path.join(
        testpath, '704fbd57169eac3af9388e03c89dd919-AudioMD-amd.xml'
        # testpath, '4dab7d9d5bab960188ea0f25e478cb17-AudioMD-amd.xml'
    )

    assert os.path.isfile(filepath)


@pytest.mark.parametrize("file, base_path", [
    ('tests/data/audio/valid-wav.wav', ''),
    ('./tests/data/audio/valid-wav.wav', ''),
    ('audio/valid-wav.wav', 'tests/data'),
    ('./audio/valid-wav.wav', './tests/data'),
    ('data/audio/valid-wav.wav', 'absolute')
])
def test_paths(testpath, file, base_path):
    """ Test the following path arguments:
    (1) Path without base_path
    (2) Path without base bath, but with './'
    (3) Path with base path
    (4) Path with base path and with './'
    (5) Absolute base path
    """
    if 'absolute' in base_path:
        base_path = os.path.join(os.getcwd(), 'tests')

    if base_path != '':
        create_audiomd.main(['--workspace', testpath, '--base_path',
                             base_path, file])
    else:
        create_audiomd.main(['--workspace', testpath, file])

    assert "file=\"" + os.path.normpath(file) + "\"" in \
        open(os.path.join(testpath, 'amd-references.xml')).read()

    assert os.path.isfile(os.path.normpath(os.path.join(base_path, file)))
