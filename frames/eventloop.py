"""eventloop.py defines asynchronous eventloop for dearpygui. The key idea
is that callback functions can be defined with or without the async keyword,
and the callback function will then be called in the appropriate way automatically.

The key benefits of this eventloop is that:
    - logging is built in for the callback functions.
    - callback functions can be defiened with or without the async keyword.
    - makes it very easy create concurrent async functions without blocking the ui.

Author: Kim Timothy Engh
Copyright: GPLv3"""


import asyncio
import dearpygui.dearpygui as dpg
import inspect
import itertools
import logging


logger = logging.getLogger(__name__)


async def eventloop():
    """event loop runs a async eventloop which handles the dearpygui
    sync and async callbacks. Before the eventloop is started manual
    callback management must be enabled during the set-up.

        | async def main():
        |     dpg.create_context()
    --> |     dpg.configure_app(manual_callback_management=True)
        |     dpg.create_viewport()
        |     dpg.setup_dearpygui()
        |
        | asyncio.run(main())

    Since normal dearpygui callbacks are blocking, longer running tasks
    can be created with the async keyword. The eventloop will call them
    passing in the arguments sender, app_data, and user_data as normal,
    given the number of positional arguements the function supports.

        | async def my_async_cb(sender, app_data, user_data):
        |     do_something()
    """

    while dpg.is_dearpygui_running(): 
        dpg.render_dearpygui_frame()

        await call_event_callbacks()
        await asyncio.sleep(0)

    dpg.destroy_context()


async def call_event_callbacks():
    """call_event_callbacks handles the dearpygui callbacks. It
    supports both syncronus and asyncronus functions to be passed
    with up to three positional arguments, sender, app_data and
    user_data - in this specific order, as supported by dearpygui.

    | async def my_async_cb(sender, app_data, user_data):
    |     asyncio.sleep(0)

    | def my_cb(sender, app_data, user_data):
    |     so_something_important()

    The use of fewer arguments are also possible, but the keywords
    are not taken into consideration.

    | async def my_async_cb(sender):
    |     await something_that_takes_time()
    """

    queue = dpg.get_callback_queue()

    if queue is None:
        return

    for callback_and_arguments in queue:       
        callback = callback_and_arguments[0]

        if callback is None:
            return
        
        arguments = callback_and_arguments[1:]
        parameters = inspect.signature(callback).parameters
        is_coroutine_fuction = asyncio.iscoroutinefunction(callback)
        
        args_to_be_passed = [
            argument for argument, parameter
            in itertools.zip_longest(arguments, parameters)
            if parameter is not None
        ]
       
        if is_coroutine_fuction:
            logger.info(f'async callback({callback}, {args_to_be_passed})')
            coroutine = callback(*args_to_be_passed)
            task = asyncio.create_task(coroutine)
        
        else:
            logger.info(f'sync callback({callback}, {args_to_be_passed})')
            callback(*args_to_be_passed)
        
        await asyncio.sleep(0)

