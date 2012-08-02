import cmd
import traceback


def parse_line(line):
    segments = line.split()
    args = []
    kwargs = {}
    for segment in segments:
        if "=" in segment:
            key, value = segment.split("=")
            kwargs[key.strip()] = value.strip()
        else:
            args.append(segment)
    
    return args, kwargs

class CmdApi(cmd.Cmd):
    """
    Alows you to implement a real api with args and kwargs using the
    cmd library.
    
    so instead of::
    
        def do_foo(self, line):
            args = line.split()
            # do something

    Now you can do::
    
        def do_foo(self, bar, baz, **flags):
            do something with all dem variables.
    
    used like::
        
        > foo "hi this will become bar" baz="yeah that works also" someflag=no otherflag=right
    
    If not all requires variables are filled in, the help of the action is shown.
    """
    def onecmd(self, s):
        # do standard parsing of line
        name, line, all = self.parseline(s)
        
        # look up the method
        method = getattr(self, "do_%s" %name, None)
        
        # if a proper method was found, try and call it.
        if method is not None and callable(method):
            # parse arguments and keyword arguments from line
            args, kwargs = parse_line(line)
            try:
                # try to call the method
                return method(*args, **kwargs)
            except TypeError as e:
                # if something went wrong, print the help for that method
                if self.debug:
                    traceback.print_exc()
                    print "%s: %s" % (type(e), e)
                if name != 'help':
                    return self.do_help(name)

                return self.do_help(None)
        
        # if no proper method with the name was found, do what cmd always does
        return cmd.Cmd.onecmd(self, s)
                
