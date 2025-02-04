"""Module for all NER relying on spaCy."""

import logging
import os
from typing import List, Union

import spacy
from spacy.tokens import Doc, Token
from spacy.util import DummyTokenizer

from cltk.core.exceptions import CLTKException
from cltk.data.fetch import FetchCorpus
from cltk.utils.utils import file_exists, query_yes_no
from cltk.utils.utils import download_file


class CustomTokenizer(DummyTokenizer):
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, words):
        return Doc(self.vocab, words=words)


def download_prompt(
    iso_code: str,
    message: str,
    model_url: str,
    interactive: bool = True,
    silent: bool = False,
):
    """Ask user whether to download files.

    TODO: Make ft and stanza use this fn. Consider moving to other module.
    """
    fetch_corpus = FetchCorpus(language=iso_code)
    download_file(model_url, os.path.join(CLTK_DATA_DIR, "/cltk_data/"+iso_code))
    #little messy


def spacy_tag_ner(
    iso_code: str, text_tokens: List[str], model_path: str
) -> List[Union[str, bool]]:
    """Take a list of tokens and return label or None.

    >>> text_tokens = ["Gallia", "est", "omnis", "divisa", "in", "partes", "tres", ",", "quarum", "unam", "incolunt", "Belgae", ",", "aliam", "Aquitani", ",", "tertiam", "qui", "ipsorum", "lingua", "Celtae", ",", "nostra", "Galli", "appellantur", "."]
    >>> from cltk.utils import CLTK_DATA_DIR
    >>> spacy_tag_ner('lat', text_tokens=text_tokens, model_path=os.path.join(CLTK_DATA_DIR, "lat/model/lat_models_cltk/ner/spacy_model/"))
    ['LOCATION', False, False, False, False, False, False, False, False, False, False, 'LOCATION', False, False, 'LOCATION', False, False, False, False, False, 'LOCATION', False, False, 'LOCATION', False, False]
    """
    # make sure that we have a List[str]
    if not isinstance(text_tokens[0], str):
        raise CLTKException("`spacy_tag_ner()` requires `List[str]`.")
    if not os.path.isdir(model_path):
        msg = f"spaCy model path '{model_path}' not found. Going to try to download it ..."
        logging.warning(msg)
        dl_msg = f"This part of the CLTK depends upon models from the CLTK project."
        model_url = f"https://github.com/cltk/{iso_code}_models_cltk"
        download_prompt(iso_code=iso_code, message=dl_msg, model_url=model_url)
    spacy_nlp = spacy.load(model_path)
    # Create the tokenizer for the spacy model
    spacy_nlp.tokenizer = CustomTokenizer(vocab=spacy_nlp.vocab)
    # Create the spacy Doc Object that contains the metadata for entities
    spacy_doc = spacy_nlp(text_tokens)  # type: Doc
    # generate the final output
    token_labels = list()  # type: List[Union[str, bool]]
    for word in spacy_doc:
        if word.ent_type_:
            # word.ent_type_  # type: str
            token_labels.append(word.ent_type_)
        else:
            token_labels.append(False)
    return token_labels
