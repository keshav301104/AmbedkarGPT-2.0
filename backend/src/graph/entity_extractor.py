import spacy

nlp = spacy.load("en_core_web_sm")

class EntityExtractor:
    def extract_entities(self, text):
        doc = nlp(text)
        entities = []
        
        # 1. Named Entities (People, Orgs, Laws)
        valid_labels = ["PERSON", "ORG", "GPE", "NORP", "LAW", "EVENT"]
        for ent in doc.ents:
            if ent.label_ in valid_labels:
                clean_ent = ent.text.strip().replace("\n", " ")
                if len(clean_ent) > 2:
                    entities.append(clean_ent)
        
        # 2. Key Concepts (Noun Phrases)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1: # Multi-word only
                clean_chunk = chunk.text.strip().replace("\n", " ")
                if len(clean_chunk) > 3 and len(clean_chunk) < 50:
                    entities.append(clean_chunk)

        return list(set(entities))