from unittest import TestCase
from rsterm import AWSSecrets, VerbNounMap


class TestAWSSecrets(TestCase):

    def test_aws_attributes(self) -> None:
        aws_secrets = AWSSecrets(key='foo', secret='bar')
        self.assertEqual(aws_secrets.key, 'foo')
        self.assertEqual(aws_secrets.secret, 'bar')
        self.assertIsNotNone(getattr(aws_secrets, 'key'))
        self.assertIsNotNone(getattr(aws_secrets, 'secret'))


class TestVerbNounMap(TestCase):

    def setUp(self) -> None:
        self.verbs = ['new', 'delete']
        self.nouns = ['test', 'config']
        self.verb_noun_map = VerbNounMap(verbs=self.verbs, nouns=self.nouns)

    def test_verb_noun_combinations(self) -> None:
        expected_combinations = ['new_test', 'new_config', 'delete_test', 'delete_config']
        expected_combinations.sort()

        verb_noun_map = self.verb_noun_map.verb_noun_map
        verb_noun_map.sort()

        self.assertEqual(expected_combinations, verb_noun_map)

    def test_verb_noun_map_is_list(self) -> None:
        self.assertIsInstance(self.verb_noun_map.verb_noun_map, list)

    def test_verb_noun_formatted_args(self) -> None:
        expected_format = {

            ('verb',): {
                'help': 'The action you would like to perform',
                'choices': self.verbs
            },

            ('noun',): {
                'help': 'The element to act upon',
                'choices': self.nouns
            }
        }

        self.assertEqual(expected_format, self.verb_noun_map.formatted_actions)

    def test_noun_list(self) -> None:
        self.assertEqual(self.nouns, self.verb_noun_map.nouns)

    def test_verb_list(self) -> None:
        self.assertEqual(self.verbs, self.verb_noun_map.verbs)
