from chemicals import search_chemical, phase_change, safety, elements
from rdkit import Chem
from rdkit.Chem import Draw
from io import BytesIO
import re
import sqlcon
from PIL import Image

def is_element(chemical_formula):
    formula_pattern = r'^[A-Z][a-z]*\d*$'  
    if re.match(formula_pattern, chemical_formula):
        return True
    else:
        return False


def ctsub(text):
    subscript_mapping = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
    return text.translate(subscript_mapping)

def imgdata(smiles):
    mol = Chem.MolFromSmiles(smiles) # type: ignore
    img = Draw.MolToImage(mol, size=(400, 400))
    image_stream = BytesIO()
    img.save(image_stream, format='PNG') # type: ignore
    image_stream.seek(0)
    return image_stream

def process_data(chemname):
    try:
        chems = search_chemical(chemname)
    except ValueError:
        data = sqlcon.GetChemicalData(chemname)
        if not data:
            return None
        with open(data[13], 'rb') as image_file:
            image = Image.open(image_file)
            image_bytesio = BytesIO()
            image.save(image_bytesio, format='JPEG')         
        ChemData = {"formula":data[1],"common":data[2],"iupac":data[3],"MW":data[4]}
        IdData = {"CAS":data[5],"smiles":data[6],"pubchemid":data[7]}
        SafetyData = {"carcinogen":data[8],"skin":data[9]}
        PhyData = {"BP":data[10],"MP":data[11],"flash":data[12]}
        OtherData = {"img":image,"synonyms":data[14]}
        chem = [ChemData,IdData,SafetyData,PhyData,OtherData]
        return chem
    cas_number = str(chems.CAS)
    fcas = re.sub(r'(\d+)(\d{2})(\d{1})', r'\1-\2-\3', cas_number)
    formula=ctsub(chems.formula)
    smiles = chems.smiles
    pubchemid = chems.pubchemid
    iupac = chems.iupac_name
    common = chems.common_name
    MolWeight = chems.MW
    BP = phase_change.Tb(fcas)
    BP = str(round(BP,2))+"° K" if BP else "No Data"
    MP = phase_change.Tm(fcas)
    MP = str(MP)+"° K" if MP else "No Data"
    carcinogen = safety.Carcinogen(CASRN=fcas)
    skin = safety.Skin(CASRN=fcas)
    skin = skin if skin else "No Data"
    flash = safety.T_flash(CASRN=fcas, method='IEC 60079-20-1 (2010)')
    flash = str(flash)+"° K" if flash else "Data not available"
    ChemData = {"formula":ctsub(formula),"common":common,"iupac":iupac,"MW":MolWeight}
    IdData = {"CAS":fcas,"smiles":smiles,"pubchemid":pubchemid}
    SafetyData = {"carcinogen":carcinogen,"skin":skin}
    PhyData = {"BP":BP,"MP":MP,"flash":flash}
    OtherData = {"img":imgdata(smiles),"synonyms":chems.synonyms}
    chem = [ChemData,IdData,SafetyData,PhyData,OtherData]
    return chem

def datatrends(start,stop):
    attributes = {1:'number',2:'MW',3:'rcov',4:'rvdw',5:'maxbonds',6:'ionization',7:'S0'}
    prompt = '''
    What trend do you want visualize 
    1) Atomic Number
    2) Molecular Weight
    3) Covalent/Ionic Radius
    4) Vander Waal's Radius
    5) Maximum number of bonds
    6) Ionization Enthalpy
    7) Standard absolute entropy
'''
    YLABEL = ['Atomic Number','Molecular Weight','Covalent/Ionic Radius','Vander Waal Radius','Maximum Number of Bonds','Ionization Enthalpy','Standard Absolute Entropy']
    choice = int(input(prompt))
    values=[]
    for i in range(start,stop+1):
        a= elements.periodic_table[i]
        value = getattr(a,attributes[choice])
        values.append(value)
    return values, YLABEL[choice-1]
