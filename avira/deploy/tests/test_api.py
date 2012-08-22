from unittest import TestCase
import avira.deploy.api
import sys
from StringIO import StringIO


class CmdApiTester(avira.deploy.api.CmdApi):
    """
    Helper class to test the CmdApi class.
    """
    def do_test_no_args(self):
        """This should show a helpmessage"""
        print "Method called with no params"

    def do_test_args(self,
                     param="defaultvalue",
                     anotherparam="defaultvalue"):
        """This message should be shown if arguments are not ok"""
        print "Method called with %(param)s and %(anotherparam)s" % locals()

    def do_test_args_and_flags(self, param="value", **flags):
        print "Method called with param %(param)s and %(flags)s" % locals()

    def do_exit(self):
        return True


def print_exc_return_nothing():
    return ""


class CmdApiTest(TestCase):

    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out
        self.cmd = CmdApiTester()
        self.cmd.use_rawinput = 0

    def tearDown(self):
        sys.stdout = self.saved_stdout
        self.out = None

    def test_no_args(self):
        self.cmd.cmdqueue = ["test_no_args", "exit"]
        self.cmd.cmdloop()
        output = self.out.getvalue()
        self.assertEqual(output, "Method called with no params\n")

    def test_args(self):
        self.cmd.cmdqueue = ["test_args", "exit"]
        self.cmd.cmdloop()
        output = self.out.getvalue()
        self.assertEqual(output,
                         "Method called with defaultvalue and defaultvalue\n")

    def test_args_params(self):
        cmd = self.cmd
        cmd.cmdqueue = ["test_args param=myvalue anotherparam=anothervalue",
                        "exit"]
        cmd.cmdloop()
        output = self.out.getvalue()
        self.assertEqual(output,
                         "Method called with myvalue and anothervalue\n")

    def test_args_params_incorrect(self):
        self.cmd.cmdqueue = ["test_args thisparam=notcorrect", "exit"]
        self.cmd.cmdloop()
        output = self.out.getvalue()
        self.assertEqual(output,
                    "This message should be shown if arguments are not ok\n")

    def test_args_params_incorrect_with_debug(self):
        avira.deploy.api.traceback.print_exc = print_exc_return_nothing
        self.cmd.debug = True
        self.cmd.cmdqueue = ["test_args thisparam=notcorrect", "exit"]
        self.cmd.cmdloop()
        output = self.out.getvalue()
        self.assertTrue("should be shown if arguments are not ok" in output)
        self.assertTrue("do_test_args() got an unexpected keyword" in output)

    def test_args_and_flags(self):
        cmd = self.cmd
        cmd.cmdqueue = ["test_args_and_flags param=myvalue flag=1", "exit"]
        cmd.cmdloop()
        output = self.out.getvalue()
        self.assertEqual(output,
                        "Method called with param myvalue and {'flag': '1'}\n")
