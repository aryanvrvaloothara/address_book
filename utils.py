import logging

logging.basicConfig(filename='log/error.log', filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

NEWLINE = "\n"


def get_new_line(value: str = '', repeat: int = 100):
    if str == '':
        repeat = 1
    return (value * repeat) + NEWLINE


def log_exception(e: Exception):
    import traceback
    stack_traces = traceback.format_stack()
    print(e)
    stack_traces = get_new_line() + str(e)
    try:
        for num in range(len(stack_traces), -1, -1):
            try:
                stack_traces += get_new_line() + stack_traces[num] + get_new_line()
            except:
                pass
    except:
        pass
    stack_traces += get_new_line('-') + get_new_line()
    logger.info(
        ''.join(traceback.format_exception(etype=type(e), value=e, tb=None)) +
        stack_traces
    )
