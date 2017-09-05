import os
import sys
from urllib2 import urlopen

CHUNK = 16 * 1024


def download_file_from_url(src_url, media_type, event_id):
        '''Download file locally from url
        url - url to file
        type - either 'image' or 'video'

        returns filename
        '''
        filename = create_filename(media_type, event_id)
        # write to tmp, because that's the only write-access an aws lambda gets
        filepath = '/tmp/{}'.format(filename)

        delete_file(filepath)

        saved_filepath = download(src_url, filepath)
        return filename, saved_filepath


def download(src_url, filepath):
    # urlib is 10x faster than using requests to download large files
    res = urlopen(src_url)

    total_size = res.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0

    with open(filepath, 'wb') as wb:
        while True:
            chunk = res.read(CHUNK)
            if not chunk:
                break
            wb.write(chunk)

            bytes_so_far = bytes_so_far + CHUNK
            progress_bar(bytes_so_far, CHUNK, total_size)

    return filepath


def progress_bar(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    sys.stdout.write("Downloaded %0.2f of %0.2f Mb (%0.2f%%)\r" % (bytes_so_far / 1000000, total_size / 1000000, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError:
        # failed to remove, thats fine
        pass


def create_filename(media_type, event_id):
    '''Create filename from GroupMe files types
    '''
    type_to_ext = {
        'image': '.jpeg',
        'video': '.mp4',
    }
    filename = '{}{}'.format(event_id, type_to_ext[media_type])

    return filename
