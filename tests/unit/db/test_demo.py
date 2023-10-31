"""
Tests for managing the demo data.
"""

import os
from sqlalchemy import text
import pytest
from lute.db import db
from lute.db.demo import contains_demo_data, remove_flag, \
    delete_demo_data, tutorial_book_id, \
    demo_data_path, load_demo_data, \
    predefined_languages, get_demo_language
from tests.dbasserts import assert_record_count_equals


def test_new_db_is_demo(app_context):
    "New db created from the baseline has the demo flag set."
    assert contains_demo_data() is True, 'new db contains demo.'


def test_removing_flag_means_not_demo(app_context):
    "Unsetting the flag means the db is not a demo."
    remove_flag()
    assert contains_demo_data() is False, 'not a demo.'


def test_wiping_db_clears_flag(app_context):
    "No longer a demo if the demo is wiped out!"
    delete_demo_data()
    assert contains_demo_data() is False, 'not a demo.'


def test_wipe_db_only_works_if_flag_is_set(app_context):
    "Can only wipe a demo db!"
    remove_flag()
    with pytest.raises(Exception):
        delete_demo_data()


def test_tutorial_id_returned_if_present(app_context):
    "Sanity check."
    assert tutorial_book_id() > 0, 'have tutorial'

    sql = 'update books set bktitle = "xxTutorial" where bktitle = "Tutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id() is None, 'no tutorial'

    sql = 'update books set bktitle = "Tutorial" where bktitle = "xxTutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id() > 0, 'have tutorial again'

    delete_demo_data()
    assert tutorial_book_id() is None, 'no tutorial'


# Getting languages from yaml files.

def test_new_english_from_yaml_file():
    """
    Smoke test, can load a new language from yaml definition.
    """
    f = os.path.join(demo_data_path(), 'languages', 'english.yaml')
    lang = get_demo_language(f)

    # Replace the following assertions with your specific expectations
    assert lang.name == "English"
    assert lang.dict_1_uri == "https://en.thefreedictionary.com/###"
    assert lang.sentence_translate_uri == "*https://www.deepl.com/translator#en/en/###"
    assert lang.show_romanization is False, 'uses default'
    assert lang.right_to_left is False, 'uses default'


def test_get_predefined():
    """
    Returns all the languages using the files in the demo folder.
    """
    langs = predefined_languages()
    langnames = [lang.name for lang in langs]
    for expected in [ 'English', 'French', 'Turkish' ]:
        assert expected in langnames, expected


# Loading.

def test_load_demo_loads_language_yaml_files(app_context):
    "All data is loaded, spot check some."
    delete_demo_data()
    assert contains_demo_data() is False, 'not a demo.'
    assert_record_count_equals('languages', 0, 'wiped out')

    load_demo_data()
    assert contains_demo_data() is True, 'demo loaded'
    checks = [
        "select * from languages where LgName = 'English'",
        "select * from books where BkTitle = 'Tutorial'"
    ]
    for c in checks:
        assert_record_count_equals(c, 1, 'got data')


# unsupported
