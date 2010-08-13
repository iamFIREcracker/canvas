#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module containing a class which simplify the creation of widgets used for
drawing purposes.
"""

from __future__ import division

import cairo
import gobject
import gtk


class Canvas(object):
    """Window containing a drawing area for drawings.
    """

    def __init__(self, do_delete=None, do_configure=None, do_draw=None):
        """Constructor.

        Initialize the window and pack a drawing area.

        Keywords:
            do_configure: user callback for the configure event.
            do_draw: user callback for drawing operations.
        """
        super(Canvas, self).__init__()

        window = gtk.Window()
        self.darea = gtk.DrawingArea()
        self.surface = self.context = None
        if do_delete is not None:
            self.do_delete = do_delete
        if do_configure is not None:
            self.do_configure = do_configure
        if do_draw is not None:
            self.do_draw = do_draw

        window.connect('delete-event', self.delete_cb)
        self.darea.connect('configure-event', self.configure_cb)
        self.darea.connect('expose-event', self.expose_cb)
        
        window.add(self.darea)
        window.show_all()

    def delete_cb(self, window, event):
        """Call the user defined callback if present.
        """
        try:
            self.do_delete(self, window, event)
        except AttributeError:
            pass

    def configure_cb(self, darea, event):
        """Create a private surface and its cairo context.

        Is it possible to extend the class and define a do_configure method
        invoked before the end of this.
        """
        width, height = darea.window.get_size()

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          width,
                                          height)
        self.context = cairo.Context(self.surface)

        try:
            self.do_configure(self, darea, event)
        except AttributeError:
            pass

        return True

    def expose_cb(self, darea, event):
        """Redraw either the whole window or a part of it.
        """
        context = darea.window.cairo_create()
        
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
        context.set_source_surface(self.surface, 0, 0)
        context.paint()

        return False

    def refresh(self):
        """Redraw on the private context and force a refresh of the window.
        """
        try:
            self.do_draw(self)
            self.darea.queue_draw()
        except AttributeError:
            pass

        return True


def main():
    """Enter the mainloop.

    Wrapper of gtk module.
    """
    gtk.main()

def main_quit():
    """Quit the mainloop.

    Wrapper of gtk module.
    """
    gtk.main_quit()

def timeout_add(time, func, *args, **kwargs):
    """Schedule a timeout callback.

    Wrapper of the gobject module.
    """
    gobject.timeout_add(time, func, *args, **kwargs)


if __name__ == '__main__':
    def delete(canvas, window, event):
        """Quit the gtk mainloop.
        """
        print '::delete'
        main_quit()

    def configure(canvas, darea, event):
        """Normalize the canvas surface in order to place (0, 0) in the center,
        and to bound both the axis between -1 and +1.
        """
        global ratio

        print '::configure'

        width, height = darea.window.get_size()
        ratio = width / height
        context = canvas.context

        context.scale(width * 0.5 / ratio, height / 2)
        context.translate(ratio, 1)

    def draw(canvas):
        """Draw a green square on black background.
        """
        global ratio

        print '::draw'

        context = canvas.context

        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_source_rgb(0, 0, 0)
        context.rectangle(-ratio, -1, 2 * ratio, 2)
        context.fill()
        context.set_source_rgb(0, 1, 0)
        context.rectangle(-0.5, -0.5, 1, 1)
        context.fill()

    ratio = 0
    canvas = Canvas(do_delete=delete, do_configure=configure, do_draw=draw)

    timeout_add(66, canvas.refresh)

    main()
