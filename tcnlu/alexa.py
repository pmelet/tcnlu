import re, json, uuid
from tcnlu.tools import get, enforce_list, flatten, walk_array
from tcnlu.humans import numbers as transform_numbers
from tcnlu.objects import *

class Alexa:
    _alexa_name_patern = re.compile('[^a-zA-Z0-9_]+')
    def _alexa_name(self, string):
        return transform_numbers(self._alexa_name_patern.sub('_', string).lower())

    def _verify_intent(self, intent, lang="en", reject_literals=False):
        name = intent.get("name")
        samples = intent.samples.get(lang)
        if not samples:
            print ("reject intent \"",name,"\" as it contains no utterances")
            return False, None, None
        collected_slots, any_literal = self.collect_slots(samples)
        if reject_literals and any_literal:
            print ("reject intent \"",name,"\" as it contains AMAZON.Literal")
            return False, None, None
        return True, samples, collected_slots

    def _get_type(self, item):
        """
        Given an object Item, determine whether the type is Standard ot Custom
        Return : type name, True if LITERAL
        """
        meta = item.meta
        if meta and type(meta) == StandardType:
            meta = meta.get("alexa")
            return meta, meta == "AMAZON.LITERAL"
        elif meta and type(meta) == CustomType:
            meta = meta.name
            return self._alexa_name(meta), False
        raise Exception("item %r has not type" % item)

    def collect_slots(self, samples):
        """
        Read all samples and collect slots mentionned
        Return: list of (slot name, type)
        """
        slots = set()
        any_literal = False
        for sample in samples:
            for item in sample:
                alias = item.name
                if alias:
                    meta, is_literal = self._get_type(item)
                    any_literal |= is_literal
                    if type(meta) == dict:
                        for k,v in meta.items():
                            slots.add((self._alexa_name(alias + "_" + k), v))
                    else:
                        slots.add((self._alexa_name(alias), meta))
        return slots, any_literal

class AlexaGenerator(Alexa):
    def __init__(self):
        pass

    def generate(self, source, lang="en", **kwargs):
        name, intents, entities = source.get_name(), source.get_intents(), source.get_entities()
        reject_literals = kwargs.get("no_literal", False)
        dialog_intents, prompts = self.generate_prompts(intents, lang=lang, reject_literals=reject_literals)
        ret = {
            "interactionModel": {
                "languageModel": {
                    "invocationName": name,
                    "intents": self.generate_intents(intents, add_default=True, lang=lang, reject_literals=reject_literals),
                    "types": self.generate_entities(entities, lang=lang)
                },
                "dialog": {
                    "intents": dialog_intents
                },
                "prompts": prompts
            }
        }
        return json.dumps(ret, indent=2)

    def generate_prompts(self, intents, lang="en", reject_literals=False):
        dialog_intents_slots, dialog_prompts = defaultdict(list), []
        for intent in intents.values():
            name = intent.get("name")
            ok, _, _ = self._verify_intent(intent, lang=lang, reject_literals=reject_literals)
            if not ok:
                continue
            for slot in intent.slots:
                if slot.required:
                    dataType = slot.dataType.get("alexa")
                    id = str(uuid.uuid4())
                    prompts = slot.prompts.get(lang)
                    if prompts:
                        dialog_prompts.append({
                            "id": "Elicit.Slot."+id,
                            "variations": [{
                                "type": "PlainText",
                                "value": value
                            } for value in prompts]
                        })
                        intent_name = self._alexa_name(name)
                        dialog_intents_slots[intent_name].append({
                            "name": self._alexa_name(slot.name),
                            "type": dataType,
                            "confirmationRequired": False,
                            "elicitationRequired": True,
                            "prompts": {
                                "elicitation": "Elicit.Slot."+id,
                            }
                        })

        dialog_intents = []
        for intent_name, slots in dialog_intents_slots.items():
            dialog_intents.append({
                "name": intent_name,
                "confirmationRequired": False,
                "prompts": {},
                "slots": slots
            })
        return dialog_intents, dialog_prompts

    def generate_intents(self, intents, add_default=True, lang="en", reject_literals=False):
        """
        Read intents objects, and generate alexa intents
        """
        ret = []
        for intent in intents.values():
            name = intent.get("name")
            ok, samples, collected_slots = self._verify_intent(intent, lang=lang, reject_literals=reject_literals)
            if not ok:
                continue
            instance_samples = [ [ self.get_sample_element(item) for item in items ] for items in samples ]
            item = {
                "name": self._alexa_name(name),
                "samples": self.flatten_samples(instance_samples)
            }
            slots = [{"name":name, "type": atype} for (name, atype) in collected_slots]
            if slots:
                item["slots"] = slots
            ret.append(item)
        return ret

    _alexa_sample_pattern = re.compile('[^a-zA-Z0-9{} ]+')
    def get_sample_element(self, item):
        """
        Given an Item object, generate the Alexa representation of the part of sample is represents
        Return: string
        """
        alias, source_text = item.name, item.text
        text = transform_numbers(source_text)
        text = self._alexa_sample_pattern.sub('', text)
        if alias:
            meta, example = self._get_type(item)
            if example:
                return" {%s|%s} " % (text, self._alexa_name(alias))
            if type(meta) == dict:
                return [" {%s} " % self._alexa_name(alias + "_" + k) for k,v in meta.items()]
            return " {%s} " % self._alexa_name(alias)
        return text

    def flatten_samples(self, samples):
        ret = []
        for sample in samples:
            for s in walk_array(sample):
                ret.append("".join(s))
        return list(set(map(str.lower, ret)))

    def generate_entities(self, entities, lang="en"):
        """
        """
        ret = []
        for entity in entities.values():
            ret.append({
                "name": self._alexa_name(entity.get("name")),
                "values": [{"name": entry} for entry in entity.get_entries(lang)]
            })
        return ret


class AlexaResponseGenerator(Alexa):
    def __init__(self):
        pass

    def generate(self, source, lang="en", **kwargs):
        reject_literals = kwargs.get("no_literal", False)
        intents = source.get_intents()
        ret = {}
        for intent in intents.values():
            ok, _, _ = self._verify_intent(intent, lang=lang, reject_literals=reject_literals)
            if not ok:
                continue
            name = self._alexa_name(intent.get("name"))
            resp = intent.responses.get(lang)
            if resp:
                ret[name] = list(filter(lambda x:x is not None, resp))
        return json.dumps(ret, indent=2)
