import unittest,app
class GraphTests(unittest.TestCase):
 def test_missing(self):
  r=app.build_graph([{"name":"alpha","requires":["beta>=1","gamma"]}])
  self.assertIn("alpha",r["missing"])
  self.assertIn("alpha",r["graph"])
 def test_tree(self):
  r=app.build_graph([{"name":"alpha","requires":["beta"]},{"name":"beta","requires":[]}])
  self.assertIn("beta",app.tree(r,"alpha"))
if __name__=="__main__":unittest.main()
