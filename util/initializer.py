import sys, argparse
import subprocess, time, os
import configparser

def initialize_setting():
    parser = argparse.ArgumentParser(description='Process some parameters')

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use, for testing purposes')

    parser.add_argument(
        '--server-ip',
        type=str,
        help='IP address of the server.',
        default='172.22.28.34') #192.168.40.148 10.79.140.204

    parser.add_argument(
        '--client-ip',
        type=str,
        help='IP address of the client mobilephone.',
        default='172.22.28.17') #192.168.40.206 10.79.94.122  -Jiayu 10.79.244.221 192.168.40.10

    parser.add_argument(
        '--client-if',
        type=str,
        help='Physical Interface.',
        default='wlxc04a001013bf')  #  enp4s0  wlxa42bb0c0012b

    parser.add_argument(
        '--wifi-server-ip',
        type=str,
        help='IP address of the server.',
        default='172.22.28.34')

    parser.add_argument(
        '--wifi-client-ip',
        type=str,
        help='IP address of the client mobilephone.',
        default='172.22.28.17')

    parser.add_argument(
        '--client-control-port',
        type=int,
        help='control port on the client side, used for signaling.',
        default=41003)

    parser.add_argument(
        '--server-control-port',
        type=int,
        help='control port on the server side, used for signaling.',
        default=41005)

    parser.add_argument(
        '--server-report-port',
        type=int,
        help='control port on the server side, used for reporting.',
        default=60040)

    parser.add_argument(
        '--client-report-port',
        type=int,
        help='control port on the client side, used for reporting.',
        default=60041)

    parser.add_argument(
        '--data-port',
        type=int,
        help='port used for data transmission.',
        default=41011)

    parser.add_argument(
        '--user-it-port',
        type=int,
        help='port used for user interaction transmission.',
        default=41012)

    parser.add_argument(
        '--symbols',
        type=int,
        help='number of symbols in each generation/block.',
        default=64)

    parser.add_argument(
        '--symbol-size',
        type=int,
        help='size of each symbol, in bytes.',
        default=1100) #byte-level serialization may solve pickling issue

    parser.add_argument(
        '--max-redundancy',
        type=float,
        help='maximum amount of redundancy to be sent, in percent.',
        default=110)

    parser.add_argument(
        '--timeout',
        type=float,
        help='timeout used for various sockets, in seconds.',
        default=0.1)

    # We have to use syg.argv for the dry-run parameter, because parse_args()
    # will fail with a "too few arguments" error if this is the only parameter
    if '--dry-run' in sys.argv:
        sys.exit(0)
    args = parser.parse_args()

    return args



def get_openarena(IS_FULLHD=True):
    # Openarena run command
    OPENARENA_FULLHD = 'openarena +set r_mode -1 r_customwidth 1920 r_customheight 1080'
    OPENARENA_NORMAL640X460 = 'openarena +set r_mode -1 r_customwidth 640 r_customheight 480'

    if IS_FULLHD:
        subprocess.Popen([OPENARENA_FULLHD, ], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    else:
        subprocess.Popen([OPENARENA_NORMAL640X460, ], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

    time.sleep(8)
    out = subprocess.Popen(['bash', 'bashscript.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    dim = list(map(int, str(stdout.decode("utf-8")).split()))
    return dim


def get_frame_dim():
    cur_dir = os.getcwd()
    config_path = os.path.join(cur_dir, 'config-ini.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    defaults = config['DEFAULT']
    frame_dim = defaults['FRAME_DIM']
    dim = [int(i) for i in frame_dim.split(",")]

    return dim

def get_video_path():
    cur_dir = os.getcwd()
    config_path = os.path.join(cur_dir, 'config-ini.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    defaults = config['DEFAULT']
    raw_video_path = defaults['RAW_VIDEO_PATH']

    return raw_video_path

def get_static_redundancy():
    cur_dir = os.getcwd()
    config_path = os.path.join(cur_dir, 'config-ini.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    defaults = config['DEFAULT']
    redundancy_value = defaults['REDUNDANCY_VALUE']

    return redundancy_value

def get_default_configurations():
    cur_dir = os.getcwd()
    config_path = os.path.join(cur_dir, 'config-ini.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    defaults = config['DEFAULT']

    return defaults


class Constants:
    # Frame type
    I_FRAME = 0
    P_FRAME = 1

    # What to protect
    PROTECT_I_FRAME = 2
    PROTECT_P_FRAME = 3
    PROTECT_BOTH = 4