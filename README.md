# ANANTA — PRIMORDIAL AI Architecture

**स्थिति:** executable software foundation v0.2  
**PRIMORDIAL** = शोध/डिजाइन दर्शन; **ANANTA** = उस पर आधारित AI system; **ANCIENT MAGIC** = प्राचीन ज्ञान से प्रेरित, आधुनिक विज्ञान द्वारा जाँचे जा सकने वाले प्रयोग।

ANANTA modular AI orchestration framework है। इसका पहला लक्ष्य input routing, task planning, evidence discipline, self-review, audit logging और permission-gated tools को एक स्पष्ट नियंत्रण-ढाँचे में लागू करना है। यह subjective consciousness का दावा नहीं करता।

## आठ modules
- **RITA:** नियम, dependency और consistency checks
- **VAK:** input validation और language metadata
- **MANAS:** task focus और working-state
- **BUDDHI:** structured task plan
- **AHAMKARA:** identity, role और capability boundaries
- **SAKSHI:** self-review और unsupported-claim flags
- **PRAMANA:** claim/evidence ledger और uncertainty
- **YANTRA:** allowlisted external actions और approval gate

## Run
Python 3.11+:
```bash
python -m pip install -e ".[dev]"
pytest -q
python -m ananta
```
Runtime core standard-library-only है; pytest केवल development dependency है।

## Safety invariants
1. बिना evidence वाला claim verified fact नहीं बनेगा।
2. Internal confidence score calibrated probability नहीं है।
3. External actions default-deny हैं।
4. High-impact actions के लिए explicit human approval अनिवार्य है।
5. हर action decision audit log में दर्ज होगा।
6. कोई module safety gate को override नहीं कर सकता।
7. AI consciousness का दावा नहीं किया जाएगा।

## सीमाएँ
यह deterministic software foundation है—trained LLM, autonomous web researcher, payment processor, robotics controller या consciousness test नहीं। Audit log अभी in-memory है; process बंद होने पर मिट जाता है। इन क्षमताओं को आगे अलग adapters, persistent storage और परीक्षणों के साथ जोड़ा जाएगा।

देखें: [Architecture](docs/architecture.md), [Security](SECURITY.md)।
