from . import QuiplashReaderV3
import sys

qpath = sys.argv[1]
output = sys.argv[2]
reader = QuiplashReaderV3(qpath)

# print(reader.quip_prompts)
print(reader.serialize())
with open(output, 'w', encoding='utf-8') as fh:
    fh.write(reader.serialize())

reader.serialize_to_csv(output + ".csv")

