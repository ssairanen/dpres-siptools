"""Command line tool for creating audioMD metadata."""
import sys
import os
import click
import pickle
import audiomd
from siptools.utils import AmdCreator, scrape_file

FILEDATA_KEYS = ['audio_data_encoding', 'bits_per_sample',
    'data_rate', 'data_rate_mode', 'sampling_frequency']

AUDIOINFO_KEYS = ['duration', 'num_channels']

ALLOW_UNAV = ['audio_data_encoding', 'codec_creator_app',
              'codec_creator_app_version', 'codec_name',
              'duration', 'num_channels']
ALLOW_ZERO = ['bits_per_sample', 'data_rate', 'sampling_frequency']


@click.command()
@click.argument(
    'filename', type=str)
@click.option(
    '--workspace', type=click.Path(exists=True), default='./workspace/',
    help="Workspace directory for the metadata files.")
@click.option(
    '--base_path', type=click.Path(exists=True), default='.',
    help="Source base path of digital objects. If used, give path to "
         "the file in relation to this base path.")
def main(workspace, base_path, filename):
    """
    Write audioMD metadata for an audio file or streams.

    FILENAME: Relative path to the file from current directory
              or from --base_path.
    """

    filerel = os.path.normpath(filename)
    filepath = os.path.normpath(os.path.join(base_path, filename))

    creator = AudiomdCreator(workspace)
    creator.add_audiomd_md(filepath, filerel)
    creator.write()


class AudiomdCreator(AmdCreator):
    """Subclass of AmdCreator, which generates audioMD metadata
    for audio files.
    """

    def add_audiomd_md(self, filepath, filerel=None):
        """Create audioMD metadata for a audio file and append it
        to self.md_elements.
        """

        # Create audioMD metadata
        audiomd_dict = create_audiomd(filepath, filerel, self.workspace)

        for index in audiomd_dict.keys():
            if '0' in audiomd_dict and len(audiomd_dict) == 1:
                self.add_md(audiomd_dict[index],
                            filerel if filerel else filepath)
            else:
                self.add_md(audiomd_dict[index],
                            filerel if filerel else filepath, index)

    def write(self, mdtype="OTHER", mdtypeversion="2.0",
              othermdtype="AudioMD"):
        super(AudiomdCreator, self).write(mdtype, mdtypeversion, othermdtype)


def fix_missing_metadata(streams, filename):
    """If an element is none, use value (:unav) if allowed in the
    specifications. Otherwise raise exception.
    """
    for index, stream in streams.iteritems():
        for key, element in stream.iteritems():
            if key in ['mimetype', 'stream_type', 'index', 'version']:
                continue
            if element in [None, '(:unav)']:
                if key in ALLOW_UNAV:
                    stream[key] = '(:unav)'
                elif key in ALLOW_ZERO:
                    stream[key] = '0'
                else:
                    raise ValueError('Missing metadata value for key %s in '
                                     'index %s for file %s' % (
                                        key, str(index), filename))


def create_audiomd(filename, filerel=None, workspace=None):
    """Creates and returns list of audioMD XML sections.
    :filename: Audio file path
    :returns: List of AudioMD XML sections.
    """
    streams = scrape_file(filename, filerel=filerel, workspace=workspace)
    fix_missing_metadata(streams, filename)

    audiomd_dict = {}
    for index, stream_md in streams.iteritems():
        if stream_md['stream_type'] != 'audio':
            continue
        file_data_elem = _get_stream_data(stream_md)
        audio_info_elem = _get_audio_info(stream_md)

        audiomd_elem = audiomd.create_audiomd(
            file_data=file_data_elem,
            audio_info=audio_info_elem
        )
        audiomd_dict[str(index)] = audiomd_elem

    if not audiomd_dict:
        raise ValueError('Audio stream info could not be constructed.')

    return audiomd_dict


def _get_stream_data(stream_dict):
    """Creates and returns the fileData XML element.
    :stream_dict: Stream dictionary given by Scraper
    :returns: AudioMD fileData element
    """
    params = {}
    for key in FILEDATA_KEYS:
        keyparts = key.split('_')
        camel_key = keyparts[0] + ''.join(x.title() for x in keyparts[1:])
        params[camel_key] = stream_dict[key]

    compression = (stream_dict['codec_creator_app'],
                   stream_dict['codec_creator_app_version'],
                   stream_dict['codec_name'],
                   stream_dict['codec_quality'])

    params['compression'] = audiomd.amd_compression(*compression)

    return audiomd.amd_file_data(params)


def _get_audio_info(stream_dict):
    """Creates and returns the audioInfo XML element.
    :stream_dict: Stream dictionary given by Scraper
    :returns: AudioMD audioInfo element
    """
    return audiomd.amd_audio_info(
        duration=stream_dict['duration'],
        num_channels=stream_dict['num_channels'])


if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
