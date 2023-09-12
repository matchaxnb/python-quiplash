"""take the given PET file (first argument), copy it as a QuiplashV3 .pet file, and as a CSV file"""
from . import QuiplashReaderV3, QuiplashReaderV1
import sys

# qpath = sys.argv[1]
# output = sys.argv[2]
# reader = QuiplashReaderV3(qpath)

# print(reader.quip_prompts)
# print(reader.serialize())
# with open(output, "w", encoding="utf-8") as fh:
#     fh.write(reader.serialize())
# 
# reader.serialize_to_csv(output + ".csv")

def to_v3_pet(orig_file, v3_output):
    """Convert to V3 PET """
    reader = QuiplashReaderV3(orig_file)
    with open(v3_output, "w", encoding="utf-8") as fh:
        fh.write(reader.serialize())

def to_v3_csv(orig_file, v3_csv_output):
    """Convert to V3 CSV"""
    reader = QuiplashReaderV3(orig_file)
    reader.serialize_to_csv(v3_csv_output, to_version=3)

def to_v1_pet(orig_file, v1_output):
    """Convert to V3 PET """
    reader = QuiplashReaderV1(orig_file)
    with open(v1_output, "w", encoding="utf-8") as fh:
        fh.write(reader.serialize())

def to_v1_csv(orig_file, v1_csv_output):
    """Convert to V3 CSV"""
    reader = QuiplashReaderV1(orig_file)
    reader.serialize_to_csv(v1_csv_output, to_version=1)

def csv_to_v1(csv_file, v1_output):
    """Convert CSV file to V1 PET"""
    reader = QuiplashReaderV1.from_csv_file(csv_file)
    with open(v1_output, "w", encoding="utf-8") as fh:
        fh.write(reader.serialize(to_version=1))

def csv_to_v3(csv_file, v3_output):
    """Convert CSV file to V1 PET"""
    reader = QuiplashReaderV3.from_csv_file(csv_file)
    with open(v3_output, "w", encoding="utf-8") as fh:
        fh.write(reader.serialize(to_version=3))

fun_map = {
    'to_v3_pet': to_v3_pet,
    'to_v3_csv': to_v3_csv,
    'to_v1_pet': to_v1_pet,
    'to_v1_csv': to_v1_csv,
    'csv_to_v1': csv_to_v1,
    'csv_to_v3': csv_to_v3,
}

try:
    request = sys.argv[1]
except IndexError:
    request = None
if request not in fun_map:
    raise ValueError(f"Operation not supported: must be one of {'|'.join(list(fun_map.keys()))}")

try:
    the_in, the_out = sys.argv[2], sys.argv[3]
except IndexError as e:
    raise ValueError(f"Usage: {request} IN_FILE OUT_FILE") from e

fun_map[request](the_in, the_out)
