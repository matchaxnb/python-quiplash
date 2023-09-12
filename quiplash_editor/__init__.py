"""quiplash_editor: tools to edit quiplash data files
"""
import json
from dataclasses import dataclass, asdict
from typing import List
import csv

SAFETY_QUIPS_DEFAULT = [
    'jus de gouille',
    'le buszy',
    'jean-marc'
]
class RowImportError(Exception):
    """Cannot import a row"""

class UnknownPromptVersionError(Exception):
    """The given prompt is of an unsupported version"""

class UnsupportedConversionError(Exception):
    """Cannot convert prompt between these versions"""
    
def infer_prompt_version(prompt: dict):
    if 'includes_player_name' in prompt:
        return 3
    elif all(a in prompt for a in ('id', 'prompt', 'x')):
        return 1
    else:
        raise UnknownPromptVersionError(f"Cannot identify {prompt}")

def as_csv_dict(obj, *args, dict_factory=dict):
    """Convert dataclass item to CSV-friendly dict"""
    dct = asdict(obj, *args, dict_factory=dict_factory)
    quip_list_types = {str(k): isinstance(v, list) for k, v in dct.items()}
    for field_name, is_list in quip_list_types.items():
        if not is_list:
            continue
        new_field_name = f"{field_name.removesuffix('s')}_"
        for i, item in enumerate(dct[field_name]):
            dct[f"{new_field_name}{i +1}"] = item
        del dct[field_name]
    return dct

@dataclass(kw_only=True)
class QuipPromptBase:
    """Base class for Quiplash prompts with utility functions to convert between versions"""
    id: int
    x: bool
    prompt: str

    def to_quiplashv1(self):
        """Provide a QuipPromptV1 version of a prompt"""
        return QuipPromptV1(
            id=int(self.id),
            x=self.x,
            prompt=self.prompt.replace('<ANYPLAYER>', '<ANY PLAYER>')
        )
    
    def to_quiplashv3(self):
        """Provide a QuipPromptV3 version of a prompt"""
        if isinstance(self, QuipPromptV1):
            prompt = self.prompt.replace('<ANY PLAYER>', '<ANYPLAYER>')
            includes_player_name = '<ANYPLAYER>' in prompt
            return QuipPromptV3(
                id=str(self.id),
                x=self.x,
                us=False,
                prompt=prompt,
                includes_player_name=includes_player_name,
                safety_quips=list(SAFETY_QUIPS_DEFAULT),
            )
        else:
            return QuipPromptV3(**asdict(self))
        
    def to_version(self, target_version=None):
        """Convert Quiplash prompt to target version"""
        if target_version is None:
            return self
        elif target_version == 1:
            return self.to_quiplashv1()
        elif target_version == 3:
            return self.to_quiplashv3()
        else:
            raise UnknownPromptVersionError(f"Cannot convert to unknown target_version {target_version}")
@dataclass(kw_only=True)
class QuipPromptV1(QuipPromptBase):
    """A Quiplash quip prompt for Quiplash 1 & 2"""
    id: int

    @classmethod
    def from_pet_entry(cls, entry: dict):
        """build a QuipPromptV1 from a .pet entry
        
        Takes care of converting whatever is missing"""
        ver = infer_prompt_version(entry)
        if ver == 1:
            return cls(
                id=int(entry['id']),
                prompt=entry['prompt'],
                x=bool(entry['x'])
            )
        elif ver == 3:
            return cls(
                id=int(entry['id']),
                prompt=entry['prompt'].replace('<ANYPLAYER>', '<ANY PLAYER>'),
                x=bool(entry['prompt'])
            )
        else:
            raise UnsupportedConversionError(f"Can't convert to QuipPromptV1 from ver {ver}")

    def to_pet_entry(self):
        """Convert QuipPromptV1 object to entry in Quiplash and Quiplash 2 PET format"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "x": self.x
        }

@dataclass(kw_only=True)
class QuipPromptV3(QuipPromptBase):
    """A Quiplash quip prompt for Quiplash 3"""
    id: str
    includes_player_name: bool
    safety_quips: List[str]
    us: bool

    def to_pet_entry(self):
        """Convert QuipPromptV3 object to entry in Quiplash 3 PET format"""
        return {
            "id": self.id,
            "includesPlayerName": self.includes_player_name,
            "prompt": self.prompt,
            "safetyQuips": self.safety_quips,
            "us": self.us,
            "x": self.x
        }

    @classmethod
    def from_pet_entry(cls, entry: dict):
        """build a QuipPromptV3 from a .pet entry
        
        Takes care of converting whatever is missing"""
        q = cls(
            id=entry.get('id'),
            includes_player_name=entry.get('includesPlayerName', False),
            prompt=entry.get('prompt').replace('<ANY PLAYER>', '<ANYPLAYER>'),
            safety_quips=entry.get('safetyQuips', list(SAFETY_QUIPS_DEFAULT)),
            us=entry.get('us', False),
            x=entry.get('x')
            )
        q.includes_player_name = '<ANYPLAYER>' in q.prompt
        return q

    @classmethod
    def from_csv_entry(cls, entry: dict):
        """build a QuipPromptV3 from a CSV entry"""
        return cls(
            id=entry.get('id'),
            includes_player_name=entry.get('includes_player_name'),
            prompt=entry.get('prompt'),
            safety_quips=[entry.get(f'safety_quip_{a}') for a in range(1, 4)],
            us=entry.get('us'),
            x=entry.get('x')
        )
class QuiplashReader:
    target_version = None

    @property
    def quip_prompts(self):
        """the quip prompts that this reader holds"""
        return self._quip_prompts

    def __init__(self, pet_path=None, csv_path=None):
        self._quip_prompts = []
        self._csv_fields = []
        if pet_path:
            self.load_pet(pet_path)
        if csv_path:
            self.load_csv(csv_path)

    def load_pet(self, path):
        """load a PET file"""
        with open(path, 'rb') as fh:
            self._data = json.load(fh)
        self.read()

    def load_csv(self, path):
        """load a CSV file"""
        with open(path, newline='', encoding='utf-8') as fh:
            csvreader = csv.DictReader(fh)
            self._csv_fields = csvreader.fieldnames
            for row in csvreader:
                self.load_csv_row(row)

    def load_csv_row(self, row):
        """load a row from a CSV file"""
        if self._csv_fields is None:
            raise RowImportError("load_csv_row: cannot load data")
        
    def read(self):
        """load Quiplash file"""

    def serialize(self, to_version=None):
        """Generate a serialized .pet from the contents"""
        return json.dumps({"content": [a.to_version(self.target_version).to_pet_entry() for a in self.quip_prompts]}, indent=2, ensure_ascii=False) + "\n"

    def serialize_to_csv(self, path, to_version=None):
        """Generate a CSV version of the contents, for edition"""
        first_quip = as_csv_dict(self.quip_prompts[0].to_version(to_version))
        quip_keys = list(first_quip.keys())
        # detect fields which are arrays
        quip_list_types = {str(k): isinstance(v, list) for k, v in first_quip.items()}
        for field_name, is_list in quip_list_types.items():
            if not is_list:
                continue
            new_field_name = f"{field_name.removesuffix('s')}_"
            quip_keys.remove(field_name)
            for i in range(1, len(first_quip[field_name] + 1)):
                quip_keys.append(f"{new_field_name}{i}")
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.DictWriter(csvfile, dialect='excel', fieldnames=quip_keys)
            csvwriter.writeheader()
            for quip_prompt in self.quip_prompts:
                csvwriter.writerow(as_csv_dict(quip_prompt))

    @classmethod
    def from_pet_file(cls, path):
        """load QuiplashReader from Quiplash pet datafile"""
        c = cls()
        c.load_pet(path)
        return c

    @classmethod
    def from_csv_file(cls, path):
        """load QuiplashReader from CSV file"""
        c = cls()
        c.load_csv(path)
        return c
class QuiplashReaderV3(QuiplashReader):
    """A Quiplash reader for Quiplash3"""
    target_version = 3

    def read(self):
        contents = self._data['content']
        for item in contents:
            self._quip_prompts.append(QuipPromptV3.from_pet_entry(item))

class QuiplashReaderV1(QuiplashReader):
    """A Quiplash reader for Quiplash and Quiplash 2"""
    target_version = 1
    def read(self):
        contents = self._data['content']
        for item in contents:
            self._quip_prompts.append(QuipPromptV1.from_pet_entry(item))
