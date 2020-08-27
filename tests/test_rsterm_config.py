import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch
from rsterm.configs import RsTermConfig
from tests import FIXTURES_PATH

EXPECTED_COMPLETE_ENV_VARS = {
    'SPAM_DB_URL': 'beans-eggs-banana',
    'SPAM_ROLE': 'the-lead-role',
    'SPAM_ACCESS_KEY': 'my-secret-key',
    'SPAM_SECRET_KEY': 'my-access-key',
    'SPAM_BUCKET': 'bucket-o-spam'
}

EXPECTED_DB_DICT = {
    'redshift': 'SPAM_DB_URL',
    'blueshift': 'this-value-is-direct-reference'
}

EXPECTED_ENVIRONMENT_DICT = {
    'load_env': True,
    'app_env': './tests/fixtures/spam.env'
}

EXPECTED_NOUN_VERB_MAP = [
    'new_eggs', 'new_beans', 'new_spam',
    'run_eggs', 'run_beans', 'run_spam',
    'delete_eggs', 'delete_beans', 'delete_spam'
]

EXPECTED_NOUNS = [
    'spam', 'eggs', 'beans'
]

EXPECTED_VERBS = [
    'new', 'run', 'delete'
]

EXPECTED_BUCKETS = {
    'redshift': 'SPAM_BUCKET',
    'blueshift': 'this-value-is-direct-reference'
}


class TestCompleteRsTermConfig(TestCase):

    def setUp(self) -> None:
        spam_path = FIXTURES_PATH / "spam.yml"
        self.rsterm = RsTermConfig.parse_config(spam_path)
        RsTermConfig.load_rsterm_env(self.rsterm)

    def test_rsterm_type(self):
        self.assertTrue(isinstance(self.rsterm, RsTermConfig))

    def test_env_vars_set(self):
        for key, value in EXPECTED_COMPLETE_ENV_VARS.items():
            self.assertEqual(os.environ[key], value)

    @patch('rsterm.configs.rsterm_config.psycopg2.connect')
    def test_psycopg2_connect(self, patched_connect):
        patched_connect.return_value = MagicMock()
        _ = self.rsterm.get_db_connection('redshift')
        patched_connect.assert_called_with('beans-eggs-banana')

    @patch('rsterm.configs.rsterm_config.psycopg2.connect')
    def test_psycopg2_direct_connect(self, patched_connect):
        patched_connect.return_value = MagicMock()
        _ = self.rsterm.get_db_connection('blueshift')
        patched_connect.assert_called_with('this-value-is-direct-reference')

    def test_get_db_connection_raises_key_error(self):
        self.assertRaises(KeyError, self.rsterm.get_db_connection, 'blackshift')

    def test_db_dict_values(self):
        self.assertEqual(self.rsterm.db_connections, EXPECTED_DB_DICT)

    def test_env_dict_values(self):
        self.assertEqual(self.rsterm.environment, EXPECTED_ENVIRONMENT_DICT)

    def test_noun_verb_map(self):
        verb_noun_map = self.rsterm.verb_noun_map
        verb_noun_map.sort()
        EXPECTED_NOUN_VERB_MAP.sort()
        self.assertEqual(verb_noun_map, EXPECTED_NOUN_VERB_MAP)

    def test_noun_list(self):
        self.rsterm.nouns.sort()
        EXPECTED_NOUNS.sort()
        self.assertEqual(self.rsterm.nouns, EXPECTED_NOUNS)

    def test_verb_list(self):
        self.rsterm.verbs.sort()
        EXPECTED_VERBS.sort()
        self.assertEqual(self.rsterm.verbs, EXPECTED_VERBS)

    def test_bucket_values(self):
        self.assertEqual(self.rsterm.s3_buckets, EXPECTED_BUCKETS)

    def test_get_bucket(self):
        bucket = self.rsterm.get_s3_bucket('redshift')
        self.assertEqual(bucket, 'bucket-o-spam')

    def test_get_direct_bucket(self):
        bucket = self.rsterm.get_s3_bucket('blueshift')
        self.assertEqual(bucket, 'this-value-is-direct-reference')

    def test_get_bucket_raises_key_error(self):
        self.assertRaises(KeyError, self.rsterm.get_s3_bucket, 'buckfoo')

    def test_load_env(self):
        self.assertTrue(self.rsterm.load_env)

    def test_load_env_path(self):
        expected_path = FIXTURES_PATH / "spam.env"
        set_path = Path(self.rsterm.env_file_name).absolute()
        self.assertEqual(set_path.as_posix(), expected_path.as_posix())
