
# the main task method
def run_sample(params, logger):
    """Run a task sample"""
    
    logger.info(f"Resetting the foo parameter from {params['foo']} to {params['bar']}.")

    params['foo'] = f"{params['bar']}" #  stringify the int
    logger.info(f"Now foo = {params['foo']}.")

    params['bar'] = _some_additional_function(params['bar'])
    logger.info(f"and bar = {params['bar']}.")

    logger.error('testing error logging')
    
    returncode = 0
    custom = {}
    return returncode, params, custom


# additional helper methods
def _some_additional_function(inval):
    return inval+1
