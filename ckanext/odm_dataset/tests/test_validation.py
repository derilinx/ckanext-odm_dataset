import os
import json
from nose.tools import assert_equal, assert_in

class TestValidation:

  dirs = [
  ];

  json_files = [
    os.path.abspath(os.path.join(__file__, '../../','odm_presets.json')),
    os.path.abspath(os.path.join(__file__, '../../','odm_dataset_schema.json'))
  ];

  def test_01_data_available(self):

    for directory in self.dirs:
      assert os.path.isdir(directory)

    for json_file in self.json_files:
      print(json_file)
      assert os.path.isfile(json_file)

  def test_02_correct_json_files(self):

    all_valid = True
    for json_file in self.json_files:
      with open(json_file) as f:
        try:
          return json.loads(f.read())
        except ValueError as e:
          all_valid = False
          print('invalid json: %s' % e)

      assert all_valid
