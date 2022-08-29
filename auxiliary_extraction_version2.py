# author: Xiaomeng (Miranda) Zhu
# version 2 updated on Aug 19
# purpose: extracting morphosyntactic features of interest from txt file
  
import os
import pandas as pd # library for creating dataframes and storing into csv
import re
import spacy

# os.chdir('/Users/mirandazhu/Desktop/demo') # CHANGE ME: the folder where you store the txt file of the speaker

# global variables:
speakerID = "DCB_se1_ag2_m_02_3" # CHANGE ME: name of the txt file that you downloaded
speaker = "DCB_se1_ag2_m_02" # CHANGE ME: the speaker ID in the transcription
file_name = speakerID + ".txt"

# set up language model for part of speech tagging
nlp = spacy.load("en_core_web_sm")

# ========== Part 1: preprocessing ==========
def read_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    return lines

def filter_speakers(lines):
    """
    return a list of lists of the form [Line, Spkr, StTime, Content, EnTime]
    """
    filtered = [line.split("\t") for line in lines if ((line.split("\t")[1]) == speaker)]
    return filtered

def get_all_sentences(lines):
    # sentence content is the third element in the list
    sents = [sent_list[3] for sent_list in lines]
    return sents


# ========= Part 2: auxiliary extraction =========
def find_all_not_fully_contracted_N(sent):
    BE_N = {"is not": 0, "are not": 0, "am not": 0, "'s not": 0, "'re not": 0, "'m not": 0, "not": 0}
    HV_N = {"have not": 0, "has not": 0, "'ve not": 0, "'s not": 0}
    DO_N = {"do not": 0, "does not": 0, "did not": 0}

    # if this sentence contains a "not", tokenize this string using spacy and determine specific category
    # regex meaning: 
    # not either preceded by a non alphanumeric character or begins at sentence boundary
    # and either followed by a non alphanumeric character or ends at sentence boundary
    if bool(re.search(r"(?:\W|^)not(?:\W|$)", sent)):

        doc = nlp(sent)
        tokens = [(token.text, token.pos_) for token in doc] # get all (token, pos) pairs

        for idx, (token, pos) in enumerate(tokens):
            if (token.lower() == "not") and (idx != 0):
                # only go into this branch if the "not" token is not the first word of this sentence
                # assumes that all "not" tokens that follow auxiliaries (including covert auxiliaries) cannot be the first word in a sentence
                
                prev_token = tokens[idx-1][0].lower()
           
                if prev_token in ["is", "are", "am"]:
                    BE_N[prev_token + " not"] += 1
                elif prev_token in ["have", "has"]:
                    HV_N[prev_token + " not"] += 1
                elif prev_token in ["do", "does", "did"]:
                    DO_N[prev_token + " not"] += 1
                elif prev_token.endswith("'re"):
                    BE_N["'re not"] += 1
                elif prev_token.endswith("'m"):
                    BE_N["'m not"] += 1
                elif prev_token.endswith("'ve"):
                    HV_N["'ve not"] += 1
                elif prev_token.endswith("'s"): 
                    # 's could be a contracted is or has, so we need to check the part of speech of the following word
                    if idx != len(tokens)-1: # only precede to POS check if there is a next token
                        next_token_spacy = doc[idx+1]
                        next_pos = tokens[idx+1][1]
                        if (next_pos == "VERB") and (next_token_spacy.morph.get("Tense") != []) and (next_token_spacy.morph.get("Tense")[0]=="Past"): # 's is a contracted has
                            HV_N["'s not"] += 1
                        else: # 's is a contracted is
                            BE_N["'s not"] += 1
                else: # not is not preceded with any auxiliaries
                    BE_N["not"] += 1
            elif (token.lower() == "not") and (idx == 0): # if not is the first token in the sentence 
                BE_N["not"] += 1


    return BE_N, HV_N, DO_N

def find_contracted_s(sent):
    BE_P = {"'s": 0}
    HV_P = {"'s": 0}
    # the code below will only change keys that are 's in the above two dicts

    if bool(re.search(r"'s\W(?!not)", sent, re.IGNORECASE)): # if this sentence contains a 's that is not followed by not
        doc = nlp(sent)
        tokens = [(token.text, token.pos_) for token in doc]
        for idx, (token, pos) in enumerate(tokens):
            if bool(re.search(r"'s(?:\W|$)", token, re.IGNORECASE)) and (idx != len(tokens) - 1): 
                # if there is a token following the token that ends with 's
                next_token_spacy = doc[idx+1]
                next_pos = tokens[idx+1][1]
                if (next_pos == "VERB") and (next_token_spacy.morph.get("Tense") != []) and (next_token_spacy.morph.get("Tense")[0]=="Past"): # 's is a contracted has
                    HV_P["'s"] += 1
                else: # 's is a contracted is
                    BE_P["'s"] += 1 # CAUTION: does not distinguish possessive 's

            elif bool(re.search(r"'s(?:\W|$)", token, re.IGNORECASE)) and (idx == len(tokens) - 1):
                # if the token containing 's is the last word of the sentence, categorize it as BE_P
                BE_P["'s"] += 1

    return BE_P, HV_P


def find_BE_P(sent):
    # BE_P: is, are, am, 's, 're, 'm
    BE_P = {
        "is": 0, 
        "are": 0,
        "am": 0,
        "'re": 0,
        "'m": 0
    }

    is_ = re.findall(r"(?:\W|^)is(?:\W|$)(?!not)", sent, re.IGNORECASE) # using this variable name because "is" is reserved in python
    are = re.findall(r"(?:\W|^)are(?:\W|$)(?!not)", sent, re.IGNORECASE)
    am = re.findall(r"(?:\W|^)am(?:\W|$)(?!not)", sent, re.IGNORECASE)
    ap_re = re.findall(r"'re(?:\W|$)(?!not)", sent, re.IGNORECASE)
    ap_m = re.findall(r"'m(?:\W|$)(?!not)", sent, re.IGNORECASE)
    
    # res = ["is"] * len(is_) + ["are"] * len(are) + ["am"] * len(am) + ["'s"] * len(ap_s) + ["'re"] * len(ap_re) + ["'m"] + len(ap_m)
    BE_P["is"] = len(is_)
    BE_P["are"] = len(are)
    BE_P["am"] = len(am)
    BE_P["'re"] = len(ap_re)
    BE_P["'m"] = len(ap_m)

    return BE_P

def find_BE_fullycontracted_N(sent):
    # BE_N: 
    # not fully contracted: is (not), are (not), am (not), 's (not), 're (not), 'm (not), not
    # fully contracted: isn't, aren't
    BE_N = {"isn't": 0, "aren't": 0}
    
    isnt = re.findall(r"(?:\W|^)isn't(?:\W|$)", sent, re.IGNORECASE)
    arent = re.findall(r"(?:\W|^)aren't(?:\W|$)", sent, re.IGNORECASE)

    # res = ["isn't"] * len(isnt) + ["aren't"] * len(arent)
    BE_N["isn't"] = len(isnt)
    BE_N["aren't"] = len(arent)

    return BE_N

def find_HV_P(sent):
    HV_P = {
        "have": 0, # does not distinguish possessive have vs. auxiliary have
        "has": 0,
        "'ve": 0,
    }
    have = re.findall(r"(?:\W|^)have(?:\W|$)(?!not)", sent, re.IGNORECASE)
    has = re.findall(r"(?:\W|^)has(?:\W|$)(?!not)", sent, re.IGNORECASE)
    ap_ve = re.findall(r"'ve(?:\W|$)(?!not)", sent, re.IGNORECASE)
    
    # ap_s = re.findall(r"'s(?!\snot)", sent, re.IGNORECASE)
    # res = ["have"] * len(have) + ["has"] * len(has) + ["'ve"] * len(ap_ve)

    HV_P["have"] = len(have)
    HV_P["has"] = len(has)
    HV_P["'ve"] = len(ap_ve)

    return HV_P


def find_HV_fullycontracted_N(sent):
    # HV_N: 
    # not fully contracted: have (not), has (not), 've (not), 's (not)
    # fully contracted: haven't, hasn't

    HV_N = {"haven't": 0, "hasn't": 0}
    havent = re.findall(r"(?:\W|^)haven't(?:\W|$)", sent, re.IGNORECASE)
    hasnt = re.findall(r"(?:\W|^)hasn't(?:\W|$)", sent, re.IGNORECASE)

    HV_N["haven't"] = len(havent)
    HV_N["hasn't"] = len(hasnt)

    return HV_N

def find_DO_P(sent):
    # DO_P: do, does, did
    DO_P = {
        "do": 0, 
        "does": 0,
        "did": 0,
    }
    do = re.findall(r"(?:\W|^)do(?:\W|$)(?!not)", sent, re.IGNORECASE)
    does = re.findall(r"(?:\W|^)does(?:\W|$)(?!not)", sent, re.IGNORECASE)
    did = re.findall(r"(?:\W|^)did(?:\W|$)(?!not)", sent, re.IGNORECASE)
    
    DO_P["do"] = len(do)
    DO_P["does"] = len(does)
    DO_P["did"] = len(did)

    return DO_P

def find_DO_fullycontracted_N(sent):
    # DO_N:
    # not fully contracted: do (not), does (not), did (not)
    # fully contracted: don't, doesn't, didn't

    DO_N = {
        "don't": 0, 
        "doesn't": 0,
        "didn't": 0
    }

    dont = re.findall(r"(?:\W|^)don't(?:\W|$)", sent, re.IGNORECASE)
    doesnt = re.findall(r"(?:\W|^)doesn't(?:\W|$)", sent, re.IGNORECASE)
    didnt = re.findall(r"(?:\W|^)didn't(?:\W|$)", sent, re.IGNORECASE)

    DO_N["don't"] = len(dont)
    DO_N["doesn't"] = len(doesnt)
    DO_N["didn't"] = len(didnt)
    
    return DO_N


def find_AI(sent):
    # AI: ain't

    res = re.findall(r"(?:\W|^)ain't(?:\W|$)", sent, re.IGNORECASE)

    return {"ain't": len(res)}

def collect_all_aux(sent):
    # negative constructions
    BE_N, HV_N, DO_N = find_all_not_fully_contracted_N(sent)

    BE_N_2 = find_BE_fullycontracted_N(sent)
    HV_N_2 = find_HV_fullycontracted_N(sent)
    DO_N_2 = find_DO_fullycontracted_N(sent)

    BE_N.update(BE_N_2)
    HV_N.update(HV_N_2)
    DO_N.update(DO_N_2)

    # positive constructions
    BE_P, HV_P = find_contracted_s(sent)

    BE_P.update(find_BE_P(sent))
    HV_P.update(find_HV_P(sent))

    DO_P = find_DO_P(sent)

    AI = find_AI(sent)

    return BE_N, HV_N, DO_N, BE_P, HV_P, DO_P, AI

def main():
    res = []
    lines = read_file(file_name)
    filtered = filter_speakers(lines)
    all_sents = get_all_sentences(filtered)
    
    # for each sentence with auxiliary, append category and token
    for idx, sent in enumerate(all_sents):
        BE_N, HV_N, DO_N, BE_P, HV_P, DO_P, AI = collect_all_aux(sent)
        master_dict = {
            "BE_N": BE_N,
            "HV_N": HV_N,
            "DO_N": DO_N,
            "BE_P": BE_P, 
            "HV_P": HV_P, 
            "DO_P": DO_P,
            "AI": AI,
        }
        for category_name in master_dict:
            category_dict = master_dict[category_name]
            for token in category_dict:
                count = category_dict[token]
                if count != 0:
                    for i in range(count):
                        row = [] + filtered[idx]
                        row.append(category_name)
                        row.append(token)
                        res.append(row)

    res_df = pd.DataFrame(res)
    res_df.columns =['Line', 'Spkr', 'StTime', 'Content', 'EnTime', 'Label', 'Aux']
    res_df.to_csv(speakerID+"_new.csv")


if __name__ == "__main__":
    # doc = nlp("that's why I said that it was kind of sad that it's changing because")
    # sent = "Not everyone has not been is not"
    # print(find_all_not_fully_contracted_N(sent))
    # print(collect_all_aux(sent))
    # token = doc[-2]  # 'I'
    # # print(token.text)
    # # print(token.morph)  # 'Case=Nom|Number=Sing|Person=1|PronType=Prs'
    # print(token.morph.get("Tense"))  # ['Prs']
    main()