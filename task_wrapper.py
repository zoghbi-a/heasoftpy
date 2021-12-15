#!/usr/bin/env python


import sys
import os
import glob
import importlib
import re

# add heasoftpy location to sys.path as it is not installed yet
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# the following prevents sub-package in heasoftpy.packages from being imported
# as they may depend on the functions in heasoftpy.fcn, that we will install here
os.environ['__INSTALLING_HSP'] = 'yes'
from heasoftpy import utils



# template text for task library #
library_text = """
from heasoftpy.core import HSPTask, HSPResult
from ._{taskname} import run_{taskname}

class HSP{taskname}(HSPTask):
    \"""python-based task\"""
    
    name = '{taskname}'
    
    def exec_task(self):
        
        # put the parameters in to a list of par=value
        params = self.params
        
        # logger
        logger = self.logger
        
        
        ## --------- ##
        ## Task code ##        
        returncode, params, custom = run_{taskname}(params, logger)
        ## --------- ##

        outMsg, errMsg = self.logger.output
        return HSPResult(returncode, outMsg, errMsg, params, custom)
    
    
    def task_docs(self):
        return {taskname}.__doc__

def {taskname}(args=None, **kwargs):
    \"""
    {task_help}
    \"""
    task = HSP{taskname}()
    result = task(args, **kwargs)
    return result
    
"""

# template text for task executable #
executable_text = """#!/usr/bin/env python

import sys
import heasoftpy as hsp


if __name__ == '__main__':
    
    task = hsp.HSP{taskname}()
    cmd_args = hsp.utils.process_cmdLine(task)
    result = task(**cmd_args)
    sys.exit(result.returncode)

"""


init_text = """

from .{taskname}_lib import HSP{taskname}, {taskname}
__all__ = ['HSP{taskname}', '{taskname}']

"""


def generate_task_wrapper(taskname, task_help=''):
    """Generate task wrappers for python tasks"""
    
    task_defs = {
        'taskname': taskname,
        'task_help': task_help,
    }
    
    # generate library code
    with open(f'{taskname}_lib.py', 'w') as fp:
        fp.write(library_text.format(**task_defs))
       
    # generate executable code
    with open(f'{taskname}.py', 'w') as fp:
        fp.write(executable_text.format(**task_defs))
        

if __name__ == '__main__':
    
    # generate wrappers for all files in current folder #
    par_files = glob.glob('*.par')
    print(f'Found {len(par_files)} par files')
    
    tasks = []
    for par_file in par_files:
        taskname = par_file.replace('.par', '')
        
        #- do we have a _{taskname}.py file? -#
        lib_file = f'_{taskname}.py'
        if os.path.exists(lib_file):
            # does it define: run_{taskname}?
            has_method = False
            with open(lib_file, 'r') as fp:
                for line in fp:
                    if re.search(f'def run_{taskname}', line):
                        has_method = True
                        break
            if not has_method:
                raise ValueError(f'{lib_file} does not seem to define method run_{taskname}')
        else:
            raise ValueError(f'There is no {lib_file}')
        #-------------------------------------#
        
        #- do we have a help file -#
        help_file = f'_{taskname}.hlp'
        if os.path.exists(help_file):
            task_help = '    '.join(open(help_file))
        else:
            task_help = ''
        #--------------------------#
        
        # ready to generate the class code #
        generate_task_wrapper(taskname, task_help)
        tasks.append(taskname)
    
    # generate __init__ file
    parent_dir = os.path.normpath(os.getcwd()).split(os.sep)[-2]
    init_text  = '\n'.join([f'from .{task}_lib import HSP{task}, {task}' for task in tasks])
    init_text += '\n__all__ = [\n{}\n]'.format('\n'.join([f"'HSP{task}', '{task}'" for task in tasks]))
    if parent_dir == 'packages':
        with open('__init__.py', 'w') as fp: fp.write(init_text)
    else:
        print('please add the following to your packages/task_package/__init__.py:')
        print(init_text)
        
    
        