"""extras.py in the frames package contains extra functions to
act as examples, or to provide basic functionality that might or
might not be apprectatied by the user. This file does not add any
additional dependecies.

Author: Kim Timothy Engh
Copyright 2024, GPLv3

Respect free software as intended."""

import asyncio
import time
import dearpygui.dearpygui as dpg
from . import eventloop


def process_manager():
    """process_manager is a dearpygui window that shows running
    asyncio tasks, and makes it possible to cancel them"""
    
    interval = 3
    
    with dpg.window(label='Process Manager') as dpg_window:
        dpg_iter = dpg.add_text(0)
        
        with dpg.table() as dpg_table:
            dpg.add_table_column(label='Task')
            dpg.add_table_column(label='Action')

    async def update():
        while True:
            try:
                for row in dpg.get_item_children(dpg_table)[1]:
                    dpg.delete_item(row)
                
                pending_tasks = list(asyncio.all_tasks())

                for task in pending_tasks:
                    with dpg.table_row(parent=dpg_table):
                        if not task.done():
                            dpg.add_text(str(task))
                            dpg.add_button(label='Stop', callback=task.cancel)

                await asyncio.sleep(3)
  
            except asyncio.CancelledError:
                dpg.delete_item(dpg_window)
                raise

    return dpg_window


async def example():
    """example is a function that starts a dearpygui window using
    the an async eventloop. It´s ment to be an example for how the
    a dearpygui app should be structured when using this library.


    The following snipped describes how to run it.
    
        | import asyncio
        | import frames
    --> | asyncio.run(frames.extras.example())

    Normally you would create you own function to start off your
    application. A minimal example is:

        | async def main():
        |     dpg.create_context()
        |     dpg.configure_app(manual_callback_management=True)
        |     dpg.create_viewport(title="Example", width=800, height=600)
        |     dpg.setup_dearpygui()
        |
        |     ...
        |
        |     dpg.show_viewport()
        |     await frames.eventloop.eventloop()
        |
        |
        | if __name__ == '__main__':
        |     asyncio.run(main())

    Replace the three dots with you application. The eventloop starts the
    dearpygui drawing, and event handling. Callbacks created for dearpygui
    can now be both sync or async depending on the need.
    """
    
    dpg.create_context()
    dpg.configure_app(manual_callback_management=True)
    dpg.create_viewport(title="Example", width=800, height=600)
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window") as win:
        label = dpg.add_text('Waiting')

        def ss(s):
            dpg.set_value(label, 'Sync...')
            time.sleep(3)
            dpg.set_value(label, 'Done!!!')
            time.sleep(1)
            dpg.set_value(label, 'Waiting...')


        async def sa(s, u, a):
            dpg.set_value(label, 'Async...')
            await asyncio.sleep(3)
            dpg.set_value(label, 'Done!!!')
            await asyncio.sleep(1)
            dpg.set_value(label, 'Watiting...')

        button1 = dpg.add_button(label='Test Sync', callback=ss)
        button2 = dpg.add_button(label='Test Async', callback=sa)

    dpg.set_primary_window(win, True)
    dpg.show_viewport()
    
    await eventloop.eventloop()

