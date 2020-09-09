# from unittest import TestCase, main
#
# from caching import CacheManager
#
#
# class TestCacheManager(TestCase):
#
#     def test_meta(self):
#         test = CacheManager(host="localhost", port=6379, s3=True, s3_cache_path="s3://dpu-testing-bucket/cache/")
#         test.create_cache()
#         test.insert_meta(key="test", value="another test")
#         self.assertEqual(True, test.worker.check_file(file="meta.json"))
#
#         self.assertEqual({"test": "another test"}, test.meta)
#         test.worker.delete_directory()
#
#         directory = test.cache_path
#
#         new_test = CacheManager(host="localhost", port=6379, s3=True, s3_cache_path="s3://dpu-testing-bucket/cache/")
#         new_test.create_cache(existing_cache=directory)
#
#         self.assertEqual(False, test.worker.check_file(file="meta.json"))
#
#
# if __name__ == "__main__":
#     main()
