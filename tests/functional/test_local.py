# from typing import Dict
# import os
# from unittest import TestCase, main
#
# import json
#
# from monolithcaching import CacheManager
#
#
# class TestCacheManager(TestCase):
#
#     @staticmethod
#     def get_meta_data(meta_data_path: str) -> Dict:
#         with open(meta_data_path) as json_file:
#             meta = json.load(json_file)
#         return meta
#
#     def test_cache(self):
#         test = CacheManager(host="localhost", port=6379)
#         test.create_cache()
#
#         cache_directory_check = test.worker.base_dir
#         meta_file_path = test.worker.base_dir + "meta.json"
#         meta_data = self.get_meta_data(meta_data_path=meta_file_path)
#
#         self.assertEqual(True, os.path.isdir(cache_directory_check))
#         self.assertEqual(test.worker.base_dir, test.worker.base_dir)
#         self.assertEqual(None, test.worker._existing_cache)
#         self.assertEqual(True, os.path.isfile(meta_file_path))
#         self.assertEqual({}, meta_data)
#         self.assertEqual({}, test.meta)
#
#         test.insert_meta(key="one", value=1)
#         test.insert_meta(key="two", value=2)
#
#         self.assertEqual({"one": 1, "two": 2}, self.get_meta_data(meta_data_path=meta_file_path))
#         self.assertEqual({"one": 1, "two": 2}, test.meta)
#
#         existing_test = CacheManager(host="localhost", port=6379)
#         existing_test.create_cache(existing_cache=test.cache_path)
#
#         existing_test.insert_meta(key="three", value=3)
#         self.assertEqual({"one": 1, "two": 2, "three": 3}, existing_test.meta)
#         self.assertEqual({"one": 1, "two": 2, "three": 3}, test.meta)
#
#         existing_test.wipe_cache()
#         self.assertEqual({"one": 1, "two": 2, "three": 3}, test.meta)
#         del existing_test
#
#         existing_cach_path = test.cache_path
#
#         del test
#
#         if os.environ.get("CI") is None:
#             self.assertEqual(False, os.path.isdir(existing_cach_path))
#
#     def test_lock(self):
#         test = CacheManager(host="localhost", port=6379)
#         test.create_cache()
#
#         self.assertEqual({}, test.meta)
#         test.lock_cache()
#         self.assertEqual({"locked": True}, test.meta)
#         existing_cach_path = test.cache_path
#
#         del test
#
#         new_test = CacheManager(host="localhost", port=6379)
#         new_test.create_cache(existing_cache=existing_cach_path)
#         self.assertEqual({"locked": True}, new_test.meta)
#         self.assertEqual(True, new_test.worker._locked)
#         self.assertEqual(True, os.path.isdir(existing_cach_path))
#         new_test.unlock_cache()
#         self.assertEqual({"locked": False}, new_test.meta)
#         self.assertEqual(False, new_test.worker._locked)
#         self.assertEqual(True, os.path.isdir(existing_cach_path))
#
#         del new_test
#
#         if os.environ.get("CI") is None:
#             self.assertEqual(False, os.path.isdir(existing_cach_path))
#
#
# if __name__ == "__main__":
#     main()
